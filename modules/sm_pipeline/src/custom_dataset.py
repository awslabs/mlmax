import pandas as pd
import torch
from torch.utils.data import Dataset


class CustomDataset(Dataset):
    def __init__(self, filename):
        """Custom Dataset."""

        df = pd.read_csv(filename)
        self.X = torch.tensor(df.iloc[:, 1:].values).float()
        self.y = torch.tensor(df.iloc[:, 0:1].values).float()

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

    def __len__(self):
        return len(self.y)


if __name__ == "__main__":
    filename = "/opt/ml/processing/train/train.csv"

    ds = CustomDataset(filename)
    train, label = ds[0]
    print("Done")
