# Readme

This is a quick start up guide on using sagemaker pipeline on your favourite IDE.

## Prequisite

- SSH to EC2 Deep Learning AMI
- git clone this repo
- Make sure vscode shell terminal is at `mlmax/modules/sm_pipeline` directory

## Setup

Run setup script to setup local directory to mirrow directory in sagemaker processing/training docker container. This will facilitate local testing to speed up testing iteration

```bash
./setup/setup.sh

```

## Execute Pipeline

This is a quick creation and execution of pipeline using default abalone dataset, which will preprocess, train, and evaluate the model.

```bash
python pipeline.py
```

## Development - Processing

This section demonstrate the standard development approach depending on the maturity of the python script at different stages.

### 1. Local standlone script development

Testing of standalone using normal python run or using VSCODE Debugger:

- To Run:

```bash
python src/preprocess.py
```

- To Debug using "preprocess" profile in `launch.json`.

### 2. Local Test with SageMaker processors

Update the instance type to switch between `local` and `sagemaker` modes.

```bash
python test_sklearn_processor.py
```

## Development - Model Training

### 1. Local standlone training script development

- To Run:

```bash
python model.py
python train.py

```

- To Debug using "train" profile in `launch.json`.

### 2. Local Test with SageMaker processors

Update the instance type to switch between `local` and `sagemaker` modes. Set data channel to use either local file or download from S3.

```bash
python test_pytorch_training.py
```

## Development - Execute pipeline

To trigger the pipeline, update project and configurable parameters, then execute:

```bash
python pipeline.py
```
