"""
Test SKLearnProcessor on local/sagemaker
"""
from sagemaker.sklearn.processing import ScriptProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
import sagemaker

sagemaker_session = sagemaker.session.Session()
role = "arn:aws:iam::342474125894:role/service-role/AmazonSageMaker-ExecutionRole-20190405T234154"
region = "ap-southeast-1"

image_uri = sagemaker.image_uris.retrieve(
    framework="pytorch",
    region=region,
    version="1.5.0",
    py_version="py3",
    instance_type="ml.m5.xlarge",
    accelerator_type=None,
    image_scope="training",
)

# Use a pytorch image because evaluation will load pytorch module
script_processor = ScriptProcessor(
    image_uri=image_uri,
    command=["python3"],
    instance_type="ml.m5.xlarge",
    instance_count=1,
    sagemaker_session=sagemaker_session,
    role=role,
)

script_processor.run(
    code="src/project/evaluate.py",
    inputs=[
        ProcessingInput(
            source="s3://sagemaker-ap-southeast-1-342474125894/pytorch-training-2021-01-16-06-26-06-283/output/model.tar.gz",
            destination="/opt/ml/processing/model",
        ),
        ProcessingInput(
            source="s3://wy-project-template/processed/test",
            destination="/opt/ml/processing/test",
        ),
    ],
    outputs=[
        ProcessingOutput(
            # default: s3://sagemaker-ap-southeast-1-342474125894/project1/script-eval-2021-01-07-05-35-18-302/output/evaluation/evaluation.json
            # output_name is used only when destination is not specified
            # output_name="evaluation",
            source="/opt/ml/processing/evaluation",
            #
            # To fix output location
            destination="s3://wy-project-template/evaluation",
        ),
    ],
)
