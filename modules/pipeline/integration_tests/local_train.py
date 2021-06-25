from sagemaker.sklearn.estimator import SKLearn

# Adapted from: https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/scikit_learn_local_processing/SKLearnProcessor_local_processing.py
# and
# https://github.com/aws-samples/amazon-sagemaker-local-mode/blob/main/scikit_learn_script_mode_local_training_and_serving/scikit_learn_script_mode_local_training_and_serving.py

# Configure local execution parameters
CODE_PATH = "../../../src/mlmax/train.py"
INSPECT_AFTER_SCRIPT = False

# For local training a dummy role will be sufficient
role = 'arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001'
sklearn = SKLearn(
    entry_point=CODE_PATH,
    role=role,
    py_version="py3",
    framework_version="0.20.0",
    instance_type="local",
    hyperparameters={"inspect": True if INSPECT_AFTER_SCRIPT else None}
)

print('Starting training job.')
print('Note: if launching for the first time in local mode, container image download might take a few minutes to complete.')
sklearn.fit(
    {"train": "file://../../../tests/mlmax/opt/ml/processing/train/",
     "test": "file://../../../tests/mlmax/opt/ml/processing/test/"},
    wait=True
)
