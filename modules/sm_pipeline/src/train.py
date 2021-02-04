"""
Pytorch training template

- This script will detect whether it is run on local or on sagemaker.
- Model will be saved on current directory (local run), or in SM_MODEL_DIR for sagemaker run.

"""
import argparse
import os
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

from custom_dataset import CustomDataset
from model import Net


def print_files_in_path(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    for f in files:
        print(f)


def train(model, epoch, train_loader, device, optimizer, log_interval):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        data, target = data.to(device), target.to(device)
        output = model(data)
        loss = F.mse_loss(output, target, reduction="mean")
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print(
                "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss (MSE): {:.2f}".format(
                    epoch, batch_idx * len(data), len(train_loader.dataset), 100.0 * batch_idx / len(train_loader), loss
                )
            )


def test(model, test_loader, device):
    model.eval()
    test_loss = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.mse_loss(output, target, reduction="sum").item()  # sum up batch loss

    mse = test_loss / len(test_loader.dataset)
    rmse = np.sqrt(mse)

    print("Test set: Loss (MSE): {:.2f}, RMSE {:.2f}".format(mse, rmse))
    print("\n")
    return rmse


def model_fn(model_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Net()
    if torch.cuda.device_count() > 1:
        print("Gpu count: {}".format(torch.cuda.device_count()))
        model = nn.DataParallel(model)

    with open(os.path.join(model_dir, "model.pth"), "rb") as f:
        model.load_state_dict(torch.load(f))
    return model.to(device)


def save_model(model, model_dir):
    path = os.path.join(model_dir, "model.pth")
    torch.save(model.state_dict(), path)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=128, help="train batch size")
    parser.add_argument(
        "--test-batch-size",
        type=int,
        default=64,
        help="test batch size",
    )
    parser.add_argument("--epochs", type=int, default=10, help="number of epochs")
    parser.add_argument("--lr", type=float, default=0.01, help="learning rate")
    parser.add_argument("--weight-decay", type=float, default=0.0001, help="Optimizer regularization (l2 penalty)")
    parser.add_argument("--stepsize", type=int, default=10, help="Step LR size")
    parser.add_argument("--gamma", type=float, default=0.1, help="Learning rate step gamma")
    parser.add_argument("--model", type=str, default="m3")
    parser.add_argument("--num-workers", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1, help="seed")
    parser.add_argument("--log-interval", type=int, default=10)

    parser.add_argument("--model-dir", type=str, default=os.getenv("SM_MODEL_DIR", "./"))
    if os.getenv("SM_HOSTS") is not None:
        # parser.add_argument("--current-host", type=str, default=os.environ["SM_CURRENT_HOST"])
        # parser.add_argument("--num-gpus", type=int, default=os.environ["SM_NUM_GPUS"])
        parser.add_argument("--train-dir", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
        parser.add_argument("--valid-dir", type=str, default=os.environ["SM_CHANNEL_VALIDATION"])

    args = parser.parse_args()
    print(args)

    return args


def get_data(filename_train, filename_valid, args):
    """Return dataloader."""
    train_dataset = CustomDataset(filename_train)
    test_dataset = CustomDataset(filename_valid)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.test_batch_size, shuffle=True)
    return train_loader, test_loader


def main():
    args = arg_parser()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)
    kwargs = {"num_workers": args.num_workers, "pin_memory": True} if torch.cuda.is_available() else {}
    print("Additional config:", kwargs)

    # On SageMaker, data is mounted to SM_CHANNEL_TRAINING, update channel to use sample/full dataset
    if os.getenv("SM_HOSTS") is not None:
        print("Running on sagemaker")
        print(f"Data in {args.train_dir} directory:")
        print_files_in_path(args.train_dir)

        # Even though fit is passed "s3://wy-project-template/processed/train/train.csv"
        # Env variable does not return file, it only returns the directory
        filename_train = f"{args.train_dir}/train.csv"
        filename_valid = f"{args.valid_dir}/validation.csv"
    else:
        print("Running on local")
        # Local, use smaller data subset for testing first
        base_dir = "/opt/ml/processing"
        filename_train = f"{base_dir}/train/train.csv"
        filename_valid = f"{base_dir}/validation/validation.csv"

    print("****************************")
    print("filename_train:", filename_train)
    print("filename_valid:", filename_valid)
    print("****************************")

    train_loader, test_loader = get_data(filename_train, filename_valid, args)

    print("Loading model:", args.model)
    model = Net()
    if torch.cuda.device_count() > 1:
        print("There are {} gpus".format(torch.cuda.device_count()))
        model = nn.DataParallel(model)

    model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=args.stepsize, gamma=args.gamma)
    log_interval = args.log_interval

    for epoch in range(1, args.epochs + 1):
        print(f"Learning rate: {scheduler.get_last_lr()[0]:.06f}")
        train(model, epoch, train_loader, device, optimizer, log_interval)
        test(model, test_loader, device)
        # Update schedule for every epoch
        scheduler.step()

    save_model(model, args.model_dir)


if __name__ == "__main__":
    main()
