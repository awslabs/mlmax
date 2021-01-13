# Regulated Industry SageMaker Environment Setup

The purpose of this guide is to setup a data science development environment in a regulated industry. This template will setup the minimum service such as SageMaker Notebook and S3 bucket for Data Scientist to start working on customer engagement.

# Use Case

Very often in a regulated industry such as Financial Service and Healthcase where data security is critical, customer has the following minimal requirement to be compliance for data science work.

- Enforce S3 encryption for all content at rest. In addition, data upload encryption header must be specified.
- No public internet access to minimize risk. Resource will have to reside in a private VPC

# Architecture Diagram

![Architecture](images/architecture.jpg)

# Setup Guide

Execute the following command to bring up the environment using cloudformation template. If `rain` command is not available, you can run `make install_rain` (for OXS) on  project directory.

```
rain deploy stacks.yaml <stack_name>
```

# Services

## S3

- Enforce service side encryption with customer managed key
- Data Scientist or developer is responsible to specify kmsid for AWSCLI, SDK or BOTO3 for any data upload to S3

## SageMaker

- Encrypted EBS volume with customer manged key
- Restricted access to default encrypted S3 bucket

## VPC Endpoint

The following endpoints have been added by default:

- s3
- git-codecommit, codecommit
- sagemaker.api, sagemaker.runtime
- ecr.api, ec.dkr
- sts
- logs

## KMS

- Generate customer managed key

## VPC

- Two Private subnets only across different avaiability zones
