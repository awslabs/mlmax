import argparse
import configparser
import tarfile
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
    # pipeline_job_name = f"pipeline-job-{unique_id}"
    training_job_name = f"scikit-learn-training-{unique_id}"
    preprocessing_job_name = f"scikit-learn-sm-preprocessing-{unique_id}"
    evaluation_job_name = f"scikit-learn-sm-evaluation-{unique_id}"

    # Step 2 - Upload source code (pre-processing, evaluation, and train) to sagemaker
    PREPROCESSING_SCRIPT_LOCATION = "../../src/mlmax/preprocessing.py"
    EVALUATION_SCRIPT_LOCATION = "../../src/mlmax/evaluation.py"
    TRAINING_SCRIPT_LOCATION = "../../src/mlmax/train.py"

    sagemaker_session = sagemaker.Session()
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{preprocessing_job_name}/source",
    )
    input_evaluation_code = sagemaker_session.upload_data(
        EVALUATION_SCRIPT_LOCATION,
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{evaluation_job_name}/source",
    )
    s3_bucket_base_uri = f"s3://{sagemaker_session.default_bucket()}"
    sm_submit_dir_url = (
        f"{s3_bucket_base_uri}/{training_job_name}/source/sourcedir.tar.gz"
    )
    tar = tarfile.open("/tmp/sourcedir.tar.gz", "w:gz")
    # TODO need to add directory if source_dir is specified.
    tar.add(TRAINING_SCRIPT_LOCATION, arcname="train.py")
    tar.close()
    sagemaker_session.upload_data(
        "/tmp/sourcedir.tar.gz",
        bucket=sagemaker_session.default_bucket(),
        key_prefix=f"{training_job_name}/source",
    )

    # Step 3 - Define data URLs, preprocessed data URLs can be made
    # specifically to this training job
    input_data = (
        f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    )
    output_data = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output"
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"
    preprocessed_model_url = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output"
    # Step 4 - Execute workflow
    print(f"Training Job Name is {training_job_name}")
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
            "EvaluationResultURL": (
                f"{s3_bucket_base_uri}/{training_job_name}/evaluation"
            ),
            "PreprocessedTrainDataURL": preprocessed_training_data,
            "PreprocessedTestDataURL": preprocessed_test_data,
            "PreprocessedModelURL": preprocessed_model_url,
            "SMOutputDataURL": f"{s3_bucket_base_uri}/",
            "SMDebugOutputURL": f"{s3_bucket_base_uri}/",
        }
    )
    execution.get_output(wait=True)
    execution.render_progress()

    # Step 5 - Inspect the output of the Workflow execution
    workflow_execution_output_json = execution.get_output(wait=True)
    import json

    from sagemaker.s3 import S3Downloader

    evaluation_output_config = workflow_execution_output_json["ProcessingOutputConfig"]
    for output in evaluation_output_config["Outputs"]:
        if output["OutputName"] == "evaluation":
            evaluation_s3_uri = "{}/{}".format(
                output["S3Output"]["S3Uri"], "evaluation.json"
            )
            break

    evaluation_output = S3Downloader.read_file(evaluation_s3_uri)
    evaluation_output_dict = json.loads(evaluation_output)
    print(json.dumps(evaluation_output_dict, sort_keys=True, indent=4))


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
