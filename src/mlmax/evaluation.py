import argparse
import json
import os
import tarfile

import pandas as pd

try:
    from sklearn.externals import joblib
except ImportError:
    import joblib

from sklearn.metrics import accuracy_score, classification_report, roc_auc_score


def read_features(args):
    print("Loading test input data")
    test_features_data = os.path.join(args.data_dir, args.features_input)
    test_labels_data = os.path.join(args.data_dir, args.labels_input)
    X_test = pd.read_csv(test_features_data, header=None)
    y_test = pd.read_csv(test_labels_data, header=None)
    return X_test, y_test


def load_model(args):
    model_path = os.path.join(args.data_dir, args.model_input)
    print(f"LOAD_MODEL: Extracting model from path: {model_path}")
    print(f"LOAD_MODEL: Extracting model file to {os.getcwd()}")
    with tarfile.open(model_path) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=".")
    print("Loading model")
    return joblib.load("model.joblib")


def evaluate(model, X_test, y_test, args):
    print("Validating LR model")
    predictions = model.predict(X_test)
    print("Creating classification evaluation report")
    report_dict = classification_report(y_test, predictions, output_dict=True)
    report_dict["accuracy"] = accuracy_score(y_test, predictions)
    report_dict["roc_auc"] = roc_auc_score(y_test, predictions)
    print(f"Classification report:\n{report_dict}")
    evaluation_output_path = os.path.join(args.data_dir, args.eval_output)
    print(f"Saving classification report to {evaluation_output_path}")
    with open(evaluation_output_path, "w") as f:
        f.write(json.dumps(report_dict))
    return report_dict


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="/opt/ml/processing")
    parser.add_argument("--features-input", type=str, default="test/test_features.csv")
    parser.add_argument("--labels-input", type=str, default="test/test_labels.csv")
    parser.add_argument("--model-input", type=str, default="model/model.tar.gz")
    parser.add_argument("--eval-output", type=str, default="evaluation/evaluation.json")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args


def main(args):
    X_test, y_test = read_features(args)
    model = load_model(args)
    report_dict = evaluate(model, X_test, y_test, args)
    print(report_dict)


if __name__ == "__main__":
    args = parse_arg()
    main(args)
