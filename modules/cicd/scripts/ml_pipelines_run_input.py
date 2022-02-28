import json
import os
import tarfile
import uuid

import boto3
import sagemaker


def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_from_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def generate_training_pipeline_input(bucket):

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
        bucket=bucket,
        key_prefix=f"{preprocessing_job_name}/source",
    )
    input_evaluation_code = sagemaker_session.upload_data(
        EVALUATION_SCRIPT_LOCATION,
        bucket=bucket,
        key_prefix=f"{evaluation_job_name}/source",
    )
    s3_bucket_base_uri = f"s3://{bucket}"
    sm_submit_dir_url = (
        f"{s3_bucket_base_uri}/{training_job_name}/source/sourcedir.tar.gz"
    )
    tar = tarfile.open("/tmp/sourcedir.tar.gz", "w:gz")
    # TODO need to add directory if source_dir is specified.
    tar.add(TRAINING_SCRIPT_LOCATION, arcname="train.py")
    tar.close()
    sagemaker_session.upload_data(
        "/tmp/sourcedir.tar.gz",
        bucket=bucket,
        key_prefix=f"{training_job_name}/source",
    )

    # Step 3 - Define data URLs, preprocessed data URLs can be made
    # specifically to this training job
    input_data = (
        f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    )
    output_data = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output_data"
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"
    preprocessed_model_url = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output"

    # Step 4 - save the json input file.
    print(f"Training Job Name is {training_job_name}")
    inputs = {
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
        "EvaluationResultURL": (f"{s3_bucket_base_uri}/{training_job_name}/evaluation"),
        "PreprocessedTrainDataURL": preprocessed_training_data,
        "PreprocessedTestDataURL": preprocessed_test_data,
        "PreprocessedModelURL": preprocessed_model_url,
        "SMOutputDataURL": f"{s3_bucket_base_uri}/",
        "SMDebugOutputURL": f"{s3_bucket_base_uri}/",
    }
    save_to_json(inputs, "config/training-pipeline-input.json")
    return (
        f"{s3_bucket_base_uri}/{preprocessing_job_name}/output/proc_model.tar.gz",
        f"{s3_bucket_base_uri}/{training_job_name}/output/model.tar.gz",
    )


def generate_inference_pipeline_input(proc_model_s3, model_s3, bucket):

    # Step 1 - Generate unique names for Pre-Processing Job, Training Job
    unique_id = uuid.uuid1().hex
    preprocessing_job_name = f"sklearn-sm-preprocessing-{unique_id}"
    inference_job_name = f"sklearn-sm-inference-{unique_id}"

    # Step 2 - Upload source code (pre-processing, inference) to S3
    PREPROCESSING_SCRIPT_LOCATION = "../../src/mlmax/preprocessing.py"
    INFERENCE_SCRIPT_LOCATION = "../../src/mlmax/inference.py"

    sagemaker_session = sagemaker.Session()
    s3_bucket_base_uri = f"s3://{bucket}"
    # upload preprocessing script
    input_preprocessing_code = sagemaker_session.upload_data(
        PREPROCESSING_SCRIPT_LOCATION,
        bucket=bucket,
        key_prefix=f"{preprocessing_job_name}/source",
    )
    print(f"Using preprocessing script from {input_preprocessing_code}")
    # upload inference script
    input_inference_code = sagemaker_session.upload_data(
        INFERENCE_SCRIPT_LOCATION,
        bucket=bucket,
        key_prefix=f"{inference_job_name}/source",
    )

    # Step 3 - Get the lastest preprocessing and ml models
    print(f"Using proc_model_s3: {proc_model_s3}")
    print(f"Using model_s3: {model_s3}")

    # Step 4 - Define data URLs, preprocessed data URLs can
    # be made specifically to this training job
    sagemaker_session = sagemaker.Session()

    input_data = (
        f"s3://sagemaker-sample-data-{region}/processing/census/census-income.csv"
    )

    s3_bucket_base_uri = "{}{}".format("s3://", bucket)
    output_data = f"{s3_bucket_base_uri}/{preprocessing_job_name}/output_data"
    preprocessed_training_data = f"{output_data}/train_data"
    preprocessed_test_data = f"{output_data}/test_data"

    # Step 5 - save the json input file.
    print(f"Preprocessing Job Name is {preprocessing_job_name}")
    print(f"Inference Job Name is {inference_job_name}")
    inputs = {
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
    save_to_json(inputs, "config/inference-pipeline-input.json")
    return inputs


if __name__ == "__main__":
    sts = boto3.client("sts")
    account = sts.get_caller_identity().get("Account")
    region = sts.meta.region_name
    # get package bucket from environment variable
    package_bucket = os.getenv("PACKAGE_BUCKET")

    # generate the input json for training and inference pipelines
    proc_model_s3, model_s3 = generate_training_pipeline_input(package_bucket)
    inputs_inference = generate_inference_pipeline_input(
        proc_model_s3, model_s3, package_bucket
    )

    # generate prod cloudformation template configuration
    config_stage = read_from_json(f"config/deploy-{region}-stage.json")
    config_stage["Parameters"]["PackageBucket"] = package_bucket
    for key, value in inputs_inference.items():
        if key not in ["PreprocessingJobName", "InferenceJobName"]:
            config_stage["Parameters"][key] = value
    save_to_json(config_stage, f"config/deploy-{region}-stage-build.json")
    config_prod = read_from_json(f"config/deploy-{region}-prod.json")
    config_prod["Parameters"]["PackageBucket"] = package_bucket
    for key, value in inputs_inference.items():
        if key not in ["PreprocessingJobName", "InferenceJobName"]:
            config_prod["Parameters"][key] = value
    save_to_json(config_prod, f"config/deploy-{region}-prod-build.json")
