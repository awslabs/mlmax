import os
import sys

import sagemaker
from sagemaker.spark.processing import PySparkProcessor

BUCKET = "ml-proserve-nyc-taxi-data"

sm_session = sagemaker.Session()
try:
    role = os.environ["ROLE"]
    print(f"Role is set to {role}")
except KeyError:
    print("It doesn't appear that ROLE is set")
    sys.exit()

processor = PySparkProcessor(
    framework_version="2.4",
    role=role,
    instance_count=16,
    instance_type="ml.m5.2xlarge",
    max_runtime_in_seconds=3600,
    sagemaker_session=sm_session,
)


configuration = [
    {"Classification": "spark-defaults", "Properties": {"spark.executor.memory": "4g"},}
]

# This takes ~25mins to complete using 8 x ml.m5.2xlarge instances
processor.run(
    submit_app="src/preprocess.py",
    arguments=[
        "--s3_input_prefix",
        f"s3://{BUCKET}/csv/",
        "--s3_output_prefix",
        f"s3://{BUCKET}/parquet/",
    ],
    configuration=configuration,
    logs=True,
    wait=False,
)
