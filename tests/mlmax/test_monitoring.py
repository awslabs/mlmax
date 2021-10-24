import argparse
import json

import numpy as np
import pandas as pd
import pytest

from mlmax.monitoring import (
    calculate_psi,
    generate_psi,
    generate_statistic,
    get_cat_counts,
    get_cols_types,
    get_dataframe_stats,
    get_num_distribution,
    write_dataframe,
    write_json,
)


@pytest.fixture()
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="train")
    parser.add_argument("--data_dir", type=str, default="/opt/ml/processing")
    parser.add_argument(
        "--data_input", type=str, default="train_input/census-income.csv"
    )
    parser.add_argument("--train_test_split_ratio", type=float, default=0.3)
    parser.add_argument(
        "--transformer_input", type=str, default="proc_model/proc_model.tar.gz"
    )
    parser.add_argument("--model_input", type=str, default="model/model.tar.gz")
    args, _ = parser.parse_known_args()
    print(f"Received arguments {args}")
    return args


@pytest.fixture
def dummy_df():
    df = pd.DataFrame(
        {
            "f1": np.arange(1, 11),
            "f2": ["a", "a", "a", "a", "a", "b", "c", "d", "d", "d"],
        }
    )
    df.astype(dtype={"f1": int, "f2": str})
    return df


@pytest.fixture
def psi_df():
    df = pd.DataFrame({"f1": np.arange(1, 11), "f2": np.arange(3, 13)})
    df.astype(dtype={"f1": float, "f2": float})
    return df


def test_write_dataframe(dummy_df, args, tmpdir):
    file = tmpdir.join("output.txt")
    write_dataframe(dummy_df.iloc[:2], args, str(file), header=True)
    print(str(file.read()))
    expected = "f1,f2\n1,a\n2,a\n"
    assert file.read() == expected


def test_write_json(dummy_df, args, tmpdir):
    file = tmpdir.join("output.json")
    data = {"a": "harlo"}
    write_json(data, args, file)
    assert file.read() == json.dumps(data)


def test_get_cols_types(dummy_df):
    cat_cols, num_cols = get_cols_types(dummy_df)
    assert cat_cols.tolist() == ["f2"]
    assert num_cols.tolist() == ["f1"]


def test_get_dataframe_stats(dummy_df):
    stats_dict = get_dataframe_stats(dummy_df)
    expected = {
        "f1": {
            "count": 10.0,
            "unique": "nan",
            "top": "nan",
            "freq": "nan",
            "mean": 5.5,
            "std": 3.0276503540974917,
            "min": 1.0,
            "25%": 3.25,
            "50%": 5.5,
            "75%": 7.75,
            "max": 10.0,
            "nan": 0.0,
            "nan_ratio": 0.0,
        },
        "f2": {
            "count": 10,
            "unique": 4,
            "top": "a",
            "freq": 5,
            "mean": "nan",
            "std": "nan",
            "min": "nan",
            "25%": "nan",
            "50%": "nan",
            "75%": "nan",
            "max": "nan",
            "nan": 0,
            "nan_ratio": 0.0,
        },
    }

    assert stats_dict == expected


def test_get_num_distribution(dummy_df):
    dist_dict = get_num_distribution(dummy_df["f1"])
    expected = {
        "numerical": [
            {"lower_bound": 1.0, "upper_bound": 1.9, "count": 1},
            {"lower_bound": 1.9, "upper_bound": 2.8, "count": 1},
            {"lower_bound": 2.8, "upper_bound": 3.7, "count": 1},
            {"lower_bound": 3.7, "upper_bound": 4.6, "count": 1},
            {"lower_bound": 4.6, "upper_bound": 5.5, "count": 1},
            {"lower_bound": 5.5, "upper_bound": 6.4, "count": 1},
            {"lower_bound": 6.4, "upper_bound": 7.3, "count": 1},
            {"lower_bound": 7.3, "upper_bound": 8.2, "count": 1},
            {"lower_bound": 8.2, "upper_bound": 9.1, "count": 1},
        ]
    }
    assert dist_dict == expected


def test_get_cat_counts(dummy_df):
    count_dict = get_cat_counts(dummy_df["f2"])
    expected = {
        "categorical": [
            {"name": "a", "count": 5},
            {"name": "d", "count": 3},
            {"name": "b", "count": 1},
            {"name": "c", "count": 1},
        ]
    }
    assert count_dict == expected


def test_train_data_profiling(dummy_df, args):
    result = generate_statistic(dummy_df, dummy_df, args)
    expected = {
        "features": [
            {
                "name": "f1",
                "statistic": {
                    "count": 10.0,
                    "unique": "nan",
                    "top": "nan",
                    "freq": "nan",
                    "mean": 5.5,
                    "std": 3.0276503540974917,
                    "min": 1.0,
                    "25%": 3.25,
                    "50%": 5.5,
                    "75%": 7.75,
                    "max": 10.0,
                    "nan": 0.0,
                    "nan_ratio": 0.0,
                    "skew": 0.0,
                    "kurtosis": -1.2000000000000002,
                    "distribution": {
                        "numerical": [
                            {"lower_bound": 1.0, "upper_bound": 1.9, "count": 1},
                            {"lower_bound": 1.9, "upper_bound": 2.8, "count": 1},
                            {"lower_bound": 2.8, "upper_bound": 3.7, "count": 1},
                            {"lower_bound": 3.7, "upper_bound": 4.6, "count": 1},
                            {"lower_bound": 4.6, "upper_bound": 5.5, "count": 1},
                            {"lower_bound": 5.5, "upper_bound": 6.4, "count": 1},
                            {"lower_bound": 6.4, "upper_bound": 7.3, "count": 1},
                            {"lower_bound": 7.3, "upper_bound": 8.2, "count": 1},
                            {"lower_bound": 8.2, "upper_bound": 9.1, "count": 1},
                        ]
                    },
                },
            },
            {
                "name": "f2",
                "statistic": {
                    "count": 10,
                    "unique": 4,
                    "top": "a",
                    "freq": 5,
                    "mean": "nan",
                    "std": "nan",
                    "min": "nan",
                    "25%": "nan",
                    "50%": "nan",
                    "75%": "nan",
                    "max": "nan",
                    "nan": 0,
                    "nan_ratio": 0.0,
                    "distribution": {
                        "categorical": [
                            {"name": "a", "count": 5},
                            {"name": "d", "count": 3},
                            {"name": "b", "count": 1},
                            {"name": "c", "count": 1},
                        ]
                    },
                },
            },
        ]
    }
    assert result == expected


def test_calculate_psi(psi_df):
    result = calculate_psi(psi_df["f1"], psi_df["f2"], buckettype="bins", bins=10)
    assert round(result, 5) == 1.38017


def test_infer_data_profiling(psi_df):
    result = generate_psi(psi_df, psi_df)
    expected = {"features": [{"name": "f1", "psi": 0.0}, {"name": "f2", "psi": 0.0}]}
    assert result == expected
