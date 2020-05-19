# ML Max Environment

This repository is a set of tools to quickly set up development environment for ML porject. It is created with the intention of encouraging collaboration as each module is aimed to be bite size, such that it is easier to understand how it works and use it for different projects.

Each module can be picked and chosen depending on project use cases, it need not be used as a whole together.

# Main categories

1. Software installation using makefile
2. AWS resource creation using Cloudformation script
3. WIP

# 1. Software Installation

The installation can be done using `make` command executed understand root directory where Makefile is located. The tenet is to allow tool to be setup with a single command.

## 1.1 Create Virtual environment

To create a new virtual environment using python `venv` package. Once the virtual environment has been created, use your favourite IDE to choose the python environment.

```
# Update `requirements.txt` with the desired package

# Run this command to create virtual environment
make create_env
```

## 1.2 Rain

This is a CloudFormation helper tools. User guide can be found [here](https://github.com/aws-cloudformation/rain)

```
# To install
make install_rain
```

## 1.3 EC2 Scheduler CLI

Prerequitesite:

- spin up EC2 Scheduler using cloudformation
  
This tool is to facilitate creation of custom schedule in DynamoDB for EC2 startup/shutdown configuration. Each EC2 instance can be tagged with `Schedule=daily7-11` for scheduler to check for usage monitoring.

User guide can be found [here](https://docs.aws.amazon.com/solutions/latest/instance-scheduler/appendix-a.html)

```
# To install
make install_scheduler_cli

# Create a new custom period
scheduler-cli create-period --stack ec2-scheduler --region ap-southeast-1 --name "period1" --begintime "07:00" --endtime "23:00"

# Attach period to schedule
scheduler-cli create-schedule --stack ec2-scheduler --region ap-southeast-1 --name "daily7-11" --period "period1" --timezone "Asia/Singapore"

# Next step is to assign EC2 to default tag 'Schedule=daily7-11'
```

# 2. CloudFormation Templates

These section contains moduler cloudformation template that is commonly used. Everyone is encouraged to contribute to template that is commondly used.

1. 00_nested_stack.yaml
   - This is a top level stack
   - Nested stack can be added in this yaml file

2. The following are different templates that can be added into the top level stack. Only those required by your use case need to be added to top level stack
   - EC2
     - Support bastian-less ssh
   - S3
   - EC2 scheduler
     - EC2 auto startup/shutdown configuration tool
   - Sagemaker Notebook
     - Custom S3 access control
     - Auto shutdown
     - Default git repo
     - Persistent custom Python environment
   - IAM policy
   - ECR repo
     - Build a default ECR repo name `mlmax-repo`
   - CodeCommit
     - Auto trigger of lambda function upon push request
   - Glue Crawler

   - Glue Schema

Run the following command to deploy cloudformation yaml script:

```
# rain deploy <template.yaml> <stack_name>

rain deploy 00_nested_stack.yaml my_nested_stack
```

# Additional Information

## AWS Glue Crawler

This artifact contains a cloudformation script which will:

- Create an AWS Glue crawler to identify the data schema in S3 bucket using a custom classifier to rename columns' name
- Scheduel crawler to run every 5 minutes using cloudwatch so that new data get updated

To use the cloudformation, simply update the S3 bucket name that contains the `glue_test_data_csv`.

## Use Case

This provide an alternative approach where you have huge dataset to process, compared to using multiprocessing approach, to cover the following:

- New data coming into S3 bucket regularly, which you need to refresh and to rename to column and expose it for query and QuickSight visualization
- Use Athena to retrieve the data training/retraining when the size is extremely large
- Auto schema discovery for your inference result in S3 for user to consume using Athena query
- Production ready glue cloudformation for deployment
