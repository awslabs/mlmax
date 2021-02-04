"""
Test SKLearnProcessor on local/sagemaker

Prerequisite:
- Update role
- Update S3 output directory

"""
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
import sagemaker

sagemaker_session = sagemaker.session.Session()
role = "arn:aws:iam::342474125894:role/service-role/AmazonSageMaker-ExecutionRole-20190405T234154"

# processing step for feature engineering
sklearn_processor = SKLearnProcessor(
    framework_version="0.23-1",
    # instance_type="ml.m5.xlarge",
    instance_type="local",
    instance_count=1,
    # base_job_name=f"sklearn-preprocess",
    sagemaker_session=sagemaker_session,
    role=role,
)

sklearn_processor.run(
    code="src/project/preprocess.py",
    # inputs=[
    #     ProcessingInput(source="s3://your-bucket/path/to/your/data", destination="/opt/ml/processing/input"),
    # ],
    outputs=[
        ProcessingOutput(
            # Output_name is only useful when destination is not specified
            # output_name="train",
            source="/opt/ml/processing/train",
            # Specify dest if want to access a copy in S3
            # s3://wy-project-template/processed/train
            destination="s3://wy-project-template/processed/train",
        ),
        # Appear in default bucket without "destination":
        # s3://sagemaker-ap-southeast-1-342474125894/project1/sklearn-preprocess-2021-01-07-03-51-14-400/output/validation
        ProcessingOutput(
            source="/opt/ml/processing/validation",
            destination="s3://wy-project-template/processed/validation",
        ),
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination="s3://wy-project-template/processed/test",
        ),
    ],
    arguments=["--input-data", "s3://sparkml-mleap/data/abalone/abalone.csv"],
)

# preprocessing_job_description = sklearn_processor.jobs[-1].describe()
