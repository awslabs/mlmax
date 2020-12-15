import argparse
import os
import pytest
import pandas as pd
import datatest as dt
import shutil

try:
    from sklearn.externals import joblib
except:
    import joblib

# Define a few fixtures
@pytest.fixture(scope="module")
@dt.working_directory(__file__)
def input_data_path():
    input_data_path = "opt/ml/processing/input/census-income-sample.csv"
    return input_data_path


@pytest.fixture(scope="module")
@dt.working_directory(__file__)
def args_train():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="train")
    parser.add_argument("--train-test-split-ratio", type=float, default=0.3)
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    parser.add_argument(
        "--data-input", type=str, default="input/census-income-sample.csv"
    )
    args, _ = parser.parse_known_args()
    os.makedirs(os.path.join(args.data_dir, "model"), exist_ok=True)
    os.makedirs(os.path.join(args.data_dir, "train"), exist_ok=True)
    return args


@pytest.fixture(scope="module")
@dt.working_directory(__file__)
def args_infer():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="infer")
    parser.add_argument("--train-test-split-ratio", type=float, default=0.3)
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    parser.add_argument(
        "--data-input", type=str, default="input/census-income-sample.csv"
    )
    args, _ = parser.parse_known_args()
    os.makedirs(os.path.join(args.data_dir, "test"), exist_ok=True)
    return args


@pytest.fixture(scope="module")
@dt.working_directory(__file__)
def test_train_data_path():
    train_data_path = "opt/ml/processing/train"
    test_data_path = "opt/ml/processing/test"
    return train_data_path, test_data_path


@pytest.fixture(scope="module")
@dt.working_directory(__file__)
def load_joblib_model():
    model_path = "opt/ml/model/model.joblib"
    model = joblib.load(model_path)
    return model
