import stepfunctions

# Newer versions of sdk >2.8.0 have PySparkProcessor
from custom_steps import MLMAXProcessingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import Chain
from stepfunctions.workflow import Workflow


def define_data_pipeline(
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
            "PreprocessingCodeURL": str,
            "PreprocessedOutputDataURL": str,
            "S3InputPath": str,
            "S3OutputPath": str,
        }
    )

    """
    Data pre-processing and feature engineering
    """
    # processor = PySparkProcessor(
    region = "ap-southeast-1"
    image = "sagemaker-spark-processing"
    img_uri = f"759080221371.dkr.ecr.{region}.amazonaws.com/{image}:2.4-cpu"
    processor = ScriptProcessor(
        image_uri=img_uri,
        role=sm_role,
        instance_count=16,
        instance_type="ml.m5.2xlarge",
        command=["/opt/program/submit"],
        max_runtime_in_seconds=3600,
        env={"mode": "python"},
    )

    # Create ProcessingInputs and ProcessingOutputs objects for Inputs and
    # Outputs respectively for the SageMaker Processing Job
    inputs = [
        ProcessingInput(
            source=execution_input["PreprocessingCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/output",
            destination=execution_input["PreprocessedOutputDataURL"],
            output_name="processed_data",
        ),
    ]

    processing_step = MLMAXProcessingStep(
        "SageMaker pre-processing step",
        processor=processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=inputs,
        outputs=outputs,
        environment={
            "S3InputPath": execution_input["S3InputPath"],
            "S3OutputPath": execution_input["S3OutputPath"],
        },
        container_entrypoint=[
            "smspark-submit",
            "/opt/ml/processing/input/code/preprocessing.py",
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

    # Create the Workflow
    workflow_graph = Chain([processing_step])
    data_pipeline = Workflow(
        name=data_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )
    return data_pipeline
