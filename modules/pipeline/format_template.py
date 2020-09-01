# debug
import yaml

with open("/tmp/my_training_pipeline.yaml") as f:
    pipeline = yaml.load(f, Loader=yaml.FullLoader)

pipeline['Resources']['StateMachineComponent']['Properties']['DefinitionString']