"""Feature engineers the abalone dataset.

Prerequisite:
Execute setup/setup.sh, which create base_dir = "/opt/ml/processing", on local workstation.

Sample data from public S3:
s3://sparkml-mleap/data/abalone/abalone.csv

Input dataset:
    Original data is on S3. The intention is download and store processed data in a new directory
    Download from s3 to "{base_dir}/data/abalone-dataset.csv"

    alternatively:
    inputs=[
        ProcessingInput(source="s3://your-bucket/abalone-dataset.csv", destination="/opt/ml/processing/data"),
    ],

Output dataset will be saved to:
    base_dir = "/opt/ml/processing"
    "{base_dir}/train/train.csv"
    "{base_dir}/validation/validation.csv"
    "{base_dir}/test/test.csv"

"""
import argparse
import logging
import os
import pathlib

import boto3
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Since we get a headerless CSV file we specify the column names here.
feature_columns_names = [
    "sex",
    "length",
    "diameter",
    "height",
    "whole_weight",
    "shucked_weight",
    "viscera_weight",
    "shell_weight",
]
label_column = "rings"

feature_columns_dtype = {
    "sex": str,
    "length": np.float64,
    "diameter": np.float64,
    "height": np.float64,
    "whole_weight": np.float64,
    "shucked_weight": np.float64,
    "viscera_weight": np.float64,
    "shell_weight": np.float64,
}
label_column_dtype = {"rings": np.float64}


def merge_two_dicts(x, y):
    """Merges two dicts, returning a new copy."""
    z = x.copy()
    z.update(y)
    return z


if __name__ == "__main__":
    # TODO configure to support both local/s3 dataset?

    logger.debug("Starting preprocessing.")
    parser = argparse.ArgumentParser()
    # TODO get from input config
    parser.add_argument(
        "--input-data",
        type=str,
        default="s3://sparkml-mleap/data/abalone/abalone.csv",
    )
    args = parser.parse_args()

    base_dir = "/opt/ml/processing"
    pathlib.Path(f"{base_dir}/data").mkdir(parents=True, exist_ok=True)
    input_data = args.input_data
    bucket = input_data.split("/")[2]
    key = "/".join(input_data.split("/")[3:])

    logger.info("Downloading data from bucket: %s, key: %s", bucket, key)
    fn = f"{base_dir}/data/abalone-dataset.csv"
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).download_file(key, fn)

    logger.debug("Reading downloaded data.")
    df = pd.read_csv(
        fn,
        header=None,
        names=feature_columns_names + [label_column],
        dtype=merge_two_dicts(feature_columns_dtype, label_column_dtype),
    )
    # Delete file
    # os.unlink(fn)
    logger.debug("Defining transformers.")
    numeric_features = list(feature_columns_names)
    numeric_features.remove("sex")
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_features = ["sex"]

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
        ]
    )
    df = df[numeric_features + [label_column]]

    logger.info("Applying transforms.")

    print("Keep numerical data only")
    print("Data shape:", df.shape)
    y = df.pop("rings")
    X_pre = preprocess.fit_transform(df)
    # Label is number of rings (1-29)
    y_pre = y.to_numpy().reshape(len(y), 1)
    assert X_pre.shape[1] == 7
    X = np.concatenate((y_pre, X_pre), axis=1)

    logger.info("Splitting %d rows of data into train, validation, test datasets.", len(X))
    np.random.shuffle(X)
    # Split into (70%, 15%, 15%)
    train, validation, test = np.split(X, [int(0.7 * len(X)), int(0.85 * len(X))])
    logger.info(f"Train: {train.shape}")
    logger.info(f"Valid: {validation.shape}")
    logger.info(f"Test: {test.shape}")

    logger.info("Writing out datasets to %s.", base_dir)
    # This is required for running local to create dir, else will be created by ProcessingStep:output
    pathlib.Path(f"{base_dir}/train").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"{base_dir}/validation").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"{base_dir}/test").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(train).to_csv(f"{base_dir}/train/train.csv", header=False, index=False)
    pd.DataFrame(validation).to_csv(f"{base_dir}/validation/validation.csv", header=False, index=False)
    pd.DataFrame(test).to_csv(f"{base_dir}/test/test.csv", header=False, index=False)
