import argparse
import configparser
import uuid

import boto3
import sagemaker
from stepfunctions.steps import Chain
from stepfunctions.workflow import Workflow


def get_existing_monitor_pipeline(workflow_arn):
    """
    Create a dummpy implementation of get existing data pipeline
    """
    data_pipeline = Workflow(
        name="data_pipeline_name", definition=Chain([]), role="workflow_execution_role",
    )

    return data_pipeline.attach(workflow_arn)


def example_run_monitor_pipeline(workflow_arn, region, config):
    """
    execute the Workflow, which consists of four steps:

    1. Define job names for pre-processing, data, and evaluation
    2. Upload source code for pre-processing, data, and evaluation
    3. Define URLs for the input, output, and intermediary data
    4. Execute the workflow with populated parameters, and monitor the progress
    5. Inspect the evaluation result when the execution is completed
    """

    data_pipeline = get_existing_monitor_pipeline(workflow_arn)

    # Step 1 - Generate unique names for all SageMaker Jobs
    unique_id = uuid.uuid1().hex
    preprocessing_job_name = f"monitor-sm-preprocessing-{unique_id}"
    preprocessing_infer_job_name = f"monitor-sm-preprocessing-infer-{unique_id}"

    # Step 2 - Upload all source code to s3
    PREPROCESSING_SCRIPT_LOCATION = "../../src/mlmax/monitoring.py"

    sagemaker_session = sagemaker.Session()
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{preprocessing_job_name}/source",
    )

    # Step 3 - Define data URLs, preprocessed data URLs can be made
    # input_data = "s3://ml-proserve-nyc-taxi-data/manifest/taxi.manifest"
    input_data = config["default"]["InputSource"]
    infer_data = config["default"]["InferSource"]
    s3_monitor_bucket = config["default"]["MonitorS3Bucket"]
    s3_monitor_prefix = config["default"]["MonitorS3Prefix"]
    print("InputSource:", input_data)
    print("InferSource:", infer_data)
    print("MonitorS3Bucket:", s3_monitor_bucket)
    print("MonitorS3Prefix:", s3_monitor_prefix)
    print("InputProcessingcode", input_preprocessing_code)

    train_output_data = f"s3://{s3_monitor_bucket}/{s3_monitor_prefix}/"
    infer_output_data = f"s3://{s3_monitor_bucket}/{s3_monitor_prefix}/inference"
    execution = data_pipeline.execute(
        inputs={
            "PreprocessingJobName": preprocessing_job_name,
            "PreprocessingInferJobName": preprocessing_infer_job_name,
            "PreprocessingCodeURL": input_preprocessing_code,
            "InputDataURL": input_data,
            "InferDataURL": infer_data,
            "MonitorTrainOutputURL": train_output_data,
            "MonitorInferOutputURL": infer_output_data,
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()

    # Step 5 - Inspect the output of the Workflow execution
    workflow_execution_output_json = execution.get_output(wait=True)

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
    data_pipeline_name = config["default"]["PipelineName"]
    target_env = config["default"]["TargetEnv"]
    workflow_arn = (
        f"arn:aws:states:{region}:{account}:"
        f"stateMachine:{data_pipeline_name}-{target_env}"
    )
    print(f"State Machine Name is {data_pipeline_name}-{target_env}")
    example_run_monitor_pipeline(workflow_arn, region, config)
