# Data Monitoring

This module demonstrate data monitoring using custom container. It is created to be run as standalone module which can be added into pipeline module.

Currently this module calculate the following baseline metrics:

- Features statistic
- Features Population Stability Index (PSI)

These metrics can then be used to compared against new inference data to identify data drift and perform necessary action based on predefined threshold.

You can customize the docker container located at `modules/monitoring/docker/Dockerfile` to include addtional python packages.

## Prerequisite

- Check that you have local docker server running with `docker info`.
- Update configuration in `modules/monitoring/config/deploy-ap-southeast-1-dev.ini`
  - `InputSource`: Baseline training data
  - `InferSource`: Inference data
  - `MonitorS3Bucket`: S3 Bucket to store monitoring baseline and inference output
  - `MonitorS3Prefix`: S3 prefix to store monitoring baseline and inference output

## Monitoring Metrics

### Baseline statistic

This is located in `<MonitorS3Bucket>/<MonitorS3Prefix>/baseline/statistic_baseline.json`.

```json
{
    "features": [
        {
            "name": "age",
            "statistic": {
                "count": 47799.0,
                "unique": "nan",
                "top": "nan",
                "freq": "nan",
                "mean": 44.187744513483544,
                "std": 15.702569095352446,
                "min": 1.0,
                "25%": 32.0,
                "50%": 43.0,
                "75%": 54.0,
                "max": 90.0,
                "nan": 0.0,
                "nan_ratio": 0.0,
                "skew": 0.4519749826293985,
                "kurtosis": -0.32770842653116317,
                "distribution": {
                    "numerical": [
                        {
                            "lower_bound": 1.0,
                            "upper_bound": 9.9,
                            "count": 6
                        },
                        {
                            "lower_bound": 9.9,
                            "upper_bound": 18.8,
                            "count": 1223
                        },
                        {
                            "lower_bound": 18.8,
                            "upper_bound": 27.7,
                            "count": 5772
                        },
                        {
                            "lower_bound": 27.7,
                            "upper_bound": 36.6,
                            "count": 9834
                        },
                        {
                            "lower_bound": 36.6,
                            "upper_bound": 45.5,
                            "count": 10427
                        },
                        {
                            "lower_bound": 45.5,
                            "upper_bound": 54.4,
                            "count": 8604
                        },
                        {
                            "lower_bound": 54.4,
                            "upper_bound": 63.3,
                            "count": 5719
                        },
                        {
                            "lower_bound": 63.3,
                            "upper_bound": 72.2,
                            "count": 3654
                        },
                        {
                            "lower_bound": 72.2,
                            "upper_bound": 81.1,
                            "count": 1892
                        }
                    ]
                }
            }
        },
```

### Baseline PSI

This is located in `<MonitorS3Bucket>/<MonitorS3Prefix>/baseline/statistic_baseline.json`.

```json
{
    "features": [
        {
            "name": "age",
            "psi": 0.000531655721643536
        },
        {
            "name": "num persons worked for employer",
            "psi": 0.00020281245865055929
        },
        {
            "name": "capital gains",
            "psi": 0.00025810223141283157
        },
        {
            "name": "capital losses",
            "psi": 0.00039750434442899896
        },
        {
            "name": "dividends from stocks",
            "psi": 0.0002493252588265323
        }
    ]
}
```

## Directory Mapping

The following is the expected input/output for `monitoring.py` python script. You can find the output of interested mainly in `/opt/ml/processing/profiling/` which is copied to `s3://<MonitorS3Bucket>/<MonitorS3Prefix>/`.

### Training mode

Takes in training data as input, and generate baseline statistic as output.

| Input                          | Output                        |
| ------------------------------ | ----------------------------- |
| /opt/ml/processing/train_input | /opt/ml/processing/profiling/ |
| /opt/ml/processing/input/code  |                               |

### Inference mode

Takes in baseline statistic and inference data as input, and score new PSI as output.

| Input                          | Output                                 |
| ------------------------------ | -------------------------------------- |
| /opt/ml/processing/infer_input | /opt/ml/processing/profiling/inference |
| /opt/ml/processing/profiling/  |                                        |

## Quick Start

**1. Clone repo**

```bash
conda create -y -n <name> python=3.7
conda activate <name>
git clone https://github.com/awslabs/mlmax.git
```

**2. Install dependencies**

```bash
# At project root directory
cd mlmax
pip install -r requirements.txt
pip install -e .
```

**3. Create the CloudFormation**

```bash
cd modules/monitoring
python monitor_pipeline_create.py
```

**4. Deploy the CloudFormation**

You will need an S3 bucket for this step.

```bash
# ./deploy.sh <target_env> <s3_bucket>
./deploy.sh dev  sagemaker-ap-southeast-1-xxxx
```

**5. Manually Run the Monitor Pipeline**

```bash
# python monitor_pipeline_run -e <target_env>
python monitor_pipeline_run.py dev
```
