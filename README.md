# ML Max

ML Max is a set of example templates to accelerate the delivery of custom ML
solutions to production so you can get started quickly without having to make
too many design choices.

![](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![](https://img.shields.io/github/workflow/status/awslabs/mlmax/main/main)
![](https://readthedocs.org/projects/mlmax/badge/?version=latest)
![](https://img.shields.io/github/v/release/awslabs/mlmax.svg)
![](https://img.shields.io/badge/code_style-black-000000.svg)

## Quick Start

1. [**ML Training
   Pipeline**](https://github.com/awslabs/mlmax/blob/main/modules/pipeline/):
This is the process to set up standard training pipelines for machine learning
models enabling both immediate experimentation, as well as tracking and
retraining models over time.
2. [**ML Inference
   Pipeline**](https://github.com/awslabs/mlmax/blob/main/modules/pipeline/):
Deploys a model to be used by the business in production. Currently this is
coupled quite closely to the ML training pipeline as there is a lot of overlap.
3. [**Development
   environment**](https://github.com/awslabs/mlmax/blob/main/modules/environment/):
This module manages the provisioning of resources and manages networking and
security, providing the environment for data scientists and engineers to
develop solutions.
4. [**Data Management and
   ETL**](https://github.com/awslabs/mlmax/blob/main/modules/data): This module
determines how the machine learning operations interacts with the data stores,
both to ingest data for processing, managing feature stores, and for processing
and use of output data. A common pattern is to take an extract, or mirror, of
the data into S3 on a project basis.

## Help and Support

* [Documentation](https://mlmax.readthedocs.io/en/latest/index.html#)
* [Contributing](https://github.com/awslabs/mlmax/blob/main/CONTRIBUTING.md)
* [License](https://github.com/awslabs/mlmax/blob/main/LICENSE)
