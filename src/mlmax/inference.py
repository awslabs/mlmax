import argparse
import os
import tarfile

import pandas as pd

try:
    from sklearn.externals import joblib
except:
    import joblib


def load_model(data_dir):
    model_path = os.path.join(data_dir, "model/model.tar.gz")
    print(f"extracting model from path: {model_path}")
    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")
    print("loading model")
    model = joblib.load("model.joblib")
    return model


def load_test_input(data_dir):
    print("Loading test input data")
    test_features_data = os.path.join(data_dir, "input/test_features.csv")
    X_test = pd.read_csv(test_features_data, header=None)
    return X_test


def write_data(data, data_dir, file_prefix):
    output_path = os.path.join(data_dir, file_prefix)
    print(f"Saving data to {output_path}")
    pd.DataFrame(data).to_csv(output_path, header=False, index=False)


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args


def main(args):
    model = load_model(args.data_dir)
    X_test = load_test_input(args.data_dir)
    predictions = model.predict(X_test)
    write_data(predictions, args.data_dir, "test/predictions.csv")


if __name__ == "__main__":
    args = parse_arg()
    main(args)
