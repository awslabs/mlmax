from sagemaker.workflow.airflow import processing_config
from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps.fields import Field
from stepfunctions.steps.states import Task
from stepfunctions.steps.utils import tags_dict_to_kv_list


class MLMAXProcessingStep(Task):

    """
    Creates a Task State to execute a SageMaker Processing Job.
    """

    def __init__(
        self,
        state_id,
        processor,
        job_name,
        inputs=None,
        outputs=None,
        experiment_config=None,
        container_arguments=None,
        container_entrypoint=None,
        kms_key_id=None,
        wait_for_completion=True,
        tags=None,
        environment=None,
        **kwargs
    ):
        """
        Args:
            state_id (str): State name whose length **must be** less than or
                equal to 128 unicode characters. State names **must be** unique
                within the scope of the whole state machine.
            processor (sagemaker.processing.Processor): The processor for the
            processing step.
                job_name (str or Placeholder): Specify a processing job name, this
                    is required for the processing job to run. We recommend to use
                :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder
                collection to pass the value dynamically in each execution.
            inputs (list[:class:`~sagemaker.processing.ProcessingInput`]):
                Input files for the processing job. These must be provided as
                :class:`~sagemaker.processing.ProcessingInput` objects (default:
                None).
            outputs (list[:class:`~sagemaker.processing.ProcessingOutput`]): Outputs for
                the processing job. These can be specified as either path strings or
                :class:`~sagemaker.processing.ProcessingOutput` objects (default: None).
            experiment_config (dict, optional): Specify the experiment config
                for the processing. (Default: None)
            container_arguments ([str]): The arguments for a container used to
                run a processing job.
            container_entrypoint ([str]): The entrypoint for a container used
                to run a processing job.
            kms_key_id (str): The AWS Key Management Service (AWS KMS) key that
                Amazon SageMaker uses to encrypt the processing job output.
                KmsKeyId can be an ID of a KMS key, ARN of a KMS key, alias of a
                KMS key, or alias of a KMS key.  The KmsKeyId is applied to all
                outputs.
            wait_for_completion (bool, optional): Boolean value set to `True`
                if the Task state should wait for the processing job to complete
                before proceeding to the next step in the workflow. Set to `False`
                if the Task state should submit the processing job and proceed to
                the next step. (default: True)
            tags (list[dict], optional): `List to tags
                <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to
                associate with the resource.
        """
        if wait_for_completion:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createProcessingJob.sync"
        else:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createProcessingJob"

        if isinstance(job_name, str):
            parameters = processing_config(
                processor=processor,
                inputs=inputs,
                outputs=outputs,
                container_arguments=container_arguments,
                container_entrypoint=container_entrypoint,
                kms_key_id=kms_key_id,
                job_name=job_name,
            )
        else:
            parameters = processing_config(
                processor=processor,
                inputs=inputs,
                outputs=outputs,
                container_arguments=container_arguments,
                container_entrypoint=container_entrypoint,
                kms_key_id=kms_key_id,
            )

        # placeholder (change at run time) or str for
        # the Container Environment Variables
        if environment is not None:
            parameters["Environment"] = environment

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters["ProcessingJobName"] = job_name

        if experiment_config is not None:
            parameters["ExperimentConfig"] = experiment_config

        if tags:
            parameters["Tags"] = tags_dict_to_kv_list(tags)

        if "S3Operations" in parameters:
            del parameters["S3Operations"]

        kwargs[Field.Parameters.value] = parameters

        super(MLMAXProcessingStep, self).__init__(state_id, **kwargs)
