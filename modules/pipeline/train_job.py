import uuid
import tarfile
import argparse

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
from custom_steps import MLMaxTrainingStep
from stepfunctions.workflow import Workflow

import sagemaker
from sagemaker import get_execution_role
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.s3 import S3Uploader
from sagemaker.sklearn.processing import SKLearnProcessor

from sagemaker.sklearn.estimator import SKLearn

import pandas as pd


EXCUTE_WORKFLOW = False


def define_training_pipeline(sm_role,
                             workflow_execution_role,
                             training_pipeline_name,
                             return_yaml=True,
                             dump_yaml_file='templates/sagemaker_training_pipeline.yaml'):
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
            "PreprocessingJobName": str,
            "PreprocessingCodeURL": str,
            "TrainingJobName": str,
            # Prevent sagemaker config hardcode sagemaker_submit_directory in workflow definition
            "SMSubmitDirURL": str,
            # Prevent sagemaker config hardcode sagemaker_region in workflow definition
            "SMRegion": str,
            "EvaluationProcessingJobName": str,
            "EvaluationCodeURL": str,
            "EvaluationResultURL": str,
            "PreprocessedTrainDataURL": str,
            "PreprocessedTestDataURL": str,
            "SMOutputDataURL": str,
            "SMDebugOutputURL": str,
        }
    )

    """
    Data pre-processing and feature engineering
    """
    sklearn_processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=sm_role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=1200,
    )

    # Create ProcessingInputs and ProcessingOutputs objects for Inputs and
    # Outputs respectively for the SageMaker Processing Job
    inputs = [
        ProcessingInput(
            source=execution_input["InputDataURL"],
            destination="/opt/ml/processing/input",
            input_name="input-1"
        ),
        ProcessingInput(
            source=execution_input["PreprocessingCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/train",
            destination=execution_input["PreprocessedTrainDataURL"],
            output_name="train_data",
        ),
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination=execution_input["PreprocessedTestDataURL"],
            output_name="test_data",
        ),
    ]

    processing_step = ProcessingStep(
        "SageMaker pre-processing step",
        processor=sklearn_processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--train-test-split-ratio", "0.2"],
        container_entrypoint=[
            "python3", "/opt/ml/processing/input/code/preprocessing.py"],
    )

    """
    Training using the pre-processed data
    """
    sklearn = SKLearn(entry_point="train.py",
                      train_instance_type="ml.m5.xlarge", role=sm_role)

    training_step = MLMaxTrainingStep(
        "SageMaker Training Step",
        estimator=sklearn,
        job_name=execution_input["TrainingJobName"],
        train_data=execution_input["PreprocessedTrainDataURL"],
        test_data=execution_input["PreprocessedTestDataURL"],
        sm_submit_url=execution_input["SMSubmitDirURL"],
        sm_region=execution_input["SMRegion"],
        sm_output_data=execution_input["SMOutputDataURL"],
        sm_debug_output_data=execution_input["SMDebugOutputURL"],
        wait_for_completion=True,
    )

    """
    Model evaluation
    """
    # Create input and output objects for Model Evaluation ProcessingStep.
    inputs_evaluation = [
        ProcessingInput(
            source=execution_input["PreprocessedTestDataURL"],
            destination="/opt/ml/processing/test",
            input_name="input-1",
        ),
        ProcessingInput(
            source=training_step.get_expected_model().model_data,
            destination="/opt/ml/processing/model",
            input_name="input-2",
        ),
        ProcessingInput(
            source=execution_input["EvaluationCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs_evaluation = [
        ProcessingOutput(
            source="/opt/ml/processing/evaluation",
            destination=execution_input["EvaluationResultURL"],
            output_name="evaluation",
        ),
    ]

    model_evaluation_processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=sm_role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=1200,
    )

    processing_evaluation_step = ProcessingStep(
        "SageMaker Processing Model Evaluation step",
        processor=model_evaluation_processor,
        job_name=execution_input["EvaluationProcessingJobName"],
        inputs=inputs_evaluation,
        outputs=outputs_evaluation,
        container_entrypoint=["python3",
                              "/opt/ml/processing/input/code/evaluation.py"],
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
    processing_step.add_catch(catch_state_processing)
    processing_evaluation_step.add_catch(catch_state_processing)
    training_step.add_catch(catch_state_processing)

    # Create the Workflow
    workflow_graph = Chain(
        [processing_step, training_step, processing_evaluation_step])
    training_pipeline = Workflow(
        name=training_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )

    # dump YAML cloud formation template
    yml = training_pipeline.get_cloudformation_template()

    if (dump_yaml_file is not None):
        with open(dump_yaml_file, 'w') as fout:
            fout.write(yml)

    if (return_yaml):
        return yml
    else:
        return training_pipeline


def example_define_training_pipeline():
    """
    An example on obtaining YAML CF template from the training pipeline definition
    """
    sm_role = "${SagerMakerRoleArn}"
    workflow_execution_role = "${WorkflowExecutionRoleArn}"
    training_pipeline_name = "${TrainingPipelineName}"
    yaml_rep = define_training_pipeline(sm_role=sm_role,
                                        workflow_execution_role=workflow_execution_role,
                                        training_pipeline_name=training_pipeline_name,
                                        dump_yaml_file=None)
    with open('/tmp/my_training_pipeline.yaml', 'w') as fout:
        fout.write(yaml_rep)


def example_execute_training_pipeline(region='us-east-1'):
    """
    execute the Workflow, which consists of four steps:

    1. Define job names for pre-processing, training, and evaluation
    2. Upload source code for pre-processing, training, and evaluation
    3. Define URLs for the input, output, and intermediary data
    4. Execute the workflow with populated parameters, and monitor the progress
    5. Inspect the evaluation result when the execution is completed
    """
    sm_role = 'arn:aws:iam::671846148176:role/service-role/AmazonSageMaker-ExecutionRole-20200419T120196'
    workflow_execution_role = 'arn:aws:iam::671846148176:role/StepFunctionsWorkflowExecutionRole'
    training_pipeline_name = 'MlMax-Training-Pipeline-Demo-dev'
    training_pipeline = define_training_pipeline(sm_role=sm_role,
                                                 workflow_execution_role=workflow_execution_role,
                                                 training_pipeline_name=training_pipeline_name,
                                                 return_yaml=False)

    smarn = training_pipeline.create()
    print(f'ARN of the stepfunction pipeline is {smarn}')

    # Step 1 - Generate unique names for Pre-Processing Job, Training Job, and
    training_job_name = f"scikit-learn-training-{uuid.uuid1().hex}"
    preprocessing_job_name = f"scikit-learn-sm-preprocessing-{uuid.uuid1().hex}"
    evaluation_job_name = f"scikit-learn-sm-evaluation-{uuid.uuid1().hex}"

    # Step 2 - Upload source code (pre-processing, evaluation, and train) to sagemaker
    PREPROCESSING_SCRIPT_LOCATION = "preprocessing.py"
    MODELEVALUATION_SCRIPT_LOCATION = "evaluation.py"
    MODELTRAINING_SCRIPT_LOCATION = 'train.py'

    sagemaker_session = sagemaker.Session()

    # To do: parameterize this in case running AWS CLI in a different region to the step function deploy region.

    #region = sagemaker_session.boto_region_name
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix="data/sklearn_processing/code",
    )
    input_evaluation_code = sagemaker_session.upload_data(
        MODELEVALUATION_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix="data/sklearn_processing/code",
    )
    s3_bucket_base_uri = f"s3://{sagemaker_session.default_bucket()}"
    sm_submit_dir_url = f"{s3_bucket_base_uri}/{training_job_name}/source/sourcedir.tar.gz"
    tar = tarfile.open('/tmp/sourcedir.tar.gz', "w:gz")
    # TODO need to add directory if source_dir is specified.
    tar.add(MODELTRAINING_SCRIPT_LOCATION)
    tar.close()
    sagemaker_session.upload_data(
        '/tmp/sourcedir.tar.gz',
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{training_job_name}/source",
    )

    # Step 3 - Define data URLs, preprocessed data URLs can be made specifically to this training job
    input_data = f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    output_data = f"{s3_bucket_base_uri}/data/sklearn_processing/output"
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"

    # Step 4 - Execute workflow
    print(f'Training Job Name is {training_job_name}')
    execution = training_pipeline.execute(
        inputs={
            "InputDataURL": input_data,
            # Each pre processing job (SageMaker processing job) requires a unique name,
            "PreprocessingJobName": preprocessing_job_name,
            "PreprocessingCodeURL": input_preprocessing_code,
            # Each Sagemaker Training job requires a unique name,
            "TrainingJobName": training_job_name,
            "SMSubmitDirURL": sm_submit_dir_url,
            "SMRegion": region,
            # Each SageMaker processing job requires a unique name,
            "EvaluationProcessingJobName": evaluation_job_name,
            "EvaluationCodeURL": input_evaluation_code,
            "EvaluationResultURL": f"{s3_bucket_base_uri}/{training_job_name}/evaluation",
            "PreprocessedTrainDataURL": preprocessed_training_data,
            "PreprocessedTestDataURL": preprocessed_test_data,
            "SMOutputDataURL": f"{s3_bucket_base_uri}/",
            "SMDebugOutputURL": f"{s3_bucket_base_uri}/"
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()

    # Step 5 - Inspect the output of the Workflow execution
    workflow_execution_output_json = execution.get_output(wait=True)
    from sagemaker.s3 import S3Downloader
    import json

    evaluation_output_config = workflow_execution_output_json["ProcessingOutputConfig"]
    for output in evaluation_output_config["Outputs"]:
        if output["OutputName"] == "evaluation":
            evaluation_s3_uri = "{}/{}".format(
                output["S3Output"]["S3Uri"], "evaluation.json")
            break

    evaluation_output = S3Downloader.read_file(evaluation_s3_uri)
    evaluation_output_dict = json.loads(evaluation_output)
    print(json.dumps(evaluation_output_dict, sort_keys=True, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--example', '-e', type=str, default='define')
    args, _ = parser.parse_known_args()
    action = args.example.lower()

    if 'define' == action:
        example_define_training_pipeline()
    elif 'execute' == action:
        example_execute_training_pipeline()
    else:
        print("--example should be either 'define' or 'execute' ")
