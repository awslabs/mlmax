import pytest
import pandas as pd
import datatest as dt

from mlmax.preprocessing import (
    read_data,
    transform,
    write_data,
    split_data,
    fit,
    parse_arg,
    main
)


@dt.working_directory(__file__)
def test_read_data(input_data_path):
    """
    test the read_data function.
    """

    required_names = [
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
    required_labels = {
        0, 1
    }
    df = read_data(input_data_path)
    # check the columns
    dt.validate(df.columns, required_names)
    # check the label values
    dt.validate(df["income"].values, required_labels)


@dt.working_directory(__file__)
def test_train_preprocessing(input_data_path, args_train):
    """
    Test the data preprocessing in the training.
    """
    train_features, test_features = main(args_train)

    # check number of features
    assert train_features.shape[1] == test_features.shape[1]


@dt.working_directory(__file__)
def test_infer_preprocessing(input_data_path, args_infer):
    """
    Test the data preprocessing in the inference.
    """
    test_featues = main(args_infer)

    # To do: add assertion


@dt.working_directory(__file__)
def test_parse_arg():
    args = parse_arg()
    assert args.mode == "infer"
    assert args.train_test_split_ratio == 0.3
    assert args.data_dir == "opt/ml/processing"
    assert args.data_input == "input/census-income.csv"

# To do: need to clean the folders created
