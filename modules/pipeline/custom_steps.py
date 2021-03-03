from sagemaker.model import FrameworkModel, Model
from sagemaker.workflow.airflow import model_config, training_config, transform_config
from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps.fields import Field
from stepfunctions.steps.states import Task
from stepfunctions.steps.utils import tags_dict_to_kv_list


class MLMaxBatchTransformStep(Task):
    """
    Creates a Task State to execute a `SageMaker Transform Job
    <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTransformJob.html>`_.
    """

    def __init__(
        self,
        state_id,
        transformer,
        job_name,
        model_name,
        data,
        outputpath,
        data_type="S3Prefix",
        content_type=None,
        compression_type=None,
        split_type=None,
        experiment_config=None,
        wait_for_completion=True,
        tags=None,
        input_filter=None,
        output_filter=None,
        join_source=None,
        **kwargs,
    ):
        """
        Args:
            state_id (str): State name whose length **must be** less than or
            equal to 128 unicode characters. State names **must be** unique
            within the scope of the whole state machine.

            transformer (sagemaker.transformer.Transformer): The SageMaker
            transformer to use in the TransformStep.

            job_name (str or Placeholder): Specify a transform job name. We
            recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput`
            placeholder collection to pass the value dynamically in each
            execution.

            model_name (str or Placeholder): Specify a model name for the
            transform job to use. We recommend to use
            :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder
            collection to pass the value dynamically in each execution.

            data (str): Input data location in S3.

            data_type (str): What the S3 location defines (default: 'S3Prefix').
                Valid values:

                * 'S3Prefix' - the S3 URI defines a key name prefix. All
                objects with this prefix will be used as inputs for the
                transform job.
                * 'ManifestFile' - the S3 URI points to a single manifest file
                listing each S3 object
                    to use as an input for the transform job.

            content_type (str): MIME type of the input data (default: None).

            compression_type (str): Compression type of the input data, if
            compressed (default: None). Valid values: 'Gzip', None.

            split_type (str): The record delimiter for the input object
            (default: 'None'). Valid values: 'None', 'Line', 'RecordIO', and
            'TFRecord'.

            experiment_config (dict, optional): Specify the experiment config
            for the transform. (Default: None)

            wait_for_completion(bool, optional): Boolean value set to `True` if
            the Task state should wait for the transform job to complete before
            proceeding to the next step in the workflow. Set to `False` if the
            Task state should submit the transform job and proceed to the next
            step. (default: True)

            tags (list[dict], optional): `List to tags
            <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to
            associate with the resource.

            input_filter (str): A JSONPath to select a portion of the input to
            pass to the algorithm container for inference. If you omit the
            field, it gets the value ‘$’, representing the entire input. For
            CSV data, each row is taken as a JSON array, so only index-based
            JSONPaths can be applied, e.g. $[0], $[1:]. CSV data should follow
            the RFC format. See Supported JSONPath Operators for a table of
            supported JSONPath operators. For more information, see the
            SageMaker API documentation for CreateTransformJob. Some examples:
                “$[1:]”, “$.features” (default: None).

            output_filter (str): A JSONPath to select a portion of the
            joined/original output to return as the output. For more
            information, see the SageMaker API documentation for
            CreateTransformJob. Some examples: “$[1:]”, “$.prediction”
            (default: None).

            join_source (str): The source of data to be joined to the transform
            output. It can be set to ‘Input’ meaning the entire input record
            will be joined to the inference result. You can use OutputFilter to
            select the useful portion before uploading to S3. (default: None).
            Valid values: Input, None.
        """
        if wait_for_completion:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createTransformJob.sync"
        else:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createTransformJob"

        if isinstance(job_name, str):
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type,
                job_name=job_name,
                input_filter=input_filter,
                output_filter=output_filter,
                join_source=join_source,
            )
        else:
            parameters = transform_config(
                transformer=transformer,
                data=data,
                data_type=data_type,
                content_type=content_type,
                compression_type=compression_type,
                split_type=split_type,
                input_filter=input_filter,
                output_filter=output_filter,
                join_source=join_source,
            )

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters["TransformJobName"] = job_name

        parameters["ModelName"] = model_name
        parameters["TransformOutput"]["S3OutputPath"] = outputpath

        if experiment_config is not None:
            parameters["ExperimentConfig"] = experiment_config

        if tags:
            parameters["Tags"] = tags_dict_to_kv_list(tags)

        # print(parameters)

        kwargs[Field.Parameters.value] = parameters
        super(MLMaxBatchTransformStep, self).__init__(state_id, **kwargs)


class MLMaxTrainingStep(Task):

    """
    Creates a Task State to execute a `SageMaker Training Job
    <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html>`_.
    The TrainingStep will also create a model by default, and the model shares
    the same name as the training job.
    """

    def __init__(
        self,
        state_id,
        estimator,
        job_name,
        data=None,
        hyperparameters=None,
        mini_batch_size=None,
        experiment_config=None,
        wait_for_completion=True,
        tags=None,
        train_data=None,
        test_data=None,
        sm_submit_url=None,
        sm_region=None,
        sm_output_data=None,
        sm_debug_output_data=None,
        **kwargs,
    ):
        """
        Args:
            state_id (str): State name whose length **must be** less than or
            equal to 128 unicode characters. State names **must be** unique
            within the scope of the whole state machine.  estimator
            (sagemaker.estimator.EstimatorBase): The estimator for the training
            step. Can be a `BYO estimator, Framework estimator
            <https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html>`_
            or `Amazon built-in algorithm estimator
            <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.
            job_name (str or Placeholder): Specify a training job name, this is
            required for the training job to run. We recommend to use
            :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder
            collection to pass the value dynamically in each execution.  data:
            Information about the training data. Please refer to the ``fit()``
            method of the associated estimator, as this can take any of the
            following forms:

                * (str) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.session.s3_input]) -
                    If using multiple channels for training data, you can specify a
                    dict mapping channel names to strings or
                    :func:`~sagemaker.session.s3_input` objects.
                * (sagemaker.session.s3_input) - Channel configuration for S3
                    data sources that can provide additional information about the
                    training dataset. See :func:`sagemaker.session.s3_input` for
                    full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            hyperparameters (dict, optional): Specify the hyper parameters for
            the training. (Default: None)
            mini_batch_size (int): Specify this argument only when estimator is
            a built-in estimator of an Amazon algorithm. For other estimators,
            batch size should be specified in the estimator.
            experiment_config (dict, optional): Specify the experiment config
            for the training. (Default: None)
            wait_for_completion (bool, optional): Boolean value set to `True`
            if the Task state should wait for the training job to complete
            before proceeding to the next step in the workflow. Set to `False`
            if the Task state should submit the training job and proceed to the
            next step. (default: True)
            tags (list[dict], optional): `List to tags
            <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to
            associate with the resource.
        """
        self.estimator = estimator
        self.job_name = job_name

        if wait_for_completion:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createTrainingJob.sync"
        else:
            kwargs[
                Field.Resource.value
            ] = "arn:aws:states:::sagemaker:createTrainingJob"

        if isinstance(job_name, str):
            parameters = training_config(
                estimator=estimator,
                inputs=data,
                job_name=job_name,
                mini_batch_size=mini_batch_size,
            )
        else:
            parameters = training_config(
                estimator=estimator, inputs=data, mini_batch_size=mini_batch_size
            )

        if data is None and train_data is not None and test_data is not None:
            if isinstance(train_data, (ExecutionInput, StepInput)) and isinstance(
                test_data, (ExecutionInput, StepInput)
            ):
                parameters["InputDataConfig"] = [
                    {
                        "DataSource": {
                            "S3DataSource": {
                                "S3DataType": "S3Prefix",
                                "S3Uri": train_data,
                                "S3DataDistributionType": "FullyReplicated",
                            }
                        },
                        "ChannelName": "train",
                    },
                    {
                        "DataSource": {
                            "S3DataSource": {
                                "S3DataType": "S3Prefix",
                                "S3Uri": test_data,
                                "S3DataDistributionType": "FullyReplicated",
                            }
                        },
                        "ChannelName": "test",
                    },
                ]

        if sm_output_data is not None:
            parameters["OutputDataConfig"]["S3OutputPath"] = sm_output_data

        if estimator.debugger_hook_config is not None:
            parameters[
                "DebugHookConfig"
            ] = estimator.debugger_hook_config._to_request_dict()

        if estimator.rules is not None:
            parameters["DebugRuleConfigurations"] = [
                rule.to_debugger_rule_config_dict() for rule in estimator.rules
            ]

        if sm_debug_output_data is not None:
            parameters["DebugHookConfig"]["S3OutputPath"] = sm_debug_output_data

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters["TrainingJobName"] = job_name

        if hyperparameters is not None:
            if "HyperParameters" in parameters:
                # try to void overwriting reserved hyperparameters:
                # github.com/aws/sagemaker-training-toolkit/blob/
                # master/src/sagemaker_training/params.py
                parameters["HyperParameters"].update(hyperparameters)
            else:
                parameters["HyperParameters"] = hyperparameters

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters["HyperParameters"]["sagemaker_job_name"] = job_name

        if sm_submit_url is not None and isinstance(
            sm_submit_url, (ExecutionInput, StepInput)
        ):
            parameters["HyperParameters"]["sagemaker_submit_directory"] = sm_submit_url

        if sm_region is not None and isinstance(sm_region, (ExecutionInput, StepInput)):
            parameters["HyperParameters"]["sagemaker_region"] = sm_region

        if experiment_config is not None:
            parameters["ExperimentConfig"] = experiment_config

        if "S3Operations" in parameters:
            del parameters["S3Operations"]

        if tags:
            parameters["Tags"] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters
        # print(kwargs)
        super(MLMaxTrainingStep, self).__init__(state_id, **kwargs)

    def get_expected_model(self, model_name=None):
        """
        Build Sagemaker model representation of the expected trained model from
        the Training step. This can be passed to the ModelStep to save the
        trained model in Sagemaker.

        Args:
            model_name (str, optional): Specify a model name. If not provided,
            training job name will be used as the model name.
        Returns:
            sagemaker.model.Model: Sagemaker model representation of the
            expected trained model.
        """
        model = self.estimator.create_model()
        if model_name:
            model.name = model_name
        else:
            model.name = self.job_name
        model.model_data = self.output()["ModelArtifacts"]["S3ModelArtifacts"]
        return model


class MLMaxModelStep(Task):

    """
    Creates a Task State to `create a model in SageMaker
    <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateModel.html>`_.
    """

    def __init__(
        self,
        state_id,
        model,
        model_data_url=None,
        sagemaker_submit_directory=None,
        model_name=None,
        instance_type=None,
        tags=None,
        **kwargs,
    ):
        """
        Args:
            state_id (str): State name whose length **must be** less than or
            equal to 128 unicode characters. State names **must be** unique
            within the scope of the whole state machine.

            model (sagemaker.model.Model): The SageMaker model to use in the
            ModelStep. If :py:class:`TrainingStep` was used to train the model
            and saving the model is the next step in the workflow, the output
            of :py:func:`TrainingStep.get_expected_model()` can be passed here.

            model_name (str or Placeholder, optional): Specify a model name,
            this is required for creating the model. We recommend to use
            :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder
            collection to pass the value dynamically in each execution.

            instance_type (str, optional): The EC2 instance type to deploy this
            Model to. For example, 'ml.p2.xlarge'. This parameter is typically
            required when the estimator used is not an `Amazon built-in
            algorithm
            <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.

            tags (list[dict], optional): `List to tags
            <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to
            associate with the resource.
        """
        if isinstance(model, FrameworkModel):
            parameters = model_config(
                model=model,
                instance_type=instance_type,
                role=model.role,
                image=model.image,
            )
            if model_name:
                parameters["ModelName"] = model_name
            # placeholder for model data url
            if model_data_url:
                parameters["PrimaryContainer"]["ModelDataUrl"] = model_data_url
            # placeholder for sagemaker script
            if sagemaker_submit_directory:
                parameters["PrimaryContainer"]["Environment"][
                    "SAGEMAKER_SUBMIT_DIRECTORY"
                ] = sagemaker_submit_directory
            print(parameters)
        elif isinstance(model, Model):
            parameters = {
                "ExecutionRoleArn": model.role,
                "ModelName": model_name or model.name,
                "PrimaryContainer": {
                    "Environment": {},
                    "Image": model.image,
                    "ModelDataUrl": model.model_data,
                },
            }
        else:
            raise ValueError(
                (
                    f"Expected 'model' parameter to be of type 'sagemaker.model.Model'"
                    f", but received type '{type(model).__name__}'"
                )
            )

        if "S3Operations" in parameters:
            del parameters["S3Operations"]

        if tags:
            parameters["Tags"] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters
        kwargs[Field.Resource.value] = "arn:aws:states:::sagemaker:createModel"

        super(MLMaxModelStep, self).__init__(state_id, **kwargs)
