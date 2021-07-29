import argparse
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

try:
    from sklearn.externals import joblib
except ImportError:
    import joblib


def read_xy(data_dir, mode="train"):
    print(f"Reading {mode} data from {data_dir}")
    X = pd.read_csv(os.path.join(data_dir, f"{mode}_features.csv"), header=None)
    y = pd.read_csv(os.path.join(data_dir, f"{mode}_labels.csv"), header=None)
    return X, y


def read_processed_data(args):
    """
    Note that the directories passed by SageMaker are:
        /opt/ml/input/data/train
        /opt/ml/input/data/test
    """
    X_train, y_train = read_xy(args.train, "train")
    X_test, y_test = read_xy(args.test, "test")
    return X_train, y_train, X_test, y_test


def train(X_train, y_train, args):
    model = LogisticRegression(class_weight="balanced", solver="lbfgs")
    print("Training LR model")
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test, args):
    print("Validating LR model")
    predictions = model.predict(X_test)
    print("Creating classification evaluation report")
    report_dict = classification_report(y_test, predictions, output_dict=True)
    report_dict["accuracy"] = accuracy_score(y_test, predictions)
    report_dict["roc_auc"] = roc_auc_score(y_test, predictions)
    print(f"Classification report:\n{report_dict}")
    return report_dict


def save_model(model, args):
    # model_dir is /opt/ml/model/
    model_output = os.path.join(args.model_dir, "model.joblib")
    print(f"Saving model to {model_output}")
    joblib.dump(model, model_output)


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default="/opt/ml/input/data/train")
    parser.add_argument("--test", type=str, default="/opt/ml/input/data/test")
    parser.add_argument("--model-dir", type=str, default="/opt/ml/model")
    parser.add_argument("--inspect", type=bool, default=False)
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args


def main(args):
    """
    To run locally:

    python train.py --train /tmp/train --test /tmp/test --model-dir /tmp/model
    """
    X_train, y_train, X_test, y_test = read_processed_data(args)
    model = train(X_train, y_train, args)
    report_dict = evaluate(model, X_test, y_test, args)
    print(report_dict)
    save_model(model, args)


if __name__ == "__main__":
    args = parse_arg()
    if args.inspect:
        os.environ["PYTHONINSPECT"] = "1"
    main(args)
