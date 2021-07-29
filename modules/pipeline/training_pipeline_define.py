import stepfunctions
from custom_steps import MLMaxTrainingStep
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.processing import SKLearnProcessor
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import Chain, ProcessingStep
from stepfunctions.workflow import Workflow


def define_training_pipeline(
    sm_role,
    workflow_execution_role,
    training_pipeline_name,
    return_yaml=True,
    dump_yaml_file="templates/sagemaker_training_pipeline.yaml",
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
            "InputDataURL": str,
            "PreprocessingJobName": str,
            "PreprocessingCodeURL": str,
            "TrainingJobName": str,
            # Prevent sagemaker config hardcode sagemaker_submit_directory in
            # workflow definition
            "SMSubmitDirURL": str,
            # Prevent sagemaker config hardcode sagemaker_region in workflow definition
            "SMRegion": str,
            "EvaluationProcessingJobName": str,
            "EvaluationCodeURL": str,
            "EvaluationResultURL": str,
            "PreprocessedTrainDataURL": str,
            "PreprocessedTestDataURL": str,
            "PreprocessedModelURL": str,
            "SMOutputDataURL": str,
            "SMDebugOutputURL": str,
        }
    )

    """
    Data pre-processing and feature engineering
    """
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
    ]

    outputs = [
        ProcessingOutput(
            source="/opt/ml/processing/train",
            destination=execution_input["PreprocessedTrainDataURL"],
            output_name="train_data",
        ),
        ProcessingOutput(
            source="/opt/ml/processing/test",
            destination=execution_input["PreprocessedTestDataURL"],
            output_name="test_data",
        ),
        ProcessingOutput(
            source="/opt/ml/processing/model",
            destination=execution_input["PreprocessedModelURL"],
            output_name="proc_model",
        ),
    ]

    processing_step = ProcessingStep(
        "SageMaker pre-processing step",
        processor=sklearn_processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=inputs,
        outputs=outputs,
        container_arguments=["--train-test-split-ratio", "0.2", "--mode", "train"],
        container_entrypoint=[
            "python3",
            "/opt/ml/processing/input/code/preprocessing.py",
        ],
    )

    """
    Training using the pre-processed data
    """
    sklearn = SKLearn(
        entry_point="../../src/mlmax/train.py",
        train_instance_type="ml.m5.xlarge",
        role=sm_role,
        py_version="py3",
        framework_version="0.20.0",
    )

    training_step = MLMaxTrainingStep(
        "SageMaker Training Step",
        estimator=sklearn,
        job_name=execution_input["TrainingJobName"],
        train_data=execution_input["PreprocessedTrainDataURL"],
        test_data=execution_input["PreprocessedTestDataURL"],
        sm_submit_url=execution_input["SMSubmitDirURL"],
        sm_region=execution_input["SMRegion"],
        sm_output_data=execution_input["SMOutputDataURL"],
        sm_debug_output_data=execution_input["SMDebugOutputURL"],
        wait_for_completion=True,
    )

    """
    Model evaluation
    """
    # Create input and output objects for Model Evaluation ProcessingStep.
    inputs_evaluation = [
        ProcessingInput(
            source=execution_input["PreprocessedTestDataURL"],
            destination="/opt/ml/processing/test",
            input_name="input-1",
        ),
        ProcessingInput(
            source=training_step.get_expected_model().model_data,
            destination="/opt/ml/processing/model",
            input_name="input-2",
        ),
        ProcessingInput(
            source=execution_input["EvaluationCodeURL"],
            destination="/opt/ml/processing/input/code",
            input_name="code",
        ),
    ]

    outputs_evaluation = [
        ProcessingOutput(
            source="/opt/ml/processing/evaluation",
            destination=execution_input["EvaluationResultURL"],
            output_name="evaluation",
        ),
    ]

    model_evaluation_processor = SKLearnProcessor(
        framework_version="0.20.0",
        role=sm_role,
        instance_type="ml.m5.xlarge",
        instance_count=1,
        max_runtime_in_seconds=1200,
    )

    processing_evaluation_step = ProcessingStep(
        "SageMaker Processing Model Evaluation step",
        processor=model_evaluation_processor,
        job_name=execution_input["EvaluationProcessingJobName"],
        inputs=inputs_evaluation,
        outputs=outputs_evaluation,
        container_entrypoint=["python3", "/opt/ml/processing/input/code/evaluation.py"],
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
    processing_evaluation_step.add_catch(catch_state_processing)
    training_step.add_catch(catch_state_processing)

    # Create the Workflow
    workflow_graph = Chain([processing_step, training_step, processing_evaluation_step])
    training_pipeline = Workflow(
        name=training_pipeline_name,
        definition=workflow_graph,
        role=workflow_execution_role,
    )
    return training_pipeline
