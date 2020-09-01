from stepfunctions.inputs import ExecutionInput, StepInput
from stepfunctions.steps.states import Task
from stepfunctions.steps.fields import Field
from stepfunctions.steps.utils import tags_dict_to_kv_list

from sagemaker.workflow.airflow import training_config

class MLMaxTrainingStep(Task):

    """
    Creates a Task State to execute a `SageMaker Training Job <https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html>`_. The TrainingStep will also create a model by default, and the model shares the same name as the training job.
    """

    def __init__(self, state_id, estimator, job_name, data=None, hyperparameters=None, 
                    mini_batch_size=None, experiment_config=None, wait_for_completion=True, tags=None,
                    train_data=None, test_data=None, sm_submit_url=None, sm_region=None, 
                    sm_output_data=None, sm_debug_output_data=None, **kwargs):
        """
        Args:
            state_id (str): State name whose length **must be** less than or equal to 128 unicode characters. State names **must be** unique within the scope of the whole state machine.
            estimator (sagemaker.estimator.EstimatorBase): The estimator for the training step. Can be a `BYO estimator, Framework estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html>`_ or `Amazon built-in algorithm estimator <https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html>`_.
            job_name (str or Placeholder): Specify a training job name, this is required for the training job to run. We recommend to use :py:class:`~stepfunctions.inputs.ExecutionInput` placeholder collection to pass the value dynamically in each execution.
            data: Information about the training data. Please refer to the ``fit()`` method of the associated estimator, as this can take any of the following forms:

                * (str) - The S3 location where training data is saved.
                * (dict[str, str] or dict[str, sagemaker.session.s3_input]) - If using multiple
                    channels for training data, you can specify a dict mapping channel names to
                    strings or :func:`~sagemaker.session.s3_input` objects.
                * (sagemaker.session.s3_input) - Channel configuration for S3 data sources that can
                    provide additional information about the training dataset. See
                    :func:`sagemaker.session.s3_input` for full details.
                * (sagemaker.amazon.amazon_estimator.RecordSet) - A collection of
                    Amazon :class:`Record` objects serialized and stored in S3.
                    For use with an estimator for an Amazon algorithm.
                * (list[sagemaker.amazon.amazon_estimator.RecordSet]) - A list of
                    :class:`sagemaker.amazon.amazon_estimator.RecordSet` objects,
                    where each instance is a different channel of training data.
            hyperparameters (dict, optional): Specify the hyper parameters for the training. (Default: None)
            mini_batch_size (int): Specify this argument only when estimator is a built-in estimator of an Amazon algorithm. For other estimators, batch size should be specified in the estimator.
            experiment_config (dict, optional): Specify the experiment config for the training. (Default: None)
            wait_for_completion (bool, optional): Boolean value set to `True` if the Task state should wait for the training job to complete before proceeding to the next step in the workflow. Set to `False` if the Task state should submit the training job and proceed to the next step. (default: True)
            tags (list[dict], optional): `List to tags <https://docs.aws.amazon.com/sagemaker/latest/dg/API_Tag.html>`_ to associate with the resource.
        """
        self.estimator = estimator
        self.job_name = job_name

        if wait_for_completion:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTrainingJob.sync'
        else:
            kwargs[Field.Resource.value] = 'arn:aws:states:::sagemaker:createTrainingJob'

        if isinstance(job_name, str):
            parameters = training_config(estimator=estimator, inputs=data, job_name=job_name, mini_batch_size=mini_batch_size)
        else:
            parameters = training_config(estimator=estimator, inputs=data, mini_batch_size=mini_batch_size)

        if (data is None and train_data is not None and test_data is not None):
            if (isinstance(train_data, (ExecutionInput, StepInput)) and 
                isinstance(test_data, (ExecutionInput, StepInput))):
                parameters['InputDataConfig'] = [{'DataSource': {'S3DataSource': {'S3DataType': 'S3Prefix', 
                'S3Uri': train_data, 
                'S3DataDistributionType': 'FullyReplicated'}}, 'ChannelName': 'train'}, 
                {'DataSource': {'S3DataSource': {'S3DataType': 'S3Prefix', 
                'S3Uri': test_data, 
                'S3DataDistributionType': 'FullyReplicated'}}, 'ChannelName': 'test'}]

        if (sm_output_data is not None):
            parameters['OutputDataConfig']['S3OutputPath'] = sm_output_data

        if estimator.debugger_hook_config != None:
            parameters['DebugHookConfig'] = estimator.debugger_hook_config._to_request_dict()

        if estimator.rules != None:
            parameters['DebugRuleConfigurations'] = [rule.to_debugger_rule_config_dict() for rule in estimator.rules]
        
        if (sm_debug_output_data is not None):
            parameters['DebugHookConfig']['S3OutputPath'] = sm_debug_output_data

        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters['TrainingJobName'] = job_name

        if hyperparameters is not None:
            if 'HyperParameters' in parameters:
                # try to void overwriting reserved hyperparameters:
                # https://github.com/aws/sagemaker-training-toolkit/blob/master/src/sagemaker_training/params.py
                parameters['HyperParameters'].update(hyperparameters)
            else:
                parameters['HyperParameters'] = hyperparameters
        
        if isinstance(job_name, (ExecutionInput, StepInput)):
            parameters['HyperParameters']['sagemaker_job_name'] = job_name
        
        if (sm_submit_url is not None and isinstance(sm_submit_url, (ExecutionInput, StepInput))):
            parameters['HyperParameters']['sagemaker_submit_directory'] = sm_submit_url
        
        if (sm_region is not None and isinstance(sm_region, (ExecutionInput, StepInput))):
            parameters['HyperParameters']['sagemaker_region'] = sm_region

        if experiment_config is not None:
            parameters['ExperimentConfig'] = experiment_config

        if 'S3Operations' in parameters:
            del parameters['S3Operations']

        if tags:
            parameters['Tags'] = tags_dict_to_kv_list(tags)

        kwargs[Field.Parameters.value] = parameters
        #print(kwargs)
        super(MLMaxTrainingStep, self).__init__(state_id, **kwargs)

    def get_expected_model(self, model_name=None):
        """
            Build Sagemaker model representation of the expected trained model from the Training step. This can be passed
            to the ModelStep to save the trained model in Sagemaker.
            Args:
                model_name (str, optional): Specify a model name. If not provided, training job name will be used as the model name.
            Returns:
                sagemaker.model.Model: Sagemaker model representation of the expected trained model.
        """
        model = self.estimator.create_model()
        if model_name:
            model.name = model_name
        else:
            model.name = self.job_name
        model.model_data = self.output()["ModelArtifacts"]["S3ModelArtifacts"]
        return model