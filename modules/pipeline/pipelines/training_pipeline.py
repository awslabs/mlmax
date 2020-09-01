# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import sagemaker
import os

DATA_DIR = 'data'
from stepfunctions.template import TrainingPipeline
from sagemaker.sklearn import SKLearn

sm_role = 'AmazonSageMaker-ExecutionRole-20200419T120196'

# go to console add role and its associated policies
workflow_execution_role = 'arn:aws:iam::671846148176:role/StepFunctionsWorkflowExecutionRole'

def sklearn_estimator(sagemaker_role_arn):
    script_path = os.path.join(DATA_DIR, "sklearn_mnist", "mnist.py")
    return SKLearn(
        entry_point=script_path,
        role=sagemaker_role_arn,
        train_instance_count=1,
        train_instance_type='ml.m5.large',
        framework_version='0.20.0',
        hyperparameters={
            "epochs": 1
        }
    )

def define_sklearn_training_pipeline(sfn_client, sklearn_estimator, sagemaker_session, sfn_role_arn):
    # upload input data
    data_path = os.path.join(DATA_DIR, "sklearn_mnist")
    inputs = sagemaker_session.upload_data(
        path=os.path.join(data_path, "train"),
        bucket=sagemaker_session.default_bucket(),
        key_prefix="integ-test-data/sklearn_mnist/train"
    )

    # create training pipeline
    pipeline = TrainingPipeline(
        sklearn_estimator,
        sfn_role_arn,
        inputs,
        sagemaker_session.default_bucket(),
        sfn_client
    )
    pipeline.create()
    yml = pipeline.workflow.get_cloudformation_template()
    with open('templates/sagemaker_training_pipeline.yaml', 'w') as fout:
        fout.write(yml)

if __name__ == '__main__':
    sm_session = sagemaker.Session()
    ske = sklearn_estimator(sm_role)
    define_sklearn_training_pipeline(None, ske, sm_session, workflow_execution_role)