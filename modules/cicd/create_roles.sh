#!/usr/bin/env bash
set -e

TARGET_ENV=${1}
if [[ -z $TARGET_ENV ]];then
    echo "Please provide target (devops, stage, prod) environment as argument..."
    exit
fi

if [[ $TARGET_ENV != "prod" ]] && [[ $TARGET_ENV != "stage" ]]&& [[ $TARGET_ENV != "devops" ]]; then
    echo "Invalid environment: ${TARGET_ENV}"
    echo "Please provide target (devops, stage, prod) environment as argument..."
    exit
fi

echo "TARGET_ENV: ${TARGET_ENV}"

source config/cicd.ini

deploy () {
    aws cloudformation deploy \
    --region=${Region} \
    --stack-name ${StackNameRoles}-${TARGET_ENV} \
    --template-file ./cicd_roles.yaml \
    --parameter-overrides $(cat config/cicd.ini) TargetEnv=${TARGET_ENV} \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}

deploy
