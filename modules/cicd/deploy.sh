STACK_NAME="mlmax-demo-cicd-pipeline"
PACKAGE_BUCKET=${1:-sagemaker-us-east-1-783128296767}
CodePipelineServiceRoleArn="arn:aws:iam::783128296767:role/mlmax-demo-cicd-pipeline-roles-CodePipelineServiceRole"
DeployRoleStageArn="arn:aws:iam::497394617784:role/mlmax-demo-cicd-pipeline-roles-deploy-role"
DeployRoleProdArn="arn:aws:iam::161422014849:role/mlmax-demo-cicd-pipeline-roles-deploy-role"
InvokeStepFunctionRoleArn="arn:aws:iam::497394617784:role/mlmax-demo-cicd-pipeline-roles-InvokeStepFunctionRole"
DevopsAccountId="783128296767"
StageAccountId="497394617784"
ProdAccountId="161422014849"

get_region() {
    REGION=$(aws configure get region)
    if [ "$REGION" == "None" ]; then
      echo "REGION is unset in your AWS configuration";
      exit 1;
    else
      echo "REGION is set to ${REGION}";
    fi
}

deploy () {
    aws cloudformation deploy \
      --region=${REGION} \
      --stack-name ${STACK_NAME} \
      --template-file ./cicd.yaml \
      --parameter-overrides \
      PackageBucket=${PACKAGE_BUCKET} \
      Region=${REGION} \
      StackName=${STACK_NAME} \
      CodePipelineServiceRoleArn=${CodePipelineServiceRoleArn} \
      DeployRoleStageArn=${DeployRoleStageArn} \
      DeployRoleProdArn=${DeployRoleProdArn} \
      InvokeStepFunctionRoleArn=${InvokeStepFunctionRoleArn} \
      DevopsAccountId=${DevopsAccountId} \
      StageAccountId=${StageAccountId} \
      ProdAccountId=${ProdAccountId} \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}

get_region
deploy
