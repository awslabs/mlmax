# ML technology best practices

Delivering ML solutions to production is hard. It is difficult to know where to
start, what tools to use, and whether you are doing it right. Often each
individual professional does it a different way based on their individual
experience or they use prescribed tools developed within their company. Either
way this requires a lot of investment of time to firstly decide what to do and
secondly to implement and maintain the infrastructure. There are many existing
tools that make parts of the process faster but many months of work is still
required to tie these together to deliver robust production infrastructure.

This project provides an example so you can get started quickly without having
to make many design choices. The aim is to standardize the approach and hence
achieve efficiency in delivery. There are nine independent yet coherent
modules:

## Quick Start Guide

### 1. Clone repo
```
isengard assume # select ml-proserve
conda create --name <name> python=3.7
conda activate <name>
git clone codecommit::us-east-1://mlmax
```

### 2. Instal dependencies
```
cd mlmax
pip3 install -r requirements.txt
```

### 3. Create the CloudFormation
```
cd modules/pipeline
python training_pipeline_create.py
python inference_pipeline_create.py
```

### 4. Deploy the CloudFormation
```
# ./deploy.sh <target_env> <s3_bucket>
./deploy.sh dev sagemaker-us-east-1-671846148176
```

### 5. Run the Training Pipeline
```
# python training_pipeline_run -e <target_env>
python training_pipeline_run.py dev
```

### 6. Run the Inference Pipeline
```
# python inference_pipeline_run -e <target_env>
python inference_pipeline_run.py dev
```
