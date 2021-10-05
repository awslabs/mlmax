#!/bin/bash -ex

# example command: ./deploy_scheduler.sh dev
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
    STACK_NAME="$PipelineName-$TargetEnv-scheduler"
    echo $STACK_NAME
  fi
}

deploy () {

    aws cloudformation deploy \
      --region=${REGION} \
      --stack-name ${STACK_NAME} \
      --template-file ./templates/scheduler.yaml \
      --parameter-overrides $(cat config/scheduler.ini) \
      PipelineName=${STACK_NAME} TargetEnv=${TARGET_ENV} \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}


get_region
get_config
deploy
