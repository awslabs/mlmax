import stepfunctions

# Newer versions of sdk >2.8.0 have PySparkProcessor
# from custom_steps import MLMAXProcessingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import ScriptProcessor
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import Chain, ProcessingStep
from stepfunctions.workflow import Workflow


def define_monitor_pipeline(
    account,
    region,
    sm_role,
    workflow_execution_role,
    data_pipeline_name,
    return_yaml=True,
    dump_yaml_file="templates/sagemaker_data_pipeline.yaml",
):
    """
    Return YAML definition of the training pipeline, which consists of multiple
    Amazon StepFunction steps

    sm_role:                    ARN of the SageMaker execution role
    workflow_execution_role:    ARN of the StepFunction execution role
    return_yaml:                Return YAML representation or not, if False,
                                it returns an instance of
                                    `stepfunctions.workflow.WorkflowObject`
    dump_yaml_file:             If not None, a YAML file will be generated at
                                    this file location

    """

    # Pass required parameters dynamically for each execution using placeholders.
    execution_input = ExecutionInput(
        schema={
            "PreprocessingJobName": str,
            "PreprocessingInferJobName": str,
            "PreprocessingCodeURL": str,
            "MonitorTrainOutputURL": str,
            "MonitorInferOutputURL": str,
            "InputDataURL": str,
            "InferDataURL": str,
        }
    )

    """
    Custom container for monitoring
    """
    image = "mlmax-processing-monitor"
    img_uri = f"{account}.dkr.ecr.{region}.amazonaws.com/{image}:latest"
    processor = ScriptProcessor(
        image_uri=img_uri,
        role=sm_role,
        instance_count=16,
        instance_type="ml.m5.2xlarge",
        command=["/opt/program/submit"],
        max_runtime_in_seconds=3600,
        env={"mode": "python"},
    )

    #############################
    # Baseline
    #############################
    # Create ProcessingInputs and ProcessingOutputs objects for Inputs and
    # Outputs respectively for the SageMaker Processing Job
    inputs = [
        ProcessingInput(
            source=execution_input["InputDataURL"],
            destination="/opt/ml/processing/train_input",
            input_name="train-input-data",
        ),
        ProcessingInput(
            source=execution_input["PreprocessingCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/profiling/inference",
            destination=execution_input["MonitorTrainOutputURL"],
            output_name="baseline-data",
        )
    ]

    processing_step = ProcessingStep(
        "SageMaker pre-processing Baseline",
        processor=processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--train-test-split-ratio", "0.2", "--mode", "train"],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/input/code/monitoring.py",
        ],
    )

    #############################
    # Inference
    #############################
    inputs = [
        ProcessingInput(
            source=execution_input["InferDataURL"],
            destination="/opt/ml/processing/infer_input",
            input_name="infer-input-data",
        ),
        ProcessingInput(
            source=execution_input["MonitorTrainOutputURL"],
            destination="/opt/ml/processing/profiling",
            input_name="baseline-data",
        ),
        ProcessingInput(
            source=execution_input["PreprocessingCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/profiling/inference",
            destination=execution_input["MonitorInferOutputURL"],
            output_name="monitor-output",
        )
    ]

    processing_step_inference = ProcessingStep(
        "SageMaker pre-processing Inference",
        processor=processor,
        job_name=execution_input["PreprocessingInferJobName"],
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--mode", "infer"],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/input/code/monitoring.py",
        ],
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
    processing_step_inference.add_catch(catch_state_processing)

    # Create the Workflow
    workflow_graph = Chain([processing_step, processing_step_inference])
    data_pipeline = Workflow(
        name=data_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )
    return data_pipeline
