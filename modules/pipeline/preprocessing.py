import argparse
import os
import warnings
import numpy as np
import pandas as pd
import tarfile

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder,
    LabelBinarizer,
    KBinsDiscretizer,
)
from sklearn.preprocessing import PolynomialFeatures
from sklearn.compose import make_column_transformer
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action="ignore", category=DataConversionWarning)
try:
    from sklearn.externals import joblib
except:
    import joblib

from io import StringIO

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


def print_shape(df):
    negative_examples, positive_examples = np.bincount(df["income"])
    print(
        "Data shape: {}, {} positive examples, {} negative examples".format(
            df.shape, positive_examples, negative_examples
        )
    )

def model_fn(model_dir):
    """
    This loads returns a Scikit-learn Classifier from a model.joblib file in
    the SageMaker model directory model_dir.
    """
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf


# TODO try to comment out the "input_fn" function below, see what happens?
def input_fn(request_body, request_content_type):
    """Takes request data and de-serializes the data into an object for prediction.
        When an InvokeEndpoint operation is made against an Endpoint running SageMaker model server,
        the model server receives two pieces of information:
            - The request Content-Type, for example "application/json"
            - The request data, which is at most 5 MB (5 * 1024 * 1024 bytes) in size.
        The input_fn is responsible to take the request data and pre-process it before prediction.
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

    print("Reading input data from {}".format(input_data_path))
    df = pd.read_csv(input_data_path)
    # df = pd.read_csv(input_data_path, names=original_columns)
    print("Just read it in", df.head(1))
    print("Before selection of DF = ", df.shape)
    df = pd.DataFrame(data=df, columns=columns[:-1]) # get rid of the income column (label)
    print("After selection of DF = ", df.shape)
    print(f"null sum = {df.isnull().sum()}")
    df.dropna(inplace=True)
    print(f"after null sum = {df.isnull().sum()}")
    print(f"final shape = {df.shape}")
    print("final head()", df.head(1))
    return df


def predict_fn(input_data, model):
    """Preprocess input data

    We implement this because the default predict_fn uses .predict(), but our model is a preprocessor
    so we want to use .transform().

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
    args, _ = parser.parse_known_args()

    print("Received arguments {}".format(args))

    input_data_path = os.path.join("/opt/ml/processing/input", "census-income.csv")

    print("Reading input data from {}".format(input_data_path))
    df = pd.read_csv(input_data_path)
    df = pd.DataFrame(data=df, columns=columns)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.replace(class_labels, [0, 1], inplace=True)

    negative_examples, positive_examples = np.bincount(df["income"])
    print(
        "Data after cleaning: {}, {} positive examples, {} negative examples".format(
            df.shape, positive_examples, negative_examples
        )
    )

    split_ratio = args.train_test_split_ratio
    print("Splitting data into train and test sets with ratio {}".format(split_ratio))
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop("income", axis=1), df["income"], test_size=split_ratio, random_state=0
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

    print("Train data shape after preprocessing: {}".format(train_features.shape))
    print("Test data shape after preprocessing: {}".format(test_features.shape))

    train_features_output_path = os.path.join(
        "/opt/ml/processing/train", "train_features.csv"
    )
    train_labels_output_path = os.path.join(
        "/opt/ml/processing/train", "train_labels.csv"
    )

    test_features_output_path = os.path.join(
        "/opt/ml/processing/test", "test_features.csv"
    )
    test_labels_output_path = os.path.join("/opt/ml/processing/test", "test_labels.csv")

    print("Saving training features to {}".format(train_features_output_path))
    pd.DataFrame(train_features).to_csv(
        train_features_output_path, header=False, index=False
    )

    print("Saving test features to {}".format(test_features_output_path))
    pd.DataFrame(test_features).to_csv(
        test_features_output_path, header=False, index=False
    )

    print("Saving training labels to {}".format(train_labels_output_path))
    y_train.to_csv(train_labels_output_path, header=False, index=False)

    print("Saving test labels to {}".format(test_labels_output_path))
    y_test.to_csv(test_labels_output_path, header=False, index=False)

    model_output_directory = "./model.joblib"
    print("Saving model to {}".format(model_output_directory))
    joblib.dump(preprocess, model_output_directory)
    # tar the model
    with tarfile.open('/opt/ml/processing/model/proc_model.tar.gz', mode='w:gz') as archive:
        archive.add(model_output_directory, recursive=True)
