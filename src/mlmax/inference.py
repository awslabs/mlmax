import os
import argparse
import tarfile
import pandas as pd

try:
    from sklearn.externals import joblib
except:
    import joblib


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    model_path = os.path.join(args.data_dir, "model/model.tar.gz")
    print(f"Extracting model from path: {model_path}")
    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")
    print("Loading model")
    model = joblib.load("model.joblib")

    print("Loading test input data")
    test_features_data = os.path.join(args.data_dir, "input/test_features.csv")
    X_test = pd.read_csv(test_features_data, header=None)
    predictions = model.predict(X_test)
    output_path = os.path.join(args.data_dir, "test/predictions.csv")
    print(f"Saving data to {output_path}")
    pd.DataFrame(predictions).to_csv(output_path, header=False, index=False)
