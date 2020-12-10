import pytest
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


# @dt.working_directory(__file__)
# def test_train_preprocessing(input_data_path, args_train):
#     """
#     Test the data preprocessing in the training.
#     """
#     train_features, test_features = main(args_train)

#     # check number of features
#     assert train_features.shape[1] == test_features.shape[1]


# @dt.working_directory(__file__)
# def test_infer_preprocessing(input_data_path, args_infer):
#     """
#     Test the data preprocessing in the inference.
#     """
#     test_featues = main(args_infer)

#     # To do: add assertion


# @dt.working_directory(__file__)
# def test_parse_arg():
#     args = parse_arg()
#     assert args.mode == "infer"
#     assert args.train_test_split_ratio == 0.3
#     assert args.data_dir == "opt/ml/processing"
#     assert args.data_input == "input/census-income.csv"


# # To do: need to clean the folders created
