import argparse
import os
import tarfile
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.exceptions import DataConversionWarning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import KBinsDiscretizer, OneHotEncoder, StandardScaler

warnings.filterwarnings(action="ignore", category=DataConversionWarning)
try:
    from sklearn.externals import joblib
except:
    import joblib

columns = [
    "age",
    "education",
    "major industry code",
    "class of worker",
    "num persons worked for employer",
    "capital gains",
    "capital losses",
    "dividends from stocks",
    "income",
]

target_col = "income"
class_labels = [" - 50000.", " 50000+."]


def read_data(input_data_path):
    print(f"Reading input data from {input_data_path}")
    df = pd.read_csv(input_data_path)
    df = pd.DataFrame(data=df, columns=columns)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.replace(class_labels, list(range(len(class_labels))), inplace=True)
    negative_examples, positive_examples = np.bincount(df[target_col])
    print(
        f"Data after cleaning: {df.shape}, {positive_examples} positive examples, "
        f"{negative_examples} negative examples"
    )
    return df


def transform(df, args, preprocess=None):
    if preprocess is None:
        model_directory = os.path.join(args.data_dir, "model")
        print(f"Reading model from {model_directory}")
        with tarfile.open(
            os.path.join(model_directory, "proc_model.tar.gz"), mode="r:gz"
        ) as archive:
            print(f"Exctracting tarfile to {model_directory}")
            archive.extractall(path=model_directory)
        preprocess = joblib.load(os.path.join(model_directory, "model.joblib"))
    features = preprocess.transform(df)
    print(f"Data shape after preprocessing: {features.shape}")
    return features


def write_data(data, args, file_prefix):
    output_path = os.path.join(args.data_dir, file_prefix)
    print(f"Saving data to {output_path}")
    pd.DataFrame(data).to_csv(output_path, header=False, index=False)


def split_data(df, args):
    split_ratio = args.train_test_split_ratio
    print(f"Splitting data into train and test sets with ratio {split_ratio}")
    return train_test_split(
        df.drop(target_col, axis=1),
        df[target_col],
        test_size=split_ratio,
        random_state=0,
    )


def fit(df, args):
    preprocess = make_column_transformer(
        (
            ["age", "num persons worked for employer"],
            KBinsDiscretizer(encode="onehot-dense", n_bins=10),
        ),
        (
            ["capital gains", "capital losses", "dividends from stocks"],
            StandardScaler(),
        ),
        (
            ["education", "major industry code", "class of worker"],
            OneHotEncoder(sparse=False),
        ),
    )
    print("Creating preprocessing and feature engineering transformations")
    preprocess.fit(df)
    joblib.dump(preprocess, "./model.joblib")
    model_output_directory = os.path.join(args.data_dir, "model/proc_model.tar.gz")
    print(f"Saving model to {model_output_directory}")
    with tarfile.open(model_output_directory, mode="w:gz") as archive:
        archive.add("./model.joblib", recursive=True)
    return preprocess


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="infer")
    parser.add_argument("--train-test-split-ratio", type=float, default=0.3)
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    parser.add_argument("--data-input", type=str, default="input/census-income.csv")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args


def main(args):
    """
    To run locally:

    DATA=s3://sagemaker-sample-data-us-east-1/processing/census/census-income.csv
    aws s3 cp $DATA /tmp/input/
    mkdir /tmp/{train,test,model}
    python preprocessing.py --mode "train" --data-dir /tmp
    """
    input_data_path = os.path.join(args.data_dir, args.data_input)
    df = read_data(input_data_path)

    if args.mode == "infer":
        test_features = transform(df, args)
        write_data(test_features, args, "test/test_features.csv")
        if target_col in df.columns:
            write_data(df[target_col], args, "test/test_labels.csv")
        return test_features
    elif args.mode == "train":
        X_train, X_test, y_train, y_test = split_data(df, args)
        preprocess = fit(X_train, args)
        train_features = transform(X_train, args, preprocess)
        test_features = transform(X_test, args, preprocess)
        write_data(train_features, args, "train/train_features.csv")
        write_data(y_train, args, "train/train_labels.csv")
        write_data(test_features, args, "test/test_features.csv")
        write_data(y_test, args, "test/test_labels.csv")
        return train_features, test_features


if __name__ == "__main__":
    args = parse_arg()
    main(args)
