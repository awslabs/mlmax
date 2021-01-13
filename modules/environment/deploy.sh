#!/bin/bash -ex

# example command: ./deploy.sh mlmax-env-stack sagemaker-us-east-1234
STACK_NAME=$1
PACKAGE_BUCKET=${2:-sagemaker-us-east-1-671846148176}

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
  # if [ ! -f config/deploy-${REGION}-${TARGET_ENV}.ini ]; then
  #   echo "Config file does not exist for ${REGION}, ${TARGET_ENV}";
  #   exit 1;
  # else
  #   echo "Config file exists";
  #   . config/deploy-${REGION}-${TARGET_ENV}.ini
  #   STACK_NAME="$PipelineName-$TargetEnv"
  #   echo $STACK_NAME
  # fi
  echo $STACK_NAME
}

package () {
    # Package the aws cloud formation templates
    aws cloudformation package \
        --region ${REGION} \
        --template-file stacks.yaml \
        --s3-bucket ${PACKAGE_BUCKET} \
        --s3-prefix clouformation-packaged \
        --output-template-file stacks_packaged.yaml

    # Validate the AWS cloud formation template
    aws cloudformation validate-template \
        --template-body file://./stacks_packaged.yaml
}

deploy () {

    aws cloudformation deploy \
      --region=${REGION} \
      --stack-name ${STACK_NAME} \
      --template-file ./stacks_packaged.yaml \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
      # --parameter-overrides $(cat config/deploy-${REGION}-${TARGET_ENV}.ini) \

    rm -f ./stacks_packaged.yaml
}


get_region
get_config
package
deploy
