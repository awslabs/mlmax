import os
import pytest
import argparse
import pandas as pd
import datatest as dt

from mlmax.train import (
    read_xy,
    read_processed_data,
    train,
    evaluate,
    save_model,
    parse_arg,
    main,
)


@pytest.fixture()
@dt.working_directory(__file__)
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default="opt/ml/processing/train")
    parser.add_argument("--test", type=str, default="opt/ml/processing/test")
    parser.add_argument("--model-dir", type=str, default="opt/ml/model")
    args, _ = parser.parse_known_args()
    os.makedirs(args.model_dir, exist_ok=True)
    print(f"Received arguments {args}")
    return args


@dt.working_directory(__file__)
def test_read_xy(test_train_data_path):
    """
    test the read_xy function.
    """

    req_col_num = 71
    required_labels = {0, 1}
    train_path, test_path = test_train_data_path
    X_train, y_train = read_xy(train_path)
    X_test, y_test = read_xy(test_path, "test")

    # check number of rows
    assert X_train.shape[0] == y_train.shape[0]
    assert X_test.shape[0] == y_test.shape[0]

    # check number of columns
    assert X_train.shape[1] == req_col_num
    assert X_test.shape[1] == req_col_num

    # check the label values
    dt.validate(y_train.iloc[:, 0], required_labels)
    dt.validate(y_test.iloc[:, 0], required_labels)


@dt.working_directory(__file__)
def test_read_processed_data(args):
    """
    Test the data preprocessing in the training.
    """
    X_train, y_train, X_test, y_test = read_processed_data(args)

    # check number of features
    assert X_train.shape[1] == X_test.shape[1]


@dt.working_directory(__file__)
def test_train(args):
    X_train, y_train, X_test, y_test = read_processed_data(args)
    model = train(X_train, y_train, args)
    predictions = model.predict(X_test)
    save_model(model, args)
    # todo: add an assert statement


@dt.working_directory(__file__)
def test_evaluate(load_joblib_model, args):
    X_train, y_train, X_test, y_test = read_processed_data(args)
    report_dict = evaluate(load_joblib_model, X_test, y_test, args)
    assert "accuracy" in report_dict.keys()
    assert "macro avg" in report_dict.keys()
    assert "f1-score" in report_dict["macro avg"].keys()
    assert isinstance(report_dict["accuracy"], float)
    assert isinstance(report_dict["macro avg"]["f1-score"], float)


@dt.working_directory(__file__)
def test_save_model(load_joblib_model, args):
    save_model(load_joblib_model, args)


@dt.working_directory(__file__)
def test_main(args):
    main(args)


@dt.working_directory(__file__)
def test_parse_arg():
    args = parse_arg()
    assert args.train == "/opt/ml/input/data/train"
    assert args.test == "/opt/ml/input/data/test"
    assert args.model_dir == "/opt/ml/model"


# # To do: need to clean the folders created
