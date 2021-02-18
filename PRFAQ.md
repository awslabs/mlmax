## PRFAQ

Now ML Engineers and Data Scientists can quickly create and use
production-ready ML solutions on AWS. mlmax provides example templates for the
delivery of custom ML solutions to production so you can get started quickly
without having to make too many design choices.

**Q: What is the motivation for mlmax?**

Delivering ML solutions to production is hard. It is difficult to know where to
start, what tools to use, and whether you are doing it right. Often each
individual professional does it a different way based on their individual
experience or they use prescribed tools developed within their company. Either
way this requires a lot of investment of time to firstly decide what to do and
secondly to implement and maintain the infrastructure. There are many existing
tools that make parts of the process faster but many months of work is still
required to tie these together to deliver robust production infrastructure.

**Q: What is mlmax?**

ML Max is a set of example templates for the delivery of custom ML solutions to
production so customers can get started quickly without having to make too many
design choices.

**Q: What modules are currently implemented?**

1. **ML Training Pipeline**: This is the process to set up standard training
   pipelines for machine learning models enabling both immediate
experimentation, as well as tracking and retraining models over time.
2. **ML Inference Pipeline**: Deploys a model to be used by the business in
   production. Currently this is coupled quite closely to the ML training pipeline
as there is a lot of overlap.
3. **Development environment**: This module manages the provisioning of
   resources and manages networking and security, providing a the environment for data
scientists and engineers to develop solutions.

**Q: What is planned for the future?**

Future work will include additional features such as scheduling, metadata
management, and monitoring.

**Q: How can I use training and inference pipeline?**

There are a couple basic steps to go through to set up your training and
inference pipeline:

* **Define the workflow**: in this step you are defining the input and output
  placeholders, which will later be supplied during runtime.
* **Create the workflow**: in this step you will create the underlying
  infrastructure including the Step Machine State Machine
* **Define the inputs/outputs**: in this step you put the raw data onto S3, both
  for training and for inference.
* **Define the runtime scripts**: in this step you define the logic for
  preprocessing, evaluation, training and inference. These are python scripts
that can be run locally as well as within SageMaker.
* **Run the pipeline**: in this step you will create a Step Machine execution. It
  will upload the python files to S3 where they will be retrieved by the Step
Functions. All meta-data will be saved to S3 including the scripts, metrics,
model, and preprocessing model.

See [modules/pipeline](https://github.com/awslabs/mlmax/blob/main/modules/pipeline) for quick start documentation.

**Q: What are the design principles that the Training and Inference pipeline was
created with?**

* **Separate definition and runtime for training and inference pipelines.** This
  enable effective collaboration between the ML Ops Engineer and the Data
Scientist. The ML Engineer can focus on managing and versioning the underlying
infrastructure and the Data Scientist can focus on the development of the ML
model, the input data, and logic for the data, preprocessing and evaluation.
* **Ensure the same code for pre-processing can be used for training and
  inference.** The exact some logic for data transformation needs to be used for
training and inference time so that the consistency of results is achieved
without silent errors.
* **Enforce traceability between components of the training and inference
  pipelines.** Training job should point to which code was used for
pre-processing, which set of data was used to source it, etc... 
* **Code should provide reproducible results wherever it is run.** Code should be
  able to be run locally, within EC2, on SageMaker, etc... This enables easy
development, and debugging.
* **Promote modularity in the development of Training and Inference solutions.**
  There are separate steps for the each of the core components of the pipeline
including preprocessing, training, inference, and evaluation. Where there is
overlap, components are reused.

