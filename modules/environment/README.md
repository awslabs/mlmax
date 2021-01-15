# Regulated Industry SageMaker Environment Setup

The purpose of this guide is to setup a data science development environment in a regulated industry. This template will setup the minimum service such as bastianless EC2 instance, SageMaker Notebook and S3 bucket for Data Scientist to start working on customer engagement.

# Use Case

Very often in a regulated industry such as Financial Service and Healthcase where data security is critical, customer has the following minimal requirement to be compliance for data science work.

- Enforce S3 encryption for all content at rest. In addition, data upload encryption header must be specified.
- No public internet access to minimize risk. Resource will have to reside in a private VPC

# Architecture Diagram

![Architecture](images/architecture.jpg)

# Setup Guide

1) Update the following config in `config/config.ini`
    - KeyName: Existing EC2 key pair name that you have access to the private file
    - S3BucketName: Unique S3 bucket name for project

2) Get ready a S3 bucket name in the same region to store cloudformation intermediate metedata

3) To deploy, run the command `deploy.sh [stack-name] [cloudformatin-bucket]`

# Services

## S3

- Enforce service side encryption with customer managed key
- Data Scientist or developer is responsible to specify kmsid for AWSCLI, SDK or BOTO3 for any data upload to S3

## SageMaker

- Encrypted EBS volume with customer manged key
- Restricted access to default encrypted S3 bucket

## VPC Endpoint

The following endpoints have been added by default, additional endpoint can be added as necessary.

- s3
- git-codecommit, codecommit
- sagemaker.api, sagemaker.runtime
- ecr.api, ec.dkr
- sts
- logs
- ssm

## KMS

- Generate a customer managed key

## VPC

- Two Private Subnets only across different avaiability zones

## EC2

- SSM Agent to support remote SSH using exisitng key pair
- First verify that Session Manager Plugin is installed on your local workstation by running the command below
- Or follow the instruction [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-verify) to install SSM agent

```
aws ssm start-session --target <ec2-instance-id>
```

- Update SSH config to be able to SSH to EC2 using command `ssh ec2-ssm`.

```
# Add the following in your SSH config

Host ec2-ssm
    HostName <ec2-instance-id>
    User ec2-user
    IdentityFile /path/to/keypair/pemfile
    ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'"

```
