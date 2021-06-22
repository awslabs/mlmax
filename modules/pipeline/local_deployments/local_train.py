from sagemaker.local import LocalSession
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.model import SKLearnModel


# Adapted from: https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/scikit_learn_local_processing/SKLearnProcessor_local_processing.py
# and
# https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/scikit_learn_script_mode_local_training_and_serving/scikit_learn_script_mode_local_training_and_serving.py
sagemaker_session = LocalSession()
sagemaker_session.config = {'local': {'local_code': True}}

# Configure local execution parameters
INSPECT_AFTER_SCRIPT = True
CODE_PATH = "../../../src/mlmax/training.py"
LOCAL_DATA_PATH = "../../../tests/mlmax/opt/ml/processing/input"
INPUT_DATA_PATH = "input/census-income-sample.csv"
EXECUTION_MODE = "train"  # Configure to either 'train', or 'infer'

# For local training a dummy role will be sufficient
role = 'arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001'
sklearn = SKLearn(
    entry_point="train.py",
    role=role,
    py_version="py3",
    framework_version="0.20.0",
    instance_type="local",
    source_dir="../../../src/mlmax/",
    environment={"PYTHONINSPECT": "1"},
    hyperparameters={"inspect": "True"}
)

print('Starting training job.')
print('Note: if launching for the first time in local mode, container image download might take a few minutes to complete.')
sklearn.fit(
    {"train": "file://../../../tests/mlmax/opt/ml/processing/train/",
     "test": "file://../../../tests/mlmax/opt/ml/processing/test/",
     "config": "file://"},
    wait=True
)
