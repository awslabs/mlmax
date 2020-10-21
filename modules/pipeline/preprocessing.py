import argparse
import os
import warnings

from io import StringIO
import numpy as np
import pandas as pd
import tarfile

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder,
    KBinsDiscretizer,
)
from sklearn.compose import make_column_transformer

from sklearn.exceptions import DataConversionWarning

warnings.filterwarnings(action="ignore", category=DataConversionWarning)
try:
    from sklearn.externals import joblib
except:
    import joblib


columns = [
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

original_columns = [
    "age",
    "class of worker",
    "detailed industry recode",
    "detailed occupation recode",
    "education",
    "wage per hour",
    "enroll in edu inst last wk",
    "marital stat",
    "major industry code",
    "major occupation code",
    "race",
    "hispanic origin",
    "sex",
    "member of a labor union",
    "reason for unemployment",
    "fill inc questionnaire for veteran's admin",
    "veterans benefits",
    "capital gains",
    "capital losses",
    "dividends from stocks",
    "tax filer stat",
    "region of previous residence",
    "state of previous residence",
    "detailed household and family stat",
    "detailed household summary in household",
    "instance weight",
    "migration code-change in msa",
    "migration code-change in reg",
    "migration code-move within reg",
    "live in this house 1 year ago",
    "migration prev res in sunbelt",
    "num persons worked for employer",
    "family members under 18",
    "country of birth father",
    "country of birth mother",
    "country of birth self",
    "citizenship",
    "own business or self employed",
    "weeks worked in year",
    "year",
    "income",
]

class_labels = [" - 50000.", " 50000+."]


def model_fn(model_dir):
    """
    This loads returns a Scikit-learn Classifier from a model.joblib file in
    the SageMaker model directory model_dir.
    """
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf


def input_fn(request_body, request_content_type):
    """
        Takes request data and de-serializes the data into an object for
        prediction.  When an InvokeEndpoint operation is made against an
        Endpoint running SageMaker model server, the model server receives two
        pieces of information:
            - The request Content-Type, for example "application/json"
            - The request data, which is at most 5 MB (5 * 1024 * 1024 bytes) in size.
        The input_fn is responsible to take the request data and pre-process it
        before prediction.
    Args:
        input_data (obj): the request data.
        content_type (str): the request Content-Type.
    Returns:
        (obj): data ready for prediction.
    """

    # print(request_body)
    print(request_content_type)
    input_data_path = "input.csv"
    print(f"input_fn is called, length is {len(request_body) // 1024 ** 2} MBytes")
    with open(input_data_path, "w") as fout:
        fout.write(request_body)

    print(f"Reading input data from {input_data_path}")
    df = pd.read_csv(input_data_path)
    # df = pd.read_csv(input_data_path, names=original_columns)
    print("Just read it in", df.head(1))
    print("Before selection of DF = ", df.shape)
    df = pd.DataFrame(
        data=df, columns=columns[:-1]
    )  # get rid of the income column (label)
    print("After selection of DF = ", df.shape)
    print(f"null sum = {df.isnull().sum()}")
    df.dropna(inplace=True)
    print(f"after null sum = {df.isnull().sum()}")
    print(f"final shape = {df.shape}")
    print("final head()", df.head(1))
    return df


def predict_fn(input_data, model):
    """Preprocess input data

    We implement this because the default predict_fn uses .predict(), but our
    model is a preprocessor so we want to use .transform().

    The output is returned in the following order:

        rest of features either one hot encoded or standardized
    """
    print(f"predict_fn: input_data - {input_data.columns}")
    print(f"predict_fn: {input_data.head()}")
    print(f"predict_fn: proc_model is {model}")
    features = model.transform(input_data)
    print(f"predict_fn: features extracted {features}")
    return features


def output_fn(prediction, response_content_type):

    strio = StringIO()
    pd.DataFrame(prediction).to_csv(strio, header=False, index=False)
    return strio.getvalue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-test-split-ratio", type=float, default=0.3)
    parser.add_argument("--mode", type=str, default="infer")
    parser.add_argument("--data-dir", type=str, default="opt/ml/processing")
    args, _ = parser.parse_known_args()

    print(f"Received arguments {args}")

    input_data_path = os.path.join(args.data_dir, "input/census-income.csv")

    print(f"Reading input data from {input_data_path}")
    df = pd.read_csv(input_data_path)
    df = pd.DataFrame(data=df, columns=columns)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.replace(class_labels, [0, 1], inplace=True)

    negative_examples, positive_examples = np.bincount(df["income"])
    print(
        f"Data after cleaning: {df.shape}, {positive_examples} positive examples, "
        f"{negative_examples} negative examples"
    )

    if args.mode == "infer":
        model_directory = os.path.join(args.data_dir, "model")
        print(f"Reading model from {model_directory}")
        with tarfile.open(
            os.path.join(model_directory, "proc_model.tar.gz"), mode="r:gz"
        ) as archive:
            archive.extractall(model_directory)
        preprocess = joblib.load(os.path.join(model_directory, "model.joblib"))
        test_features = preprocess.transform(df)

        test_features_output_path = os.path.join(
            args.data_dir, "test/test_features.csv"
        )
        print(f"Saving test features to {test_features_output_path}")
        pd.DataFrame(test_features).to_csv(
            test_features_output_path, header=False, index=False
        )

        test_labels_output_path = os.path.join(args.data_dir, "test/test_labels.csv")
        print(f"Saving test labels to {test_labels_output_path}")
        y_test = df["income"]
        y_test.to_csv(test_labels_output_path, header=False, index=False)
    elif args.mode == "train":
        split_ratio = args.train_test_split_ratio
        print(f"Splitting data into train and test sets with ratio {split_ratio}")
        X_train, X_test, y_train, y_test = train_test_split(
            df.drop("income", axis=1),
            df["income"],
            test_size=split_ratio,
            random_state=0,
        )

        preprocess = make_column_transformer(
            (
                ["age", "num persons worked for employer"],
                KBinsDiscretizer(encode="onehot-dense", n_bins=10),
            ),
            (
                ["capital gains", "capital losses", "dividends from stocks"],
                StandardScaler(),
            ),
            (
                ["education", "major industry code", "class of worker"],
                OneHotEncoder(sparse=False),
            ),
        )
        print("Running preprocessing and feature engineering transformations")
        train_features = preprocess.fit_transform(X_train)
        test_features = preprocess.transform(X_test)

        print(f"Train data shape after preprocessing: {train_features.shape}")
        print(f"Test data shape after preprocessing: {test_features.shape}")

        train_features_output_path = os.path.join(
            args.data_dir, "train/train_features.csv"
        )
        train_labels_output_path = os.path.join(args.data_dir, "train/train_labels.csv")

        test_features_output_path = os.path.join(
            args.data_dir, "test/test_features.csv"
        )
        test_labels_output_path = os.path.join(args.data_dir, "test/test_labels.csv")

        print(f"Saving training features to {train_features_output_path}")
        pd.DataFrame(train_features).to_csv(
            train_features_output_path, header=False, index=False
        )

        print(f"Saving test features to {test_features_output_path}")
        pd.DataFrame(test_features).to_csv(
            test_features_output_path, header=False, index=False
        )

        print(f"Saving training labels to {train_labels_output_path}")
        y_train.to_csv(train_labels_output_path, header=False, index=False)

        print(f"Saving test labels to {test_labels_output_path}")
        y_test.to_csv(test_labels_output_path, header=False, index=False)
        joblib.dump(preprocess, "./model.joblib")
        model_output_directory = os.path.join(args.data_dir, "model/proc_model.tar.gz")
        print(f"Saving model to {model_output_directory}")
        with tarfile.open(model_output_directory, mode="w:gz") as archive:
            archive.add(model_output_directory, recursive=True)
