# debug
#import yaml

import ruamel.yaml as yaml

#infile = yaml.load(open('yamlfile'), Loader=yaml.RoundTripLoader)

with open("/tmp/my_training_pipeline.yaml") as f:
    pipeline = yaml.load(f, Loader=yaml.RoundTripLoader)

#print(pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString'])

## add the parameters
#pipeline["Parameters"] = {
#  "TrainingPipelineName": {
#    "Type": "String"
#  },
#  "SagerMakerRoleArn": {
#    "Type": "String"
#  },
#  "WorkflowExecutionRoleArn": {
#    "Type": "String"
#  },
#  "TargetEnv": {
#    "Type": "String"
#  }
#}

## replace StateMachineName
pipeline['Resources']['StateMachineComponent']['Properties']['StateMachineName'] = '!Sub "${TrainingPipelineName}-${TargetEnv}"'

#replace DefinitionString
old_value = pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString']
pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString'] = '!Sub' + old_value

# replace
old_value = pipeline['Resources']['StateMachineComponent']['Properties']['RoleArn']
pipeline['Resources']['StateMachineComponent']['Properties']['RoleArn'] = "!Sub " + old_value

#with open("./modules/pipeline/templates/my_training_pipeline_formatted.yaml", "w") as f:
#with open("./templates/my_training_pipeline_formatted.yaml", "w") as f:
#    pipeline = yaml.dump(pipeline, f, default_style='|')
##import sys
##yaml.dump(pipeline, sys.stdout)
##sys.stdout.write('\n')

#with open("./templates/my_training_pipeline_formatted.yaml", "w") as f:
#    yaml.dump(f, Dumper=yaml.RoundTripDumper)
print(yaml.dump(pipeline, Dumper=yaml.RoundTripDumper))
