import argparse
import configparser
import uuid

import boto3
import sagemaker
from stepfunctions.steps import Chain
from stepfunctions.workflow import Workflow


def get_existing_training_pipeline(workflow_arn):
    """
    Create a dummpy implementation of get existing training pipeline
    """
    training_pipeline = Workflow(
        name="training_pipeline_name",
        definition=Chain([]),
        role="workflow_execution_role",
    )

    return training_pipeline.attach(workflow_arn)


def example_run_training_pipeline(workflow_arn, region):
    """
    execute the Workflow, which consists of four steps:

    1. Define job names for pre-processing, training, and evaluation
    2. Upload source code for pre-processing, training, and evaluation
    3. Define URLs for the input, output, and intermediary data
    4. Execute the workflow with populated parameters, and monitor the progress
    5. Inspect the evaluation result when the execution is completed
    """

    training_pipeline = get_existing_training_pipeline(workflow_arn)

    # Step 1 - Generate unique names for Pre-Processing Job, Training Job, and
    unique_id = uuid.uuid1().hex
    preprocessing_job_name = f"pyspark-sm-preprocessing-{unique_id}"

    # Step 2 - Upload source code (pre-processing, evaluation, and train) to sagemaker
    PREPROCESSING_SCRIPT_LOCATION = "src/preprocessing.py"

    sagemaker_session = sagemaker.Session()
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{preprocessing_job_name}/source",
    )
    s3_bucket_base_uri = f"s3://{sagemaker_session.default_bucket()}"

    # Step 3 - Define data URLs, preprocessed data URLs can be made
    input_data = "s3://ml-proserve-nyc-taxi-data/manifest/taxi.manifest"
    output_data = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output"
    preprocessed_training_data = f"{output_data}/train_data"
    execution = training_pipeline.execute(
        inputs={
            "InputDataURL": input_data,
            # Each preprocessing job (SageMaker) requires a unique name,
            "PreprocessingJobName": preprocessing_job_name,
            "PreprocessingCodeURL": input_preprocessing_code,
            "PreprocessedTrainDataURL": preprocessed_training_data,
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()

    # Step 5 - Inspect the output of the Workflow execution
    workflow_execution_output_json = execution.get_output(wait=True)

    # print(f"output: {json.dumps(workflow_execution_output_json)}")
    print(f"output: {workflow_execution_output_json}")


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
    training_pipeline_name = config["default"]["PipelineName"] + "-Training"
    target_env = config["default"]["TargetEnv"]
    workflow_arn = (
        f"arn:aws:states:{region}:{account}:"
        f"stateMachine:{training_pipeline_name}-{target_env}"
    )
    print(f"State Machine Name is {training_pipeline_name}-{target_env}")
    example_run_training_pipeline(workflow_arn, region)
