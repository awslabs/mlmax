#!/bin/bash
set -ex

ACCOUNT_ID=${1:-$(aws sts get-caller-identity --query Account --output text)}
REGION=${2:-$(aws configure get region --output text)}
REPO_NAME="mlmax-processing-monitor"
SERVER="${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com"
echo "ACCOUNT_ID: ${ACCOUNT_ID}"
echo "REPO_NAME: ${REPO_NAME}"
echo "REGION: ${REGION}"
echo "DOCKERFILE: ${DOCKERFILE}"

docker build -f Dockerfile -t ${REPO_NAME} .

docker tag ${REPO_NAME} ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:latest

aws ecr get-login-password | docker login --username AWS --password-stdin ${SERVER}

aws ecr describe-repositories --repository-names ${REPO_NAME}|| aws ecr create-repository --repository-name ${REPO_NAME}

docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:latest

