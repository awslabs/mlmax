import stepfunctions
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import Chain, ProcessingStep
from stepfunctions.workflow import Workflow


def define_inference_pipeline(
    sm_role,
    workflow_execution_role,
    inference_pipeline_name,
    return_yaml=True,
    dump_yaml_file="templates/sagemaker_inference_pipeline.yaml",
):
    """
    Return YAML definition of the training pipeline, which consists of multiple
    Amazon StepFunction steps

    sm_role:                    ARN of the SageMaker execution role
    workflow_execution_role:    ARN of the StepFunction execution role
    return_yaml:                Return YAML representation or not, if False,
                     it returns an instance of `stepfunctions.workflow.WorkflowObject`
    dump_yaml_file:  If not None, a YAML file will be generated at this file location

    """

    # Pass required parameters dynamically for each execution using placeholders.
    execution_input = ExecutionInput(
        schema={
            "InputDataURL": str,
            "PreprocessingJobName": str,
            "InferenceJobName": str,
            "ProcModelS3": str,
            "PreprocessingCodeURL": str,
            "InferenceCodeURL": str,
            "ModelS3": str,
            "PreprocessedTrainDataURL": str,
            "PreprocessedTestDataURL": str,
            "OutputPathURL": str,
        }
    )

    """
    Create Preprocessing Model from model artifact.
    """
    # sagemaker_session = sagemaker.Session()

    sklearn_processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=sm_role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=1200,
    )
    # Create ProcessingInputs and ProcessingOutputs objects for Inputs and
    # Outputs respectively for the SageMaker Processing Job
    inputs = [
        ProcessingInput(
            source=execution_input["InputDataURL"],
            destination="/opt/ml/processing/input",
            input_name="input-1",
        ),
        ProcessingInput(
            source=execution_input["PreprocessingCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
        ProcessingInput(
            source=execution_input["ProcModelS3"],
            destination="/opt/ml/processing/model",
            input_name="proc_model",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination=execution_input["PreprocessedTestDataURL"],
            output_name="test_data",
        ),
    ]

    processing_step = ProcessingStep(
        "SageMaker pre-processing step",
        processor=sklearn_processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--mode", "infer"],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/input/code/preprocessing.py",
        ],
    )

    """
    Create inference with sklearn processing step.

    Inputs are the preprocessed data S3 URL, the inference code S3 URL, and
    the model S3 URL. Output is the inferred data.
    """
    sklearn_processor2 = SKLearnProcessor(
        framework_version="0.20.0",
        role=sm_role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=1200,
    )
    inputs = [
        ProcessingInput(
            source=execution_input["PreprocessedTestDataURL"],
            destination="/opt/ml/processing/input",
            input_name="input-1",
        ),
        ProcessingInput(
            source=execution_input["InferenceCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
        ProcessingInput(
            source=execution_input["ModelS3"],
            destination="/opt/ml/processing/model",
            input_name="model",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination=execution_input["OutputPathURL"],
            output_name="test_data",
        ),
    ]

    inference_step = ProcessingStep(
        "SageMaker inference step",
        processor=sklearn_processor2,
        job_name=execution_input["InferenceJobName"],
        inputs=inputs,
        outputs=outputs,
        container_entrypoint=["python3", "/opt/ml/processing/input/code/inference.py",],
    )

    # Create Fail state to mark the workflow failed in case any of the steps fail.
    failed_state_sagemaker_processing_failure = stepfunctions.steps.states.Fail(
        "ML Workflow failed", cause="SageMakerProcessingJobFailed"
    )

    # Add the Error handling in the workflow
    catch_state_processing = stepfunctions.steps.states.Catch(
        error_equals=["States.TaskFailed"],
        next_step=failed_state_sagemaker_processing_failure,
    )

    processing_step.add_catch(catch_state_processing)
    inference_step.add_catch(catch_state_processing)

    # Create the Workflow
    workflow_graph = Chain([processing_step, inference_step])
    inference_pipeline = Workflow(
        name=inference_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )
    return inference_pipeline
