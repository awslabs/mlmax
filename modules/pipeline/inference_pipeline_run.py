import argparse
import configparser
import uuid

import boto3
import sagemaker
from stepfunctions.steps import Chain
from stepfunctions.workflow import Workflow


def get_existing_inference_pipeline(workflow_arn):
    """
    Create a dummy implementation to get existing training pipeline

    TODO: This could be a good PR for the SDK.
    """
    inference_pipeline = Workflow(
        name="inference_pipeline_name",
        definition=Chain([]),
        role="workflow_execution_role",
    )

    return inference_pipeline.attach(workflow_arn)


def get_latest_models():
    client = boto3.client("sagemaker")

    # Get the preprocessing model
    response = client.list_processing_jobs(
        NameContains="scikit-learn-sm-preprocessing",
        StatusEquals="Completed",
        SortBy="CreationTime",
        SortOrder="Descending",
    )
    processing_job_name = response["ProcessingJobSummaries"][0]["ProcessingJobName"]
    proc_model_s3 = (
        client.describe_processing_job(ProcessingJobName=processing_job_name)[
            "ProcessingOutputConfig"
        ]["Outputs"][2]["S3Output"]["S3Uri"]
        + "/proc_model.tar.gz"
    )
    # Get the trained sklearn model
    response = client.list_training_jobs(
        NameContains="scikit-learn-training",
        StatusEquals="Completed",
        SortBy="CreationTime",
        SortOrder="Descending",
    )
    training_job_name = response["TrainingJobSummaries"][0]["TrainingJobName"]
    model_s3 = client.describe_training_job(TrainingJobName=training_job_name)[
        "ModelArtifacts"
    ]["S3ModelArtifacts"]
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

    # Step 1 - Generate unique names for Pre-Processing Job, Training Job
    # (Batch Transform)
    unique_id = uuid.uuid1().hex
    preprocessing_job_name = f"sklearn-sm-preprocessing-{unique_id}"
    inference_job_name = f"sklearn-sm-inference-{unique_id}"

    # Step 2 - Upload source code (pre-processing, inference) to S3
    PREPROCESSING_SCRIPT_LOCATION = "../../src/mlmax/preprocessing.py"
    INFERENCE_SCRIPT_LOCATION = "../../src/mlmax/inference.py"

    sagemaker_session = sagemaker.Session()
    s3_bucket_base_uri = f"s3://{sagemaker_session.default_bucket()}"
    # upload preprocessing script
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{preprocessing_job_name}/source",
    )
    print(f"Using preprocessing script from {input_preprocessing_code}")
    # upload inference script
    input_inference_code = sagemaker_session.upload_data(
        INFERENCE_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{inference_job_name}/source",
    )

    # Step 3 - Get the lastest preprocessing and ml models
    # TODO: allow user to pass this as optional input
    proc_model_s3, model_s3 = get_latest_models()
    print(f"Using proc_model_s3: {proc_model_s3}")
    print(f"Using model_s3: {model_s3}")

    # Step 4 - Define data URLs, preprocessed data URLs can
    # be made specifically to this training job
    sagemaker_session = sagemaker.Session()

    input_data = (
        f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    )

    s3_bucket_base_uri = "{}{}".format("s3://", sagemaker_session.default_bucket())
    output_data = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output"
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"

    # Step 5 - Execute workflow
    print(f"Preprocessing Job Name is {preprocessing_job_name}")
    print(f"Inference Job Name is {inference_job_name}")
    execution = inference_pipeline.execute(
        inputs={
            "InputDataURL": input_data,
            "PreprocessingJobName": preprocessing_job_name,
            "InferenceJobName": inference_job_name,
            "ProcModelS3": proc_model_s3,
            "PreprocessingCodeURL": input_preprocessing_code,
            "InferenceCodeURL": input_inference_code,
            "ModelS3": model_s3,
            "PreprocessedTrainDataURL": preprocessed_training_data,
            "PreprocessedTestDataURL": preprocessed_test_data,
            "OutputPathURL": f"{s3_bucket_base_uri}/{inference_job_name}/output",
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()


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
    inference_pipeline_name = config["default"]["PipelineName"] + "-Inference"
    target_env = config["default"]["TargetEnv"]
    stack_name = (
        config["default"]["PipelineName"] + "-" + config["default"]["TargetEnv"]
    )
    workflow_arn = (
        f"arn:aws:states:{region}:{account}:"
        f"stateMachine:{inference_pipeline_name}-{target_env}"
    )
    print(f"State Machine Name is {inference_pipeline_name}-{target_env}")

    example_run_inference_pipeline(workflow_arn, region)
