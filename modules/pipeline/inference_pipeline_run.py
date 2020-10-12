import uuid
import tarfile
import argparse
import configparser

import boto3
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
from stepfunctions.workflow import Workflow

import sagemaker
from sagemaker import get_execution_role
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.s3 import S3Uploader
from sagemaker.sklearn.processing import SKLearnProcessor

from sagemaker.sklearn.model import SKLearnModel
from sagemaker.transformer import Transformer

def get_existing_inference_pipeline(workflow_arn):
    """
    Create a dummpy implementation of get existing training pipeline
    """
    inference_pipeline = Workflow(
        name="inference_pipeline_name",
        definition=Chain([]),
        role="workflow_execution_role",
    )

    return inference_pipeline.attach(workflow_arn)


def get_latest_models():
    client = boto3.client('sagemaker')

    # Get the preprocessing model
    response = client.list_processing_jobs(NameContains="scikit-learn-sm-preprocessing",
                                         StatusEquals="Completed",
                                         SortBy="CreationTime",
                                         SortOrder="Descending")
    processing_job_name = response['ProcessingJobSummaries'][0]['ProcessingJobName']
    proc_model_s3 = client.describe_processing_job(ProcessingJobName=processing_job_name)['ProcessingOutputConfig']['Outputs']\
                           [2]['S3Output']['S3Uri'] + '/proc_model.tar.gz'
    # Get the trained sklearn model
    response = client.list_training_jobs(NameContains="scikit-learn-training",
                                         StatusEquals="Completed",
                                         SortBy="CreationTime",
                                         SortOrder="Descending")
    training_job_name = response['TrainingJobSummaries'][0]['TrainingJobName']
    model_s3 = client.describe_training_job(TrainingJobName=training_job_name)['ModelArtifacts']['S3ModelArtifacts']
    return proc_model_s3, model_s3


def example_run_inference_pipeline(workflow_arn, region):
    """
    execute the Workflow, which consists of four steps:

    1. Define job names for pre-processing, training, and evaluation
    2. Upload source code for pre-processing, training, and evaluation
    3. Define URLs for the input, output, and intermediary data
    4. Execute the workflow with populated parameters, and monitor the progress
    5. Inspect the evaluation result when the execution is completed
    """
    inference_pipeline = get_existing_inference_pipeline(workflow_arn)

    # Ad hoc SageMaker Execution Role
    role = "arn:aws:iam::671846148176:role/service-role/AmazonSageMaker-ExecutionRole-20200419T120196"

    # Step 1 - Generate unique names for Pre-Processing Job, Training Job (Batch Transform)
    preprocessing_job_name = f"scikit-learn-sm-preprocessing-{uuid.uuid1().hex}"
    inference_job_name = f"scikit-learn-sm-inference-{uuid.uuid1().hex}"

    ## Step 2 - Upload source code (pre-processing, evaluation, and train) to sagemaker
    #PREPROCESSING_SCRIPT_LOCATION = "preprocessing.py"
    ##MODELEVALUATION_SCRIPT_LOCATION = "evaluation.py"
    ##MODELTRAINING_SCRIPT_LOCATION = "train.py"

    #sagemaker_session = sagemaker.Session()

    #input_preprocessing_code = sagemaker_session.upload_data(
    #    PREPROCESSING_SCRIPT_LOCATION,
    #    bucket=sagemaker_session.default_bucket(),
    #    key_prefix="data/sklearn_processing/code",
    #)
    #input_evaluation_code = sagemaker_session.upload_data(
    #    MODELEVALUATION_SCRIPT_LOCATION,
    #    bucket=sagemaker_session.default_bucket(),
    #    key_prefix="data/sklearn_processing/code",
    #)
    #s3_bucket_base_uri = f"s3://{sagemaker_session.default_bucket()}"
    #sm_submit_dir_url = (
    #    f"{s3_bucket_base_uri}/{training_job_name}/source/sourcedir.tar.gz"
    #)
    #tar = tarfile.open("/tmp/sourcedir.tar.gz", "w:gz")
    ## TODO need to add directory if source_dir is specified.
    #tar.add(MODELTRAINING_SCRIPT_LOCATION)
    #tar.close()
    #sagemaker_session.upload_data(
    #    "/tmp/sourcedir.tar.gz",
    #    bucket=sagemaker_session.default_bucket(),
    #    key_prefix=f"{training_job_name}/source",
    #)

    # Step 2 - Get the lastest preprocessing and ml models
    proc_model_s3, model_s3 = get_latest_models()

    # Step 3 - Define data URLs, preprocessed data URLs can be made specifically to this training job
    sagemaker_session = sagemaker.Session()

    input_data = (
        f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    )

    #input_code = sagemaker_session.upload_data(
    #    PREPROCESSING_SCRIPT_LOCATION,
    #    bucket=sagemaker_session.default_bucket(),
    #    key_prefix="data/sklearn_processing/code",
    #)

    s3_bucket_base_uri = "{}{}".format("s3://", sagemaker_session.default_bucket())
    output_data = "{}/{}".format(s3_bucket_base_uri, "data/sklearn_processing/output")
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"

    # To do: put this into step function
    proc_model = SKLearnModel(
        model_data=proc_model_s3,
        role=role,
        framework_version="0.20.0",
        entry_point="preprocessing.py",
    )

    transformer = proc_model.transformer(instance_count=1, instance_type="ml.c5.xlarge")

    proc_model_name = proc_model.name
    print(f"proc_model is {proc_model_name}")

    # To do: put this into step function
    model = SKLearnModel(
        model_data=model_s3,
        role=role,
        framework_version="0.20.0",
        entry_point="inference.py",
    )

    transformer = model.transformer(instance_count=1, instance_type="ml.c5.xlarge")

    model_name = model.name
    print(f"model name is {model_name}")

    # Step 4 - Execute workflow
    print(f"Preprocessing Job Name is {preprocessing_job_name}")
    print(f"Inference Job Name is {inference_job_name}")
    execution = inference_pipeline.execute(
        inputs={
            "InputDataURL": input_data,
            "PreprocessingJobName": preprocessing_job_name,
            # Each pre processing job (SageMaker processing job) requires a unique name,
            "BatchTransformJobName": inference_job_name,  # Each SageMaker processing job requires a unique name,
            "ModelName": model_name,
            "ProcModelName": proc_model_name,
            "PreprocessedTrainDataURL": preprocessed_training_data,
            "PreprocessedTestDataURL": preprocessed_test_data,
            "OutputPathURL": f"{s3_bucket_base_uri}/{model_name}",
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()

    ## Step 5 - Inspect the output of the Workflow execution
    #workflow_execution_output_json = execution.get_output(wait=True)
    #from sagemaker.s3 import S3Downloader
    #import json

    #evaluation_output_config = workflow_execution_output_json["ProcessingOutputConfig"]
    #for output in evaluation_output_config["Outputs"]:
    #    if output["OutputName"] == "evaluation":
    #        evaluation_s3_uri = "{}/{}".format(
    #            output["S3Output"]["S3Uri"], "evaluation.json"
    #        )
    #        break

    #evaluation_output = S3Downloader.read_file(evaluation_s3_uri)
    #evaluation_output_dict = json.loads(evaluation_output)
    #print(json.dumps(evaluation_output_dict, sort_keys=True, indent=4))


if __name__ == "__main__":
    sts = boto3.client("sts")
    account = sts.get_caller_identity().get("Account")
    region = sts.meta.region_name
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_env", "-e", type=str, default="dev")
    args, _ = parser.parse_known_args()
    config = configparser.ConfigParser()
    with open(f"config/deploy-{region}-{args.target_env}.ini") as f:
        config.read_string("[default]\n" + f.read())
    inference_pipeline_name = config["default"]["InferencePipelineName"]
    target_env = config["default"]["TargetEnv"]
    workflow_arn = (
        f"arn:aws:states:{region}:{account}:"
        f"stateMachine:{inference_pipeline_name}-{target_env}"
    )
    print(f"State Machine Name is {inference_pipeline_name}-{target_env}")
    example_run_inference_pipeline(workflow_arn, region)
