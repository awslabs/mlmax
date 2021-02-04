"""
Create and execute pipeline.

Prerequisite:
- Update project info
    model_package_group_name = "ModelPackageGroup"
    pipeline_name = "PyTorchPipeline"
    project_name = "project"

- Update role

- Update configurable parameters
    ProcessingInstanceType

"""
import os

import boto3
import sagemaker
import sagemaker.session
from sagemaker.inputs import TrainingInput
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.pytorch import PyTorch
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.workflow.condition_step import ConditionStep, JsonGet
from sagemaker.workflow.conditions import ConditionLessThanOrEqualTo
from sagemaker.workflow.parameters import ParameterInteger, ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.steps import ProcessingStep, TrainingStep

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


def get_session(region, default_bucket):
    """Gets the sagemaker session based on the region.

    Args:
        region: the aws region to start the session
        default_bucket: the bucket to use for storing the artifacts

    Returns:
        `sagemaker.session.Session instance
    """

    boto_session = boto3.Session(region_name=region)

    sagemaker_client = boto_session.client("sagemaker")
    runtime_client = boto_session.client("sagemaker-runtime")
    return sagemaker.session.Session(
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        sagemaker_runtime_client=runtime_client,
        default_bucket=default_bucket,
    )


def get_pipeline(
    region,
    role=None,
    default_bucket=None,
    model_package_group_name="ModelPackageGroup",
    pipeline_name="ModelPipeline",
    base_job_prefix="project",
):
    """Gets a SageMaker ML Pipeline instance working with data.

    Args:
        region: AWS region to create and run the pipeline.
        role: IAM role to create and run steps and pipeline.
        default_bucket: the bucket to use for storing the artifacts

    Returns:
        an instance of a pipeline
    """
    sagemaker_session = get_session(region, default_bucket)
    if role is None:
        role = sagemaker.session.get_execution_role(sagemaker_session)

    # parameters for pipeline execution (placeholder, can be updated during execution)
    processing_instance_count = ParameterInteger(name="ProcessingInstanceCount", default_value=1)
    processing_instance_type = ParameterString(name="ProcessingInstanceType", default_value="ml.m5.xlarge")
    training_instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m5.xlarge")
    model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="Approved")
    # TODO: Bucket name to be configurable

    input_data = ParameterString(
        name="InputDataUrl",
        default_value="s3://wy-project-template/data/abalone-dataset.csv",
    )

    # processing step for feature engineering
    sklearn_processor = SKLearnProcessor(
        framework_version="0.23-1",
        instance_type=processing_instance_type,
        instance_count=processing_instance_count,
        base_job_name=f"{base_job_prefix}/sklearn-preprocess",
        sagemaker_session=sagemaker_session,
        role=role,
    )
    step_process = ProcessingStep(
        name="PreprocessData",
        processor=sklearn_processor,
        outputs=[
            ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/train",
                destination="s3://wy-project-template/processed/train",
            ),
            ProcessingOutput(
                output_name="validation",
                source="/opt/ml/processing/validation",
                destination="s3://wy-project-template/processed/validation",
            ),
            ProcessingOutput(
                output_name="test",
                source="/opt/ml/processing/test",
                destination="s3://wy-project-template/processed/test",
            ),
        ],
        code=os.path.join(BASE_DIR, "preprocess.py"),
        # Provide argument if script support it
        job_arguments=["--input-data", input_data],
    )

    # training step for generating model artifacts
    pytorch_est = PyTorch(
        entry_point="train.py",
        source_dir=f"{BASE_DIR}",
        role=role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        framework_version="1.6.0",
        py_version="py3",
        hyperparameters={"epochs": 10, "batch-size": 128, "lr": 0.1},
    )
    step_train = TrainingStep(
        name="TrainModel",
        estimator=pytorch_est,
        inputs={
            "train": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
                content_type="text/csv",
            ),
            "validation": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs["validation"].S3Output.S3Uri,
                content_type="text/csv",
            ),
        },
    )

    # processing step for evaluation
    image_uri = sagemaker.image_uris.retrieve(
        framework="pytorch",
        region=region,
        version="1.5.0",
        py_version="py3",
        instance_type="ml.m5.xlarge",
        accelerator_type=None,
        image_scope="training",
    )
    script_eval = ScriptProcessor(
        image_uri=image_uri,
        command=["python3"],
        instance_type=processing_instance_type,
        instance_count=1,
        base_job_name=f"{base_job_prefix}/script-eval",
        sagemaker_session=sagemaker_session,
        role=role,
    )
    evaluation_report = PropertyFile(
        name="EvaluationReport",
        # The name of the processing job output channel, must exist in processor "output_name"
        output_name="evaluation",
        path="evaluation.json",
    )
    step_eval = ProcessingStep(
        name="EvaluateModel",
        processor=script_eval,
        inputs=[
            ProcessingInput(
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=step_process.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(
                output_name="evaluation",
                source="/opt/ml/processing/evaluation",
                destination="s3://wy-project-template/evaluation",
            ),
        ],
        code=os.path.join(BASE_DIR, "evaluate.py"),
        property_files=[evaluation_report],
    )

    # register model step that will be conditionally executed
    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri="{}/evaluation.json".format(
                step_eval.arguments["ProcessingOutputConfig"]["Outputs"][0]["S3Output"]["S3Uri"]
            ),
            content_type="application/json",
        )
    )
    step_register = RegisterModel(
        name="RegisterModel",
        estimator=pytorch_est,
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=["ml.t2.medium", "ml.m5.large"],
        transform_instances=["ml.m5.large"],
        model_package_group_name=model_package_group_name,
        approval_status=model_approval_status,
        model_metrics=model_metrics,
    )

    # condition step for evaluating model quality and branching execution
    # It will parse the json in property file
    cond_lte = ConditionLessThanOrEqualTo(
        left=JsonGet(step=step_eval, property_file=evaluation_report, json_path="regression_metrics.rmse.value"),
        right=6.0,
    )
    # Register model if meet evaluation criteria
    step_cond = ConditionStep(
        name="CheckMSEEvaluation",
        conditions=[cond_lte],
        if_steps=[step_register],
        else_steps=[],
    )

    # Create Pipeline
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            processing_instance_type,
            processing_instance_count,
            training_instance_type,
            model_approval_status,
            input_data,
        ],
        steps=[step_process, step_train, step_eval, step_cond],
        sagemaker_session=sagemaker_session,
    )
    return pipeline


if __name__ == "__main__":
    region = boto3.Session().region_name
    # TODO: Use generic retrieval method
    role = sagemaker.get_execution_role()
    role = "arn:aws:iam::476245144988:role/service-role/AmazonSageMaker-ExecutionRole-20191204T094674"
    default_bucket = sagemaker.session.Session().default_bucket()

    # Change these to reflect your project/business name or if you want to separate ModelPackageGroup/Pipeline from the rest of your team
    model_package_group_name = "ModelPackageGroup"
    pipeline_name = "PyTorchPipeline"
    project_name = "project"
    print(region)
    print(role)
    print(default_bucket)

    pipeline = get_pipeline(
        region=region,
        role=role,
        default_bucket=default_bucket,
        model_package_group_name=model_package_group_name,
        pipeline_name=pipeline_name,
        base_job_prefix=project_name,
    )

    # Create pipeline
    pipeline.upsert(role_arn=role)

    # Execute pipeline
    execution = pipeline.start(
        parameters=dict(
            ProcessingInstanceType="ml.c5.xlarge",
            ModelApprovalStatus="Approved",
        )
    )
