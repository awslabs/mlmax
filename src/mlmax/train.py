import os
import argparse

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score

try:
    from sklearn.externals import joblib
except:
    import joblib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--test", type=str, default=os.environ.get("SM_CHANNEL_TEST"))
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    args, _ = parser.parse_known_args()

    training_data_dir = args.train  # "/opt/ml/input/data/train"
    test_data_dir = args.test

    train_features_data = os.path.join(training_data_dir, "train_features.csv")
    train_labels_data = os.path.join(training_data_dir, "train_labels.csv")
    print("Reading input data")
    X_train = pd.read_csv(train_features_data, header=None)
    y_train = pd.read_csv(train_labels_data, header=None)

    model = LogisticRegression(class_weight="balanced", solver="lbfgs")
    print("Training LR model")
    model.fit(X_train, y_train)

    print("Validating LR model")
    test_features_data = os.path.join(test_data_dir, "test_features.csv")
    test_labels_data = os.path.join(test_data_dir, "test_labels.csv")

    X_test = pd.read_csv(test_features_data, header=None)
    y_test = pd.read_csv(test_labels_data, header=None)
    predictions = model.predict(X_test)

    print("Creating classification evaluation report")
    report_dict = classification_report(y_test, predictions, output_dict=True)
    report_dict["accuracy"] = accuracy_score(y_test, predictions)
    report_dict["roc_auc"] = roc_auc_score(y_test, predictions)

    print(f"Classification report:\n{report_dict}")

    model_output_directory = os.path.join(args.model_dir, "model.joblib")
    print(f"Saving model to {model_output_directory}")
    joblib.dump(model, model_output_directory)
