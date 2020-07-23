#!/usr/bin/env bash
# Utility for checking permissions for new account
# Todo: code commit, sagemaker, efs, cloudwatch, vpc

##### BEGIN CHANGES #########
S3_BUCKET=""   # existing bucket for testing access to (e.g. "josiah-2017")
S3_KEY=""      # existing in bucket existing for sample download (e.g. "test_file.txt")
REGION=""      # region for testing resource creation (e.g. "ap-southeast-1")
##### END CHANGES ##########

S3_TMP_BUCKET=tmp-`date "+%Y-%m-%d-%H-%M-%S"`

check_env_variables() {
  if [ -z ${S3_BUCKET} ]; then 
    echo "S3_BUCKET is unset"
    exit 1
  else 
    echo "S3_BUCKET is set to '$S3_BUCKET'"; 
  fi
  if [ -z ${S3_KEY} ]; then 
    echo "S3_KEY is unset"
    exit 1
  else 
    echo "S3_KEY is set to '$S3_KEY'"; 
  fi
  if [ -z ${REGION} ]; then 
    echo "REGION is unset"
    exit 1
  else 
    echo "REGION is set to '$REGION'"; 
  fi
}

runc() {
    $1 &>/dev/null
    if [ $? -eq 0 ]; then 
        echo "WORKS  | $1"
    else
        echo "FAILED | $1"
    fi
}

test_s3() {
    runc "aws s3 ls"
    runc "aws s3 ls s3://${S3_BUCKET}"
    runc "aws s3 cp s3://${S3_BUCKET}/${S3_KEY} ."
    runc "aws s3api --region ${REGION} create-bucket --bucket ${S3_TMP_BUCKET} --acl private --create-bucket-configuration LocationConstraint=${REGION}"  
    runc "echo 'one ring to rule them all' | aws s3 cp s3://${S3_TMP_BUCKET}/hello-world.txt"
    runc "aws s3 rm s3://${S3_TMP_BUCKET}/hello-world.txt"
    runc "aws s3api delete-bucket --bucket ${S3_TMP_BUCKET}"
}

test_iam(){
    runc "aws iam list-policies"
    runc "aws iam list-roles"
    runc "aws iam get-policy --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

test_ec2(){
    runc "aws ec2 run-instances --image-id ami-0487874ffa1361b7a"
    runc "create-key-pair --key-name tmp-kp"
    runc "delete-key-pair --key-name tmp-kp"
}

echo "############################################"
check_env_variables
echo " "
echo "S3"
echo "-------"
test_s3
echo " "
echo "IAM"
echo "-------"
test_iam
echo " "
echo "EC2"
echo "-------"
test_ec2
echo " "
echo "############################################"
