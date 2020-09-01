# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import os
import json
from datetime import datetime

import sagemaker
from sagemaker.sklearn.estimator import SKLearn

from stepfunctions.template.pipeline import InferencePipeline

# Constants
BASE_NAME = 'inference-pipeline-integtest'
COMPRESSED_NPY_DATA = 'mnist.npy.gz'
DATA_DIR = 'data'
sm_role = 'AmazonSageMaker-ExecutionRole-20200419T120196'

# go to console add role and its associated policies
workflow_execution_role = 'arn:aws:iam::671846148176:role/StepFunctionsWorkflowExecutionRole'


def sklearn_preprocessor(sagemaker_role_arn, sagemaker_session):
    script_path = os.path.join(DATA_DIR,
                               'one_p_mnist',
                               'sklearn_mnist_preprocessor.py')
    sklearn_preprocessor = SKLearn(
        entry_point=script_path,
        role=sagemaker_role_arn,
        train_instance_type="ml.m5.large",
        sagemaker_session=sagemaker_session,
        hyperparameters={"epochs": 1},
    )
    return sklearn_preprocessor


def sklearn_estimator(sagemaker_role_arn, sagemaker_session):
    script_path = os.path.join(DATA_DIR,
                               'one_p_mnist',
                               'sklearn_mnist_estimator.py')
    sklearn_estimator = SKLearn(
        entry_point=script_path,
        role=sagemaker_role_arn,
        train_instance_type="ml.m5.large",
        sagemaker_session=sagemaker_session,
        hyperparameters={"epochs": 1},
        input_mode='File'
    )
    return sklearn_estimator


def inputs(sagemaker_session):
    data_path = os.path.join(DATA_DIR, "one_p_mnist", COMPRESSED_NPY_DATA)
    inputs = sagemaker_session.upload_data(
        path=data_path, key_prefix='dataset/one_p_mnist'
    )
    return inputs


def define_inference_pipeline_framework(
        sagemaker_session,
        sfn_role_arn,
        sagemaker_role_arn,
        sklearn_preprocessor,
        sklearn_estimator,
        inputs):
    bucket_name = sagemaker_session.default_bucket()
    unique_name = '{}-{}'.format(BASE_NAME,
                                 datetime.now().strftime('%Y%m%d%H%M%S'))
    pipeline = InferencePipeline(
        preprocessor=sklearn_preprocessor,
        estimator=sklearn_estimator,
        inputs={'train': inputs, 'test': inputs},
        s3_bucket=bucket_name,
        role=sfn_role_arn,
        compression_type='Gzip',
        content_type='application/x-npy',
        pipeline_name=unique_name
    )

    pipeline.create()
    yml = pipeline.workflow.get_cloudformation_template()
    with open('templates/sagemaker_inference_pipeline.yaml', 'w') as fout:
        fout.write(yml)


if __name__ == '__main__':
    sm_session = sagemaker.Session()
    ske = sklearn_estimator(sm_role, sm_session)
    skp = sklearn_preprocessor(sm_role, sm_session)
    ip = inputs(sm_session)
    define_inference_pipeline_framework(
        sm_session, workflow_execution_role, sm_role, skp, ske, ip)
