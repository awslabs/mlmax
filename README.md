# ML Max
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

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg) ![Documentation Status](https://readthedocs.org/projects/mlmax/badge/?version=latest)](https://mlmax.readthedocs.io/en/latest/?badge=latest)


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

## Contributing

Please see [CONTRIBUTING](https://github.com/awslabs/mlmax/blob/main/CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License.

