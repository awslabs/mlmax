import argparse
import pytest
import pandas as pd
import datatest as dt
from sklearn.linear_model import LogisticRegression

from mlmax.inference import (
    load_model,
    load_test_input,
    write_data,
    parse_arg,
    main
)


@pytest.fixture()
@dt.working_directory(__file__)
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir",
                        type=str,
                        default="opt/ml/processing")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args
    return "opt/ml/processing"


@dt.working_directory(__file__)
def test_load_model(args):
    """
    test the load model function.
    """
    model = load_model(args.data_dir)
    assert isinstance(model, LogisticRegression)


@dt.working_directory(__file__)
def test_load_test_input(args):
    """
    test the load test input function.
    """
    X_test = load_test_input(args.data_dir)
    assert isinstance(X_test, pd.DataFrame)


@dt.working_directory(__file__)
def test_main(args):
    main(args)


