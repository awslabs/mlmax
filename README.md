# What is ML Max?
Delivering ML solutions to production is hard. It is difficult to know where to
start, what tools to use, and whether you are doing it right. Often each
individual professional does it a different way based on their individual
experience or they use prescribed tools developed within their company. Either
way this requires a lot of investment of time to firstly decide what to do and
secondly to implement and maintain the infrastructure. There are many existing
tools that make parts of the process faster but many months of work is still
required to tie these together to deliver robust production infrastructure.

ML Max is a set of example templates to accelerate the delivery of custom ML solutions to
production so you can get started quickly without having to make too many
design choices.


## Quick Start Usage

1. [**ML Training Pipeline**](https://github.com/awslabs/mlmax/blob/main/modules/pipeline): This is the process to set up standard training
   pipelines for machine learning models enabling both immediate
experimentation, as well as tracking and retraining models over time.
2. [**ML Inference Pipeline**](https://github.com/awslabs/mlmax/blob/main/modules/pipeline): Deploys a model to be used by the business in
html_theme = "alabaster"
   production. Currently this is coupled quite closely to the ML training pipeline
as there is a lot of overlap.
3. [**Development environment**](https://github.com/awslabs/mlmax/blob/main/modules/environment): This module manages the provisioning of
   resources and manages networking and security, providing the environment for data
scientists and engineers to develop solutions.

## Training and Inference Pipeline

Create a semi-automated Training and Inference Pipeline using CloudFormation,
Step Functions, and Amazon SageMaker. 

![arch](https://github.com/awslabs/mlmax/raw/main/reports/figures/training-inference.png)

See [quick start documentation](https://github.com/awslabs/mlmax/blob/main/modules/pipeline) for details.

## Environment

Get started with a working environment with encryption and network isolation.

![arch](https://github.com/awslabs/mlmax/raw/main/modules/environment/images/architecture.png)

See [quick start documentation](https://github.com/awslabs/mlmax/blob/main/modules/environment) for details.

## Links

* [Creating a Training and Inference Pipeline](https://github.com/awslabs/mlmax/blob/main/modules/pipeline)
* [Setting up an Environment](https://github.com/awslabs/mlmax/blob/main/modules/environment)
* [PR FAQ](PRFAQ.md)
* [Configuring your Jupyter Notebook](https://github.com/awslabs/mlmax/blob/main/notebooks/example_notebook.ipynb)
* [Best Practices](https://github.com/awslabs/mlmax/blob/main/BEST_PRACTICES.md)
* [Contributing](https://github.com/awslabs/mlmax/blob/main/CONTRIBUTING.md)

## Security

See [CONTRIBUTING](https://github.com/awslabs/mlmax/blob/main/CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

