STACK_NAME="mlmax-demo-cicd-pipeline"
PACKAGE_BUCKET=${1:-sagemaker-us-east-1-783128296767}

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
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}

get_region
deploy
