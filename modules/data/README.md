# Data Management and ETL

This module determines how the machine learning operations interacts with the
data stores, both to ingest data for processing, managing feature stores, and
for processing and use of output data. A common pattern is to take an extract,
or mirror, of the data into S3 on a project basis.

## Quick Start

**1. Clone repo**
```
conda create --name <name> python=3.7
conda activate <name>
git clone https://github.com/awslabs/mlmax.git
```

**2. Install dependencies**
```
cd mlmax/modules/data
pip install -r requirements.txt
```

**3. Create the CloudFormation**
```
python data_pipeline_create.py
```

**4. Deploy the CloudFormation**

You will need an S3 bucket for this step. After the deployment, `the pipeline will be scheduled to run daily`.

```
# ./deploy.sh <target_env> <s3_bucket>
# ./deploy.sh dev sagemaker-us-east-1-1234
```

**5. Manually Run the Data Pipeline**
```
# python data_pipeline_run -e <target_env>
python data_pipeline_run.py dev
```
