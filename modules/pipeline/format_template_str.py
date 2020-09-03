with open("/tmp/my_training_pipeline.yaml", "r") as file:
    data = file.read()

# add the parameters
data = data.replace("""AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for AWS Step Functions - State Machine
""",
"""AWSTemplateFormatVersion: '2010-09-09'
Description: CloudFormation template for AWS Step Functions - State Machine

# Added by script
Parameters:
  TrainingPipelineName:
    Type: String
  SagerMakerRoleArn:
    Type: String
  WorkflowExecutionRoleArn:
    Type: String
  TargetEnv:
      Type: String

"""
)

# replace StateMachineName
data = data.replace("StateMachineName: ${TrainingPipelineName}", "# Replaced by script\n      StateMachineName: !Sub \"${TrainingPipelineName}-${TargetEnv}\"")

# replace DefinitionString
data = data.replace("DefinitionString:", "# Replaced by script\n      DefinitionString: !Sub")

# replace Role Arn
data = data.replace("RoleArn: ${WorkflowExecutionRoleArn}", "# Replaced by script\n      RoleArn: !Sub \"${WorkflowExecutionRoleArn}\"")

with open("./templates/my_training_pipeline.yaml", "w") as file:
    file.write(data)
