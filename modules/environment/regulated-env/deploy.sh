#!/bin/bash -e

# USAGE:
# example command: ./deploy.sh mlmax-env-stack sagemaker-us-east-1234 ap-southeast-2
#
# NOTES:
# - Your (1) EC2 Keypair, (2) CFN bucket must be in the same region specified in 'REGION' argument.
# - If no region argument is given, default region will be retrieve from .aws/config file.


get_region() {
  REGION=$(aws configure get region)
  if [ "$REGION" == "None" ]; then
    echo "REGION is unset in your AWS configuration";
    exit 1;
  else
    echo "Override REGION to ${REGION}";
  fi
}

get_config() {
  if [ ! -f config/config.ini ]; then
    echo "Config file does not exist";
    exit 1;
  else
    echo "Config file exists";
    . config/config.ini
    echo "KeyName: ${KeyName}"
    echo "S3BucketName: ${S3BucketName}"
  fi
}

check_bucket_exist() {
    if aws s3api head-bucket --bucket ${S3BucketName} 2>/dev/null
    then
        echo
        echo "S3 bucket name already exist, please use another name."
        exit 1
    fi
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
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
      --parameter-overrides $(cat config/config.ini)

    rm -f ./stacks_packaged.yaml
}

#########################
# Main
#########################

STACK_NAME=$1
PACKAGE_BUCKET=$2
REGION=$3

if [ "$#" -lt 2 ]; then
    echo "Missing argument"
    echo
    echo "Usage: deploy.sh <STACK_NAME> <CFN_S3BUCKET> [REGION]"
    echo
    exit 1
fi

echo "Input arguments:"
echo "STACK_NAME: ${STACK_NAME}"
echo "PACKAGE_BUCKET: ${PACKAGE_BUCKET}"
echo "REGION: ${REGION}"


if [[ -z "${REGION}" ]];then
    echo "Retrieving default region..."
    get_region
fi

get_config
check_bucket_exist
package
deploy
