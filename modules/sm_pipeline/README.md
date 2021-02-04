# Readme

This is a quick start up guide on using sagemaker pipeline on your favourite IDE.

## Prequisite

- SSH to EC2 Deep Learning AMI
- git clone this repo
- Make sure vscode shell terminal is at `mlmax/modules/sm_pipeline` directory

## Setup

Run setup script to setup local directory to mirrow directory in sagemaker processing/training docker container. This will facilitate local testing to speed up testing iteration

```bash
pip install -r requirements.txt
./setup/setup.sh

```

## Execute Pipeline

This is a quick creation and execution of pipeline using default abalone dataset, which will preprocess, train, and evaluate the model.

```bash
python src/pipeline.py
```

Configurable parameters can be set in `pipeline.py` using directionary:

```python
execution = pipeline.start(
    parameters=dict(
        ProcessingInstanceType="ml.c5.xlarge",
        ModelApprovalStatus="Approved",
    )
```

## Development

This section demonstrate the standard development approach depending on the maturity of the python script at different stages.

### Local Standlone script development

Testing of standalone using normal python run or using VSCODE Debugger:

- To Run:

```bash
python src/preprocess.py
python src/train.py

# Copy model binary gzip from S3 to local /opt/ml/processing/model/model.tar.gz
python src/evaluate.py
```
