import pytest
import pandas as pd
import datatest as dt
import argparse
import os
import tarfile

from mlmax.evaluation import (
    read_features,
    load_model,
    evaluate,
    parse_arg,
    main,
)


@pytest.fixture()
@dt.working_directory(__file__)
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    parser.add_argument("--features-input", type=str, default="test/test_features.csv")
    parser.add_argument("--labels-input", type=str, default="test/test_labels.csv")
    parser.add_argument("--model-input", type=str, default="model/model.tar.gz")
    parser.add_argument("--eval-output", type=str, default="evaluation/evaluation.json")
    args, _ = parser.parse_known_args()
    os.makedirs(os.path.join(args.data_dir, "evaluation"), exist_ok=True)
    print(f"Received arguments {args}")
    return args


@pytest.fixture()
@dt.working_directory(__file__)
def tar_model(args):
    """
    Zip the ML model that was previously saved and tar it. This is something
    that the SageMaker funtion automatically does.
    """
    model_output_directory = os.path.join(args.data_dir, "model/model.tar.gz")
    print(f"TAR_MODEL: Saving model to {model_output_directory}")
    model_unzipped = "opt/ml/model/model.joblib"
    with tarfile.open(model_output_directory, mode="w:gz") as archive:
        archive.add(model_unzipped, arcname="model.joblib")
    return model_output_directory


@dt.working_directory(__file__)
def test_read_features(args):
    """
    Test the data reading in the evaluation module.
    """
    X_test, y_test = read_features(args)

    # check number of observations
    assert X_test.shape[0] == y_test.shape[0]


@dt.working_directory(__file__)
def test_load_model(tar_model, args):
    model = load_model(args)


@dt.working_directory(__file__)
def test_evaluate(load_joblib_model, args):
    X_test, y_test = read_features(args)
    report_dict = evaluate(load_joblib_model, X_test, y_test, args)
    assert "accuracy" in report_dict.keys()
    assert "macro avg" in report_dict.keys()
    assert "f1-score" in report_dict["macro avg"].keys()
    assert isinstance(report_dict["accuracy"], float)
    assert isinstance(report_dict["macro avg"]["f1-score"], float)


@dt.working_directory(__file__)
def test_main(tar_model, args):
    main(args)


@dt.working_directory(__file__)
def test_parse_arg():
    args = parse_arg()
    assert args.data_dir == "/opt/ml/processing"
    assert args.features_input == "test/test_features.csv"
    assert args.labels_input == "test/test_labels.csv"
    assert args.model_input == "model/model.tar.gz"
    assert args.eval_output == "evaluation/evaluation.json"
