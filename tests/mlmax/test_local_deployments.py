import datatest as dt
import pytest
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.processing import SKLearnProcessor

# These tests are skipped unless pytest is run with the `--smlocal` flag.
# These tests will be run in Python inspect mode if pytest is run with the
# `--smlocal --inspectlocal` flags.

# For local training a dummy role will be sufficient
role = "arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20200101T000001"


@pytest.fixture()
def processor(inspectlocal):
    processor = SKLearnProcessor(
        framework_version="0.20.0",
        instance_count=1,
        instance_type="local",
        role=role,
        max_runtime_in_seconds=1200,
        env={"PYTHONINSPECT": "1"} if inspectlocal else None,
    )
    return processor


@dt.working_directory(__file__)
@pytest.mark.smlocal
def test_preprocessing_script_in_local_container(processor):
    code_path = "../../src/mlmax/preprocessing.py"
    execution_mode = "tr ain"  # Configure to either 'train', or 'infer'
    input_data_path = "input/census-income-sample.csv"
    local_data_path = "opt/ml/processing/input"

    processor.run(
        code=code_path,
        inputs=[
            ProcessingInput(
                source=local_data_path, destination="/opt/ml/processing/input"
            )
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/train", output_name="train_data",
            ),
            ProcessingOutput(
                source="/opt/ml/processing/test", output_name="test_data",
            ),
            ProcessingOutput(
                source="/opt/ml/processing/model", output_name="proc_model",
            ),
        ],
        arguments=[
            "--train-test-split-ratio",
            "0.2",
            "--mode",
            execution_mode,
            "--data-input",
            input_data_path,
        ],
        wait=False,
    )


@dt.working_directory(__file__)
@pytest.mark.smlocal
def test_training_script_in_local_container(inspectlocal):
    code_path = "../../src/mlmax/train.py"
    train_data_path = "opt/ml/processing/train/"
    test_data_path = "opt/ml/processing/test/"

    sklearn = SKLearn(
        entry_point=code_path,
        role=role,
        py_version="py3",
        framework_version="0.20.0",
        instance_type="local",
        hyperparameters={"inspect": True if inspectlocal else None},
    )
    sklearn.fit(
        {"train": "file://" + train_data_path, "test": "file://" + test_data_path},
        wait=True,
    )


@dt.working_directory(__file__)
@pytest.mark.smlocal
def test_inference_script_in_local_container(processor):
    code_path = "../../src/mlmax/inference.py"
    local_data_path = "opt/ml/processing/input"
    model_path = "opt/ml/processing/model"

    processor.run(
        code=code_path,
        inputs=[
            ProcessingInput(
                source=local_data_path,
                destination="/opt/ml/processing/input",
                input_name="input",
            ),
            ProcessingInput(
                source=model_path,
                destination="/opt/ml/processing/model",
                input_name="model",
            ),
        ],
        outputs=[
            ProcessingOutput(source="/opt/ml/processing/test", output_name="test_data",)
        ],
        wait=False,
    )


@dt.working_directory(__file__)
@pytest.mark.smlocal
def test_evaluation_script_in_local_container(processor):
    code_path = "../../src/mlmax/evaluation.py"
    local_data_path = "opt/ml/processing/test"
    model_path = "opt/ml/processing/model"

    processor.run(
        code=code_path,
        inputs=[
            ProcessingInput(
                source=local_data_path,
                destination="/opt/ml/processing/test",
                input_name="input",
            ),
            ProcessingInput(
                source=model_path,
                destination="/opt/ml/processing/model",
                input_name="model",
            ),
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/evaluation", output_name="evaluation",
            )
        ],
        wait=False,
    )
