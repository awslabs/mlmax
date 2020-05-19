#!/bin/bash -ex

if [ ! $# -eq 3 ]
  then
    echo "Invalid arguments supplied"
fi

# Option to target specific region and environment
REGION=$1
TARGET_ENV=$2
TEMPLATE=$3

# Command variables regardless of region and environment
#source ./config/build.ini
STACK_PREFIX="ProjectX"
PROFILE="default"
ACCOUNTNUMBER=$(aws sts get-caller-identity --query 'Account' --output text)

echo "Executing..."
echo ${TEMPLATE}

deploy () {
    local STACK_NAME=${STACK_PREFIX}-${TARGET_ENV}

    local CMD="aws cloudformation --region=${REGION} --profile=${PROFILE:-default}"

    # No comment allow in ini files. Must be key-value pair. Value without quote
    ${CMD} deploy \
      --stack-name ${STACK_NAME} \
      --template-file ${TEMPLATE} \
      --parameter-overrides $(cat config/${TARGET_ENV}.ini) \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}

deploy
