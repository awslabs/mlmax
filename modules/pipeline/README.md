# ML Training and Inference Pipeline

The Training module manages the process to set up standard training pipelines
for machine learning models enabling both immediate experimentation, as well as
tracking and retraining models over time.The Inference module deploys a model
to be used by the business in production. Often this is coupled quite closely
to the ML training pipeline as there is a lot of overlap.


## Design Principles

| Principle                                                                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Separate definition and runtime for training/inference pipelines.              | One anti-pattern we have observed is that of the unicorn data scientist. This person is asked to do everything, from seeking business value, to developing models, to provisioning infrastructure. Creating a seperation of concerns between the individuals responsible for engineering the pipeline and individuals responsible for building the model recognizes the unique value that Data Scientist and ML Engineer provides while creating a work environment that stimulates collaboration.                                                                                          |
| Use the same code for pre-processing in training and inference                 | The majority of time in most ML projects is allocated to data collection, data engineering, label and feature engineering. It is vital to ensure that the same code/logic is used by both the training and inference pipeline so that there are no opportunities for human errors and inconsistencies.                                                                                                                                                                                                                                                                                      |
| Traceability between components of the training and inference pipelines.       | A well-governed machine learning pipelines provide clear lineage for all components of the training and inference pipeline definition and runtime. For the runtime traceability training pipeline and inference pipelines. Which data sources were used for training? What modelling techniques were used? What type of preprocessing was used? Where are the artifact’s stored? From the perspective of the pipeline definition, changes applied to pipelines should be tracked using versioning.                                                                                          |
| Code should provide consistent results wherever it is run.                     | Data Scientists are used to programming in an environment that allows them interactively explore the data and get rapid results. Data engineers are used to submitting jobs that run end-to-end, anticipating what might happen and including appropriate measures for ensuring that the process is robust. It is important to keep both of these divergent approaches in mind when considering how to design a training and inference pipeline. A well designed Training and Inference pipeline will make it relatively easy to run the code and get consistent results in both scenarios. |
| Promote modularity in the development of Training and Inference solutions.     | Training and inference pipelines can be broken down into several components such as data validation, data preprocessing, data combination, etc.... When designing training and inference pipelines it is important that these components are created such that they can be developed, tested, and maintained independently from one another.                                                                                                                                                                                                                                                |
| Use on-demand compute, only paying for it when you need it for a specific job. | One of the anti-patterns we have observed is the attempt to treat the cloud as the same as an on-premise cluster of compute resources. But the cloud allows for fine-grained security and cost-control measures to decentralize the utilization of cloud resources. This enable cost-savings resulting from a pay-as-you-go model and empowers a growing Data Science organization to harness the power of cloud computing.                                                                                                                                                                 |

## Quick Start

**1. Clone repo**
```
conda create --name <name> python=3.7
conda activate <name>
git clone https://github.com/awslabs/mlmax.git
```

**2. Install dependencies**
```
cd mlmax/modules/pipeline
pip install -r requirements.txt
```

**3. Create the CloudFormation**
```
cd modules/pipeline
python training_pipeline_create.py
python inference_pipeline_create.py
```

**4. Deploy the CloudFormation**

You will need an S3 bucket for this step.

```
# ./deploy.sh <target_env> <s3_bucket>
# ./deploy.sh dev sagemaker-us-east-1-1234
```

**5. Run the Training Pipeline**
```
# python training_pipeline_run -e <target_env>
python training_pipeline_run.py dev
```

**6. Run the Inference Pipeline**
```
# python inference_pipeline_run -e <target_env>
python inference_pipeline_run.py dev
```

## Architecture

The ML training and inference pipeline consists of Amazon Sakemaker running
within Step Functions. The code included in this module:
- Generates the Cloudformation for the training and inference pipeline using
  the Data Science Step Functions SDK.
- Packages and deploys the Cloudformation, (creating the State Machines).
- Runs the traning and inference pipeline (executing the State Machines).

![](https://github.com/awslabs/mlmax/raw/main/modules/pipeline/images/training-inference.png)
