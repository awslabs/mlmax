# !/bin/bash

# Build and push docker image to ECR
#
# Prerequisite: ECR repo has been created
# Arg: ECR repo name

image_name=${1:-mlmax-repo}

$(aws ecr get-login --no-include-email --region ap-southeast-1)
docker build -t ${image_name} .
docker tag mlmax-repo:latest 342474125894.dkr.ecr.ap-southeast-1.amazonaws.com/${image_name}:latest



