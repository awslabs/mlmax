import argparse
import json
import os
<<<<<<< HEAD
=======
import tarfile
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415
from typing import List, Tuple

import numpy as np
import pandas as pd
from loguru import logger

try:
    from sklearn.externals import joblib
except ImportError:
    import joblib

<<<<<<< HEAD
from sklearn.model_selection import train_test_split

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

target_col = "income"
class_labels = [" - 50000.", " 50000+."]
=======
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

from mlmax.preprocessing import read_data, split_data, transform

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

target_col = "income"
class_labels = [" - 50000.", " 50000+."]


def write_dataframe(data: pd.DataFrame, args, file_prefix, header=False) -> None:
    output_path = os.path.join(args.output_dir, file_prefix)
    print(f"Saving data to {output_path}")
    pd.DataFrame(data).to_csv(output_path, header=header, index=False)


def read_json(file: str) -> dict:
    with open(file, "r") as f:
        data = json.load(f)
    return data


def write_json(data: dict, args, file_prefix) -> None:
    output_path = os.path.join(args.data_dir, file_prefix)
    print(f"Saving data to {output_path}")
    with open(output_path, "w") as f:
        json.dump(data, f)


def load_transformer(args):
    transformer_path = os.path.join(args.data_dir, args.transformer_input)
    print(f"LOAD_TRANSFORMER: Extracting transfomer from path: {transformer_path}")
    print(f"LOAD_TRANSFORMER: Extracting transfomer file to {os.getcwd()}")
    with tarfile.open(transformer_path) as tar:
        tar.extractall(path=".")
    print("Loading model")
    return joblib.load("model.joblib")
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415


def read_data(input_data_path):
    logger.info(f"Reading input data from {input_data_path}")
    df = pd.read_csv(input_data_path)
    df = pd.DataFrame(data=df, columns=columns)
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df.replace(class_labels, list(range(len(class_labels))), inplace=True)
    negative_examples, positive_examples = np.bincount(df[target_col])
    logger.info(
        f"Data after cleaning: {df.shape}, {positive_examples} positive examples, "
        f"{negative_examples} negative examples"
    )
    return df

<<<<<<< HEAD

def split_data(df, args):
    split_ratio = args.train_test_split_ratio
    logger.info(f"Splitting data into train and test sets with ratio {split_ratio}")
    return train_test_split(
        df.drop(target_col, axis=1), df[target_col], test_size=split_ratio, random_state=0,
    )
=======
def get_cols_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    cat_cols = df.columns[df.dtypes == "object"]
    num_cols = df.columns[df.dtypes != "object"]
    assert (len(cat_cols) + len(num_cols)) == len(df.columns)
    return cat_cols, num_cols


def get_dataframe_stats(df: pd.DataFrame):

    stats_df = df.describe(include="all")
    missing_series = df.isnull().sum(axis=0)
    missing_series.name = "nan"
    stats_df = stats_df.append(missing_series)
    missing_ratio = stats_df.loc["nan"] / stats_df.loc["count"]
    missing_ratio.name = "nan_ratio"
    stats_df = stats_df.append(missing_ratio)
    return stats_df

>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415

def get_num_distribution(data: pd.Series) -> dict:
    counts, bins = np.histogram(data, bins=10)
    # counts, bins = counts.astype(np.int32), bins.astype(np.float32)
    hist_list = []
    for i in range(len(counts) - 1):
        data = {
            "lower_bound": float(f"{bins[i]:.02f}"),
            "upper_bound": float(f"{bins[i + 1]:.02f}"),
            "count": int(counts[i]),
        }
        hist_list.append(data)

<<<<<<< HEAD
def write_dataframe(data: pd.DataFrame, args, file_prefix, header=False) -> None:
    output_path = os.path.join(args.data_dir, file_prefix)
    logger.info(f"Saving data to {output_path}")
    pd.DataFrame(data).to_csv(output_path, header=header, index=False)


def read_json(file: str) -> dict:
    with open(file, "r") as f:
        data = json.load(f)
    return data


def write_json(data: dict, args, file_prefix) -> None:
    output_path = os.path.join(args.data_dir, file_prefix)
    logger.info(f"Saving data to {output_path}")
    with open(output_path, "w") as f:
        json.dump(data, f)


def get_cols_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    cat_cols = df.columns[df.dtypes == "object"]
    num_cols = df.columns[df.dtypes != "object"]
    assert (len(cat_cols) + len(num_cols)) == len(df.columns)
    return cat_cols, num_cols


def get_dataframe_stats(df: pd.DataFrame) -> dict:
    stats_df = df.describe(include="all")
    missing_series = df.isnull().sum(axis=0)
    missing_series.name = "nan"
    stats_df = stats_df.append(missing_series)
    missing_ratio = stats_df.loc["nan"] / stats_df.loc["count"]
    missing_ratio.name = "nan_ratio"
    stats_df = stats_df.append(missing_ratio)
    stats_dict = stats_df.fillna("nan").to_dict()
    return stats_dict


def get_num_distribution(data: pd.Series) -> dict:
    counts, bins = np.histogram(data, bins=10)
    # counts, bins = counts.astype(np.int32), bins.astype(np.float32)
    hist_list = []
    for i in range(len(counts) - 1):
        data = {
            "lower_bound": float(f"{bins[i]:.02f}"),
            "upper_bound": float(f"{bins[i + 1]:.02f}"),
            "count": int(counts[i]),
        }
        hist_list.append(data)

=======
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415
    dist_dict = {"numerical": hist_list}
    return dist_dict


def get_cat_counts(data: pd.Series) -> dict:
    value_dict = data.value_counts().to_dict()
    value_list = [{"name": name, "count": count} for name, count in value_dict.items()]
    count_dict = {"categorical": value_list}
    return count_dict


<<<<<<< HEAD
def train_data_profiling(X_train: pd.DataFrame, y_train: pd.Series, args=None):
    cat_cols, num_cols = get_cols_types(X_train)
    logger.info(f"Categorical cols: {cat_cols}")
    logger.info(f"Numerical cols: {num_cols}")
    stats_dict = get_dataframe_stats(X_train)
    for col, dtype in X_train.dtypes.to_dict().items():
        logger.debug(col, dtype)
        if dtype == "object":
            dist = get_cat_counts(X_train[col])
        else:
            dist = get_num_distribution(X_train[col])
            skew = X_train[col].skew()
            kurtosis = X_train[col].kurtosis()
            stats_dict[col]["skew"] = skew
            stats_dict[col]["kurtosis"] = kurtosis

        stats_dict[col]["distribution"] = dist

    # Reformat
    festures_list = [{"name": k, "statistic": v} for k, v in stats_dict.items()]
    result = {"features": festures_list}

    return result


def calculate_psi(
    expected: pd.Series, actual: pd.Series, buckettype: str = "bins", bins: int = 10, axis: int = 0
):
    """Calculate the PSI (population stability index) across all variables
    Ref:
    https://mwburke.github.io/data%20science/2018/04/29/population-stability-index.html

    Args:
       expected: numpy matrix of original values
       actual: numpy matrix of new values, same size as expected
       buckettype: "bins" or "quantiles"
       buckets: number of quantiles to use in bucketing variables
       axis: axis by which variables are defined, 0 for vertical, 1 for horizontal

    Returns:
       psi_values: ndarray of psi values for each variable
    """
    assert buckettype in ["bins", "quantiles"]

    def psi(expected_array, actual_array, bins):
        """Calculate the PSI for a single variable
        Args:
           expected_array: numpy array of original values
           actual_array: numpy array of new values, same size as expected
           buckets: number of percentile ranges to bucket the values into

        Returns:
           psi_value: calculated PSI value
        """

        def scale_range(input_arr: np.ndarray, new_min: float, new_max: float):
            temp = (new_max - new_min) * (input_arr - np.min(input_arr))
            temp = temp / (np.max(input_arr) - np.min(input_arr))
            temp = temp + new_min
            return temp

        def sub_psi(e_perc, a_perc):
            """Calculate the actual PSI value from comparing the values.
               Update the actual value to a very small number if equal to zero
            """
            if a_perc == 0:
                a_perc = 0.0001
            if e_perc == 0:
                e_perc = 0.0001

            value = (e_perc - a_perc) * np.log(e_perc / a_perc)
            return value

        # Breakpoint [0, 100] with equal bins
        breakpoints = np.arange(0, bins + 1) / bins * 100

        if buckettype == "bins":
            breakpoints = scale_range(breakpoints, np.min(expected_array), np.max(expected_array))
        elif buckettype == "quantiles":
            breakpoints = np.stack([np.percentile(expected_array, b) for b in breakpoints])

        expected_percents = np.histogram(expected_array, breakpoints)[0] / len(expected_array)
        actual_percents = np.histogram(actual_array, breakpoints)[0] / len(actual_array)

        psi_value = sum(
            sub_psi(expected_percents[i], actual_percents[i])
            for i in range(0, len(expected_percents))
        )

        return psi_value

    if len(expected.shape) == 1:
        psi_values = np.empty(len(expected.shape))
    else:
        psi_values = np.empty(expected.shape[axis])

    for i in range(0, len(psi_values)):
        if len(psi_values) == 1:
            psi_values = psi(expected, actual, bins)
        elif axis == 0:
            psi_values[i] = psi(expected[:, i], actual[:, i], bins)
        elif axis == 1:
            psi_values[i] = psi(expected[i, :], actual[i, :], bins)

    return psi_values


def get_psi_score(X_train: pd.DataFrame, X_test: pd.DataFrame, args=None):
    """Get PSI for numerical columns."""
    _, num_cols = get_cols_types(X_train)

    psi_list = []
    for col in num_cols:
        temp_dict = {"name": col}
        temp_dict["psi"] = calculate_psi(X_train[col], X_test[col], bins=10, buckettype="bins")
        psi_list.append(temp_dict)

    return psi_list


def infer_data_profiling(X_train: pd.DataFrame, X_test: pd.DataFrame, args=None) -> dict:
    psi_score_list = get_psi_score(X_train, X_test)

    # Reformat
    result = {"features": psi_score_list}
    return result
=======
def train_data_profiling(X_train, y_train, args=None):
    df = pd.DataFrame(X_train)
    cat_cols, num_cols = get_cols_types(df)
    print(f"Categorical cols: {cat_cols}")
    print(f"Numerical cols: {num_cols}")
    stats_dict = get_dataframe_stats(df).fillna("nan").to_dict()

    for col, dtype in df.dtypes.to_dict().items():
        print(col, dtype)
        if dtype == "object":
            dist = get_cat_counts(df[col])
        else:
            dist = get_num_distribution(df[col])

        stats_dict[col]["distribution"] = dist

    write_json(stats_dict, args, "profiling/training_baseline.json")
    return stats_dict
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="train")
    parser.add_argument("--data_dir", type=str, default="/opt/ml/processing")
    parser.add_argument("--data_input", type=str, default="input/census-income.csv")
    parser.add_argument("--train_test_split_ratio", type=float, default=0.3)
<<<<<<< HEAD
=======
    parser.add_argument(
        "--transformer_input", type=str, default="model/proc_model.tar.gz"
    )
    parser.add_argument("--model_input", type=str, default="model/model.tar.gz")
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415
    args, _ = parser.parse_known_args()
    logger.info(f"Received arguments {args}")
    return args


def main(args):
<<<<<<< HEAD
    input_data_path = os.path.join(args.data_dir, args.data_input)
    df = read_data(input_data_path)

    if args.mode == "train":
        X_train, X_test, y_train, y_test = split_data(df, args)
=======
    """
    To run locally:

    DATA=s3://sagemaker-sample-data-us-east-1/processing/census/census-income.csv
    aws s3 cp $DATA /tmp/input/
    mkdir /tmp/{train,test,model}
    python preprocessing.py --mode "train" --data-dir /tmp
    """
    input_data_path = os.path.join(args.data_dir, args.data_input)
    df = read_data(input_data_path)

    if args.mode == "infer":
        test_features = transform(df, args)
        # write_data(test_features, args, "test/test_features.csv")
        # if target_col in df.columns:
        #     write_data(df[target_col], args, "test/test_labels.csv")
        # return test_features

    elif args.mode == "train":
        X_train, X_test, y_train, y_test = split_data(df, args)
        train_data_profiling(X_train, X_test, args)

        preprocess = load_transformer(args)

    # transformer = load_transformer(args)

    # model = load_model(args)
    # train_features = transform(X_train, args, transformer)
    # test_features = transform(X_test, args, transformer)
    # y_pred = model.predict(X_test)
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415

        # Training data (before preprocess) as baseline
        write_dataframe(X_train, args, "profiling/train_features_baseline.csv", header=True)
        write_dataframe(y_train, args, "profiling/train_labels_baseline.csv", header=True)
        write_dataframe(X_test, args, "profiling/test_features.csv", header=True)
        write_dataframe(y_test, args, "profiling/test_labels.csv", header=True)

<<<<<<< HEAD
        result = train_data_profiling(X_train, y_train, args)
        write_json(result, args, "profiling/statistic_baseline.json")

        test_result = infer_data_profiling(X_train, X_test, args)
        write_json(test_result, args, "profiling/psi.json")


=======
"""
Local run
sudo aws s3 cp s3://sagemaker-ap-southeast-1-342474125894/scikit-learn-sm-preprocessing-24404ccc058511eca494027eb9b287ec/output/test_data/test_features.csv \
/opt/ml/processing/test/

sudo aws s3 cp s3://sagemaker-ap-southeast-1-342474125894/scikit-learn-sm-preprocessing-24404ccc058511eca494027eb9b287ec/output/test_data/test_labels.csv \
/opt/ml/processing/test/

sudo aws s3 cp s3://sagemaker-sample-data-us-east-1/processing/census/census-income.csv /opt/ml/processing/input/census-income.csv

sudo aws s3 cp s3://sagemaker-ap-southeast-1-342474125894/scikit-learn-training-24404ccc058511eca494027eb9b287ec/output/model.tar.gz \
/opt/ml/processing/model/

sudo aws s3 cp s3://sagemaker-ap-southeast-1-342474125894/scikit-learn-sm-preprocessing-24404ccc058511eca494027eb9b287ec/output/proc_model.tar.gz \
/opt/ml/processing/model/
"""
>>>>>>> bb143d8e45225e30ae73a99e808ab371e054d415
if __name__ == "__main__":
    """
    Local run:

    DATA=s3://sagemaker-sample-data-us-east-1/processing/census/census-income.csv
    aws s3 cp $DATA /tmp/input/
    mkdir /tmp/{profiling}
    python preprocessing.py --mode "train" --data-dir /tmp

    """

    args = parse_arg()
    main(args)
