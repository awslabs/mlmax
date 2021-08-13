# Data Management and ETL

This module determines how the machine learning operations interact with the
data stores to ingest data for processing, manage feature stores, and
for processing and use of output data. A common pattern is to take an extract,
or mirror of the data into S3 on a per project basis.

## Quick Start

**Prerequisites:**

The data used in this example is taken from the [NYC TLC Trip Record Data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page), which was downloaded using the tools provided by https://github.com/toddwschneider/nyc-taxi-data. These tools can be used to download the entire dataset from scratch, or to update an existing dataset.

You will need to upload the dataset to an S3 bucket. The folder structure should look something like this:

```
$ aws s3 ls s3://S3InputBucket/S3InputPrefix/ --human-readable
                           PRE unaltered/
2020-10-13 13:47:21  364.0 KiB central_park_weather.csv
2020-10-13 13:47:21   45.7 KiB fhv_bases.csv
2020-10-13 13:47:21   81.8 MiB fhv_tripdata_2015-01.csv
2020-10-13 13:47:21   93.3 MiB fhv_tripdata_2015-02.csv
...
2020-10-13 13:51:20    1.2 GiB fhvhv_tripdata_2019-02.csv
2020-10-13 13:51:20    1.4 GiB fhvhv_tripdata_2019-03.csv
...
2020-10-13 13:53:16    1.1 MiB green_tripdata_2013-08.csv
2020-10-13 13:53:17    7.3 MiB green_tripdata_2013-09.csv
...
2020-10-13 13:54:32    2.4 GiB yellow_tripdata_2009-01.csv
2020-10-13 13:54:32    2.2 GiB yellow_tripdata_2009-02.csv
...
2020-10-13 14:21:57   30.2 MiB yellow_tripdata_2020-05.csv
2020-10-13 14:21:58   47.9 MiB yellow_tripdata_2020-06.csv
```

**1. Clone repo**
```
conda create -y -n <name> python=3.7
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
