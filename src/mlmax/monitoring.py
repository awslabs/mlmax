import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from loguru import logger
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


def split_data(df, args):
    split_ratio = args.train_test_split_ratio
    logger.info(f"Splitting data into train and test sets with ratio {split_ratio}")
    return train_test_split(
        df.drop(target_col, axis=1),
        df[target_col],
        test_size=split_ratio,
        random_state=0,
    )


def write_dataframe(data: pd.DataFrame, args, file_prefix, header=False) -> None:
    """Write dataframe into args.data_dir directory + file_prefix."""
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

    dist_dict = {"numerical": hist_list}
    return dist_dict


def get_cat_counts(data: pd.Series) -> dict:
    value_dict = data.value_counts().to_dict()
    value_list = [{"name": name, "count": count} for name, count in value_dict.items()]
    count_dict = {"categorical": value_list}
    return count_dict


def generate_statistic(X_train: pd.DataFrame, y_train: pd.Series, args=None):
    """
    Examples of X_train:

            age                    education                 major industry code ...
    26873    28             5th or 6th grade        Business and repair services
    179865   31   Bachelors degree(BA AB BS)   Finance insurance and real estate

    """
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
    expected: pd.Series,
    actual: pd.Series,
    buckettype: str = "bins",
    bins: int = 10,
    # axis: int = 0,
):
    """Calculate the PSI (population stability index) for a feature.

    Ref:
    https://mwburke.github.io/data%20science/2018/04/29/population-stability-index.html

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
            """Scale values into 10 equal range intervals."""
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
            breakpoints = scale_range(
                breakpoints, np.min(expected_array), np.max(expected_array)
            )
        elif buckettype == "quantiles":
            breakpoints = np.stack(
                [np.percentile(expected_array, b) for b in breakpoints]
            )
        # Percentage of count for each bin
        expected_percents = np.histogram(expected_array, breakpoints)[0] / len(
            expected_array
        )
        actual_percents = np.histogram(actual_array, breakpoints)[0] / len(actual_array)

        psi_value = sum(
            sub_psi(expected_percents[i], actual_percents[i])
            for i in range(0, len(expected_percents))
        )

        return psi_value

    psi_values = psi(expected, actual, bins)
    return psi_values


def get_psi_score(X_train: pd.DataFrame, X_test: pd.DataFrame, args=None) -> List[dict]:
    """Get PSI for numerical columns.

    Return:
        [{'name': 'age', 'psi': 0.000531655721643536}]
    """
    _, num_cols = get_cols_types(X_train)

    psi_list = []
    for col in num_cols:
        temp_dict = {"name": col}
        temp_dict["psi"] = calculate_psi(
            X_train[col], X_test[col], bins=10, buckettype="bins"
        )
        psi_list.append(temp_dict)

    return psi_list


def generate_psi(X_train: pd.DataFrame, X_test: pd.DataFrame, args=None) -> dict:
    psi_score_list = get_psi_score(X_train, X_test)

    # Reformat
    result = {"features": psi_score_list}
    return result


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="train")
    parser.add_argument("--data_dir", type=str, default="/opt/ml/processing")
    parser.add_argument(
        "--train_input", type=str, default="train_input/census-income.csv"
    )
    parser.add_argument(
        "--infer_input", type=str, default="infer_input/census-income.csv"
    )
    parser.add_argument(
        "--infer_baseline",
        type=str,
        default="profiling/baseline/train_features_baseline.csv",
    )
    parser.add_argument("--train_test_split_ratio", type=float, default=0.3)
    args, _ = parser.parse_known_args()
    logger.info(f"Received arguments {args}")
    return args


def main(args):
    """
    All profiling output artifacts will be placed at /opt/ml/processing/profiling.

    Tree:
    /opt/ml/processing/profiling/baseline/
    /opt/ml/processing/profiling/inference/
    """
    # Create directory
    data_dir = Path(args.data_dir)
    (data_dir / "profiling/baseline").mkdir(exist_ok=True, parents=True)
    (data_dir / "profiling/inference").mkdir(exist_ok=True, parents=True)

    if args.mode == "train":

        # TODO: if there data has been in proper format, there is no processing
        # required.
        infer_data_path = os.path.join(args.data_dir, args.train_input)
        df = read_data(infer_data_path)
        X_train, X_test, y_train, y_test = split_data(df, args)

        # Save baseline data for future reference
        write_dataframe(
            X_train, args, "profiling/baseline/train_features_baseline.csv", header=True
        )
        write_dataframe(
            y_train, args, "profiling/baseline/train_labels_baseline.csv", header=True
        )
        write_dataframe(
            X_test, args, "profiling/baseline/test_features.csv", header=True
        )
        write_dataframe(y_test, args, "profiling/baseline/test_labels.csv", header=True)

        # Calculate baseline metrics based on training data
        result = generate_statistic(X_train, y_train, args)
        write_json(result, args, "profiling/baseline/baseline_statistic.json")

        # Calculate PSI for baseline data (train vs test set).
        # Expected to have good score.
        test_result = generate_psi(X_train, X_test, args)
        write_json(test_result, args, "profiling/baseline/baseline_psi.json")

    if args.mode == "infer":
        # Read baseline training features
        baseline_data_path = os.path.join(args.data_dir, args.infer_baseline)
        X_train = pd.read_csv(baseline_data_path)

        # Read new inference features
        infer_data_path = os.path.join(args.data_dir, args.infer_input)
        X_infer = read_data(infer_data_path)
        X_infer = X_infer.drop(["income"], axis=1)

        # Calculate PSI for inference vs baseline data
        test_result = generate_psi(X_train, X_infer, args)
        write_json(test_result, args, "profiling/inference/infer_psi.json")

        # TODO
        # Trigger alert if PSI higher than threshold configuration


if __name__ == "__main__":
    """
    Local run:

    DATA=s3://sagemaker-sample-data-us-east-1/processing/census/census-income.csv
    mkdir -p /opt/ml/processing/train_input
    mkdir -p /opt/ml/processing/infer_input
    aws s3 cp $DATA /opt/ml/processing/train_input/
    cp /opt/ml/processing/train_input/census-income.csv /opt/ml/processing/infer_input/
    python monitoring.py --mode "train" --data_dir /opt/ml/processing
    python monitoring.py --mode "infer" --data_dir /opt/ml/processing
    """

    args = parse_arg()
    main(args)
