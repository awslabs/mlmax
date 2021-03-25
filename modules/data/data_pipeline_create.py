from data_pipeline_define import define_data_pipeline


def format_template_str():
    with open("/tmp/my_data_pipeline.yaml", "r") as file:
        data = file.read()

    # add the parameters
    data = data.replace(
        """AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for AWS Step Functions - State Machine
""",
        """AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for AWS Step Functions - State Machine

Parameters:
  PipelineName:
    Type: String
  SagerMakerRoleArn:
    Type: String
  WorkflowExecutionRoleArn:
    Type: String
  TargetEnv:
    Type: String

""",
    )

    # replace StateMachineName
    data = data.replace(
        "StateMachineName: ${DataPipelineName}",
        'StateMachineName: !Sub "${PipelineName}-Data-${TargetEnv}"',
    )

    # replace DefinitionString
    data = data.replace("DefinitionString:", "DefinitionString: !Sub")

    # replace Role Arn
    data = data.replace(
        "RoleArn: ${WorkflowExecutionRoleArn}",
        'RoleArn: !Sub "${WorkflowExecutionRoleArn}"',
    )

    # add output
    data = (
        data
        + "\n"
        + """Outputs:
  StateMachineComponentArn:
    Description: The step function ARN
    Value: !GetAtt StateMachineComponent.Arn
"""
    )
    with open("./templates/my_data_pipeline.yaml", "w") as file:
        file.write(data)


def create_data_pipeline(
    sm_role,
    workflow_execution_role,
    data_pipeline_name,
    return_yaml=True,
    dump_yaml_file="templates/sagemaker_data_pipeline.yaml",
):
    """
    Return YAML definition of the data pipeline, which consists of multiple
    Amazon StepFunction steps

    sm_role:                    ARN of the SageMaker execution role
    workflow_execution_role:    ARN of the StepFunction execution role
    return_yaml:                Return YAML representation or not, if False, it returns
                                an instance of `stepfunctions.workflow.WorkflowObject`
    dump_yaml_file:             If not None, a YAML file will be generated at this file
                                location

    """

    data_pipeline = define_data_pipeline(
        sm_role,
        workflow_execution_role,
        data_pipeline_name,
        return_yaml,
        dump_yaml_file,
    )
    # dump YAML cloud formation template
    yml = data_pipeline.get_cloudformation_template()

    if dump_yaml_file is not None:
        with open(dump_yaml_file, "w") as fout:
            fout.write(yml)

    if return_yaml:
        return yml
    else:
        return data_pipeline


def example_create_data_pipeline():
    """
    An example on obtaining YAML CF template from the data pipeline definition
    """
    sm_role = "${SagerMakerRoleArn}"
    workflow_execution_role = "${WorkflowExecutionRoleArn}"
    data_pipeline_name = "${DataPipelineName}"
    yaml_rep = create_data_pipeline(
        sm_role=sm_role,
        workflow_execution_role=workflow_execution_role,
        data_pipeline_name=data_pipeline_name,
        dump_yaml_file=None,
    )
    with open("/tmp/my_data_pipeline.yaml", "w") as fout:
        fout.write(yaml_rep)


if __name__ == "__main__":
    example_create_data_pipeline()
    format_template_str()
