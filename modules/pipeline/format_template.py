# debug
import yaml

with open("/tmp/my_training_pipeline.yaml") as f:
    pipeline = yaml.load(f, Loader=yaml.FullLoader)

# add the parameters
pipeline["Parameters"] = {
  "TrainingPipelineName": {
    "Type": "String"
  },
  "SagerMakerRoleArn": {
    "Type": "String"
  },
  "WorkflowExecutionRoleArn": {
    "Type": "String"
  },
  "TargetEnv": {
    "Type": "String"
  }
}

# replace StateMachineName
pipeline['Resources']['StateMachineComponent']['Properties']['StateMachineName'] = '!Sub "${TrainingPipelineName}-${TargetEnv}"'

# replace DefinitionString
old_value = pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString']
pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString'] = "!Sub " + old_value

# replace
old_value = pipeline['Resources']['StateMachineComponent']['Properties']['RoleArn']
pipeline['Resources']['StateMachineComponent']['Properties']['RoleArn'] = "!Sub " + old_value

with open("/tmp/my_training_pipeline.yaml", "w") as f:
    pipeline = yaml.dump(pipeline, f)
