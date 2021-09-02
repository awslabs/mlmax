import datatest as dt
import pytest
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import ScriptProcessor

# These tests are skipped unless pytest is run with the `--smlocal` flag.


# For local training a dummy role will be sufficient
ROLE = "arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001"
IMAGE_URI = "342474125894.dkr.ecr.ap-southeast-1.amazonaws.com/mlmax-processing-monitor:latest"


@pytest.fixture()
def processor():
    processor = ScriptProcessor(
        image_uri=IMAGE_URI,
        command=["python3"],
        instance_type="local",
        instance_count=1,
        role=ROLE,
    )
    return processor


@dt.working_directory(__file__)
@pytest.mark.smlocal
def test_preprocessing_script_in_local_container(processor):
    code_path = "../../src/mlmax/monitoring.py"
    execution_mode = "train"  # Configure to either 'train', or 'infer'
    input_data_path = "input/census-income.csv"

    processor.run(
        code=code_path,
        inputs=[
            ProcessingInput(
                source="s3://wy-cba/census-income.csv", destination="/opt/ml/processing/input"
            )
        ],
        outputs=[
            ProcessingOutput(source="/opt/ml/processing/profiling", output_name="profiling",),
        ],
        arguments=["--mode", execution_mode, "--data_input", input_data_path],
        wait=False,
    )
