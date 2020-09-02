#!/bin/bash -ex

# example command: ./deploy.sh us-east-1 dev MlMax-Training-Pipeline-Demo

REGION=$1
TARGET_ENV=$2
STACK_PREFIX=$3
PACKAGE_BUCKET=${4:-sagemaker-${REGION}-671846148176}
echo $PACKAGE_BUCKET

# Package the AWS cloud formation templates
aws cloudformation package \
      --region ${REGION} \
      --template-file templates/master.yaml \
      --s3-bucket sagemaker-${REGION}-671846148176 \
      --s3-prefix clouformation-packaged \
      --output-template-file templates/master_packaged.yaml

# Validate the AWS cloud formation template
aws cloudformation validate-template --template-body file://./templates/master_packaged.yaml

deploy () {
    local STACK_NAME=${STACK_PREFIX}-${TARGET_ENV}

    local CMD="aws cloudformation --region=${REGION}"

    ${CMD} deploy \
      --stack-name ${STACK_NAME} \
      --template-file ./templates/master_packaged.yaml \
      --parameter-overrides $(cat config/deploy-${REGION}-${TARGET_ENV}.ini) \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

    rm -f ./templates/master_packaged.yaml
}

deploy
