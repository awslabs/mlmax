#!/bin/bash -ex

replace_text_in_file() {
  local FIND_TEXT=$1
  local REPLACE_TEXT=$2
  local SRC_FILE=$3
  sed -i.bak s/${FIND_TEXT}/${REPLACE_TEXT}/g ${SRC_FILE}
  rm $SRC_FILE.bak
}

# re
replace_text_in_file 'AWSTemplateFormatVersion: 2010-09-09\x27\nDescription: CloudFormation template for AWS Step Functions - State Machine' 'AWSTemplateFormatVersion: \x272010-09-09\x27\nDescription: CloudFormation template for AWS Step Functions - State Machine\n\nParameters:\n  TrainingPipelineName: \n    Type: String\n  SagerMakerRoleArn:\n    Type: String\n  WorkflowExecutionRoleArn:\n    Type: String\n  TargetEnv:\n    Type: String' '/tmp/my_training_pipeline.yaml'
