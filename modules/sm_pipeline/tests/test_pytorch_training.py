"""
Test PyTorch training on local/sagemaker

Prerequisite:
- Update role
- Update S3 training data directory, decide local or S3 training dataset

"""

import boto3
import sagemaker
from sagemaker.pytorch import PyTorch
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

role = "arn:aws:iam::342474125894:role/service-role/AmazonSageMaker-ExecutionRole-20200829T153114"
ecr_repository_name = "coswara"
account_id = role.split(":")[4]
region = boto3.Session().region_name
sagemaker_session = sagemaker.Session()
bucket = sagemaker_session.default_bucket()
prefix = "coswara-data"

print("Account: {}".format(account_id))
print("Region: {}".format(region))
print("Role: {}".format(role))
print("S3 Bucket: {}".format(bucket))

pytorch_est = PyTorch(
    entry_point="train.py",
    source_dir=f"{BASE_DIR}/../src/project",
    role=role,
    instance_type="local",
    # instance_type="ml.m5.xlarge",
    instance_count=1,
    framework_version="1.6.0",
    py_version="py3",
    hyperparameters={"epochs": 10, "batch-size": 128, "lr": 0.1},
)
pytorch_est.fit(
    # Only download all files from specific directory, cant specify single file. Equivalent to mounting
    {
        "train": "s3://wy-project-template/processed/train/",
        "validation": "s3://wy-project-template/processed/validation/",
    },
    #
    # Only work for local mode
    # {
    #     "train": "file:///opt/ml/processing/train",
    #     "validation": "file:///opt/ml/processing/validation",
    # },
)
