import argparse
import os

import pyspark.sql.functions as F
from pyspark.sql import SparkSession


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3_input_path", default=os.getenv("S3InputPath"), type=str)
    parser.add_argument(
        "--s3_output_path", default=os.getenv("S3OutputPath"), type=str,
    )
    args = parser.parse_args()

    s3_input_path = args.s3_input_path.rstrip("/").lstrip("s3://")
    s3_output_path = args.s3_output_path.rstrip("/").lstrip("s3://")

    # Build the spark session
    spark = (
        SparkSession.builder.appName("SparkProcessor")
        .config("spark.executor.memory", "4g")
        .getOrCreate()
    )

    # Read the raw input csv from S3
    sdf_fhv = spark.read.csv(
        f"s3://{s3_input_path}/fhv_tripdata_*.csv", header=True, inferSchema=True
    )
    sdf_fhvhv = spark.read.csv(
        f"s3://{s3_input_path}/fhvhv_tripdata_*.csv", header=True, inferSchema=True
    )
    sdf_green = spark.read.csv(
        f"s3://{s3_input_path}/green_tripdata_*.csv", header=True, inferSchema=True
    )
    sdf_yellow = spark.read.csv(
        f"s3://{s3_input_path}/yellow_tripdata_*.csv", header=True, inferSchema=True
    )

    sdf0 = (
        sdf_fhv.select(F.col("Pickup_date").alias("dt_pickup"))
        .unionAll(sdf_fhvhv.select(F.col("pickup_datetime").alias("dt_pickup")))
        .unionAll(sdf_green.select(F.col("lpep_pickup_datetime").alias("dt_pickup")))
        .unionAll(sdf_yellow.select(F.col("Trip_Pickup_DateTime").alias("dt_pickup")))
    )

    # Generate ride-counts at 15-minute intervals
    sdf1 = (
        sdf0.groupBy(F.window("dt_pickup", "15 minutes"))
        .agg(F.count("*").alias("num_rides"))
        .withColumn("timestamp", F.col("window.start"))
        .drop("window")
    )

    # Add time-based features
    sdf2 = sdf1.select(
        "*",
        (F.minute("timestamp") + F.hour("timestamp") * 60).alias("minutes"),
        (F.dayofweek("timestamp")).alias("dow"),
        (F.month("timestamp")).alias("month"),
        (F.dayofyear("timestamp")).alias("doy"),
    )

    # Write features to parquet
    sdf2.write.option("header", "true").parquet(
        f"s3://{s3_output_path}/X.parquet", mode="overwrite"
    )

    return


if __name__ == "__main__":
    main()
