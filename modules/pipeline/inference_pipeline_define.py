import uuid
import tarfile
import argparse
import configparser

import stepfunctions
from stepfunctions import steps
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import (
    Chain,
    ChoiceRule,
    ModelStep,
    ProcessingStep,
    TrainingStep,
    TransformStep,
)
from custom_steps import MLMaxBatchTransformStep
from stepfunctions.workflow import Workflow

import sagemaker
from sagemaker import get_execution_role
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.s3 import S3Uploader
#from sagemaker.sklearn.processing import SKLearnProcessor

#from sagemaker.sklearn.estimator import SKLearn
from sagemaker.transformer import Transformer

def define_inference_pipeline(sm_role,
                             workflow_execution_role,
                             inference_pipeline_name,
                             return_yaml=True,
                             dump_yaml_file='templates/sagemaker_inference_pipeline.yaml'):
    """
    Return YAML definition of the training pipeline, which consists of multiple Amazon StepFunction steps

    sm_role:                    ARN of the SageMaker execution role
    workflow_execution_role:    ARN of the StepFunction execution role
    return_yaml:                Return YAML representation or not, if False,
                                it returns an instance of `stepfunctions.workflow.WorkflowObject`
    dump_yaml_file:             If not None, a YAML file will be generated at this file location

    """

    # Pass required parameters dynamically for each execution using placeholders.
    execution_input = ExecutionInput(
        schema={
            "InputDataURL": str,
            #"InputCodeURL": str,
            "PreprocessingJobName": str,
            "BatchTransformJobName": str,
            "ProcModelName": str,
            "ModelName": str,
            "PreprocessedTrainDataURL": str,
            "PreprocessedTestDataURL": str,
            "OutputPathURL": str,
        }
    )

    """
    Preprocessing transformer
    """
    transformer_proc = Transformer(
        model_name="preprocess_model_name",
        instance_count=1,
        instance_type="ml.c5.xlarge",
        strategy="MultiRecord",
        max_payload=100,
    )

    process_transformer_step = MLMaxBatchTransformStep(
        "SageMaker Preprocess BatchTransform step",
        transformer_proc,
        job_name=execution_input["PreprocessingJobName"],
        model_name=execution_input["ProcModelName"],
        data=execution_input["InputDataURL"],
        outputpath=execution_input["PreprocessedTestDataURL"],
        split_type="Line",
    )

    """
    Inference (batch transform) using the pre-processed data and previous model.
    """

    transformer = Transformer(
        model_name="dummy_model_name",
        instance_count=1,
        instance_type="ml.c5.xlarge",
        strategy="MultiRecord",
    )

    infer_transformer_step = MLMaxBatchTransformStep(
        "SageMaker Inference BatchTransform step",
        transformer,
        job_name=execution_input["BatchTransformJobName"],
        model_name=execution_input["ModelName"],
        data=execution_input["PreprocessedTestDataURL"],
        outputpath=execution_input["OutputPathURL"],
        split_type="Line",
    )

    # Create Fail state to mark the workflow failed in case any of the steps fail.
    failed_state_sagemaker_processing_failure = stepfunctions.steps.states.Fail(
        "ML Workflow failed", cause="SageMakerProcessingJobFailed"
    )

    # Add the Error handling in the workflow
    catch_state_processing = stepfunctions.steps.states.Catch(
        error_equals=["States.TaskFailed"],
        next_step=failed_state_sagemaker_processing_failure,
    )

    process_transformer_step.add_catch(catch_state_processing)
    infer_transformer_step.add_catch(catch_state_processing)

    # Create the Workflow
    workflow_graph = Chain([process_transformer_step, infer_transformer_step])
    inference_pipeline = Workflow(
        name=inference_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )
    return inference_pipeline
