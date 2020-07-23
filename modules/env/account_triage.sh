#!/usr/bin/env bash
# Utility for checking permissions for new account
# Todo: code commit, sagemaker, efs, cloudwatch, vpc

##### BEGIN CHANGES #########
S3_BUCKET="josiah-2017"   # existing bucket for testing access to
S3_KEY="test_file.txt"    # existing in bucket existing for sample download
REGION="ap-southeast-1"   # region for testing resource creation
##### END CHANGES ##########

S3_TMP_BUCKET=tmp-`date "+%Y-%m-%d-%H-%M-%S"`

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
