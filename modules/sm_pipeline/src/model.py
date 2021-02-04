from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

from custom_dataset import CustomDataset


class Net(nn.Module):
    def __init__(self, input_size=7, output_size=1):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


if __name__ == "__main__":
    filename = "/opt/ml/processing/train/train.csv"

    model = Net()
    ds = CustomDataset(filename)
    train, label = ds[0]
    print(f"train: {train.shape}")
    pred = model(train)
    print(f"Pred: {pred.shape}")
    print("Done")
