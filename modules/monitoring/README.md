# Data Monitoring

This module demonstrate data monitoring using custom container which can be added into your existing pipeline.
It is created to be run as standalone module which can be added into pipeline module.

Currently this module calculate the following metrics which can be used to perform model update decision:

- Training data - statistic
- Inference data - Population Stability Index (PSI)

You can customize the docker container located at `modules/monitoring/docker/Dockerfile` to include addtional python packages.

## Prerequisite

Check that you have local docker server running with `docker info`.

## Quick Start

**1. Clone repo**

```bash
conda create -y -n <name> python=3.7
conda activate <name>
git clone https://github.com/awslabs/mlmax.git
```

**2. Install dependencies**

```bash
cd mlmax/modules/monitoring
pip install -r requirements.txt
```

**3. Create the CloudFormation**

```bash
python monitor_pipeline_create.py
```

**4. Deploy the CloudFormation**

You will need an S3 bucket for this step.

```bash
# ./deploy.sh <target_env> <s3_bucket>
./deploy.sh dev sagemaker-us-east-1-1234
```

**5. Manually Run the Monitor Pipeline**

```bash
# python monitor_pipeline_run -e <target_env>
python monitor_pipeline_run.py dev
```
