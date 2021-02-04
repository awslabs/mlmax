"""
Test PyTorch model deployment to endpoint

Prerequisite:
- Update role
- Update model location

"""

from sagemaker.pytorch import PyTorchModel
import boto3
import sagemaker
import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

role = "arn:aws:iam::342474125894:role/service-role/AmazonSageMaker-ExecutionRole-20200829T153114"
account_id = role.split(":")[4]
region = boto3.Session().region_name
sagemaker_session = sagemaker.Session()
bucket = sagemaker_session.default_bucket()
model_location = (
    "s3://sagemaker-ap-southeast-1-342474125894/pytorch-training-2021-01-16-06-26-06-283/output/model.tar.gz"
)

print("Account: {}".format(account_id))
print("Region: {}".format(region))
print("Role: {}".format(role))
print("S3 Bucket: {}".format(bucket))

pytorch_model = PyTorchModel(
    model_data=model_location,
    role=role,
    entry_point="inference.py",
    source_dir="src/project",
    py_version="py3",
    framework_version="1.5.0",
)
predictor = pytorch_model.deploy(initial_instance_count=1, instance_type="ml.m5.2xlarge", wait=True)

print(f"Endpoint: {pytorch_model.endpoint_name}")
