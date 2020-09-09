#!/bin/bash -ex

# example command: ./deploy.sh dev MlMax-Training-Pipeline-Demo sagemaker-us-east-1234
TARGET_ENV=$1

get_region() {
  REGION=$(aws configure get region)
  if [ "$REGION" == "None" ]; then 
    echo "REGION is unset in your AWS configuration";
    exit 1;
  else
    echo "REGION is set to ${REGION}";
  fi
}


get_config() {
  if [ ! -f config/deploy-${REGION}-${TARGET_ENV}.ini ]; then 
    echo "Config file does not exist for ${REGION}, ${TARGET_ENV}";
    exit 1;
  else
    echo "Config file exists";
    . config/deploy-${REGION}-${TARGET_ENV}.ini
    STACK_NAME="$TrainingPipelineName-$TargetEnv"
    echo $STACK_NAME 
  fi
}

deploy () {

    local CMD="aws cloudformation --region=${REGION}"

    ${CMD} deploy \
      --stack-name ${STACK_NAME} \
      --template-file ./templates/master_packaged.yaml \
      --parameter-overrides $(cat config/deploy-${REGION}-${TARGET_ENV}.ini) \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

    rm -f ./templates/master_packaged.yaml
}


get_region
get_config

PACKAGE_BUCKET=${2:-sagemaker-${REGION}-671846148176}
# package the aws cloud formation templates
aws cloudformation package \
      --region ${REGION} \
      --template-file templates/master.yaml \
      --s3-bucket ${PACKAGE_BUCKET} \
      --s3-prefix clouformation-packaged \
      --output-template-file templates/master_packaged.yaml

# Validate the AWS cloud formation template
aws cloudformation validate-template --template-body file://./templates/master_packaged.yaml

deploy

