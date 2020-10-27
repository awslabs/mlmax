# MLMax

Delivering ML solutions to production is hard. It is difficult to know where to
start, what tools to use, and whether you are doing it right. Often each
individual professional does it a different way based on their individual
experience or they use prescribed tools developed within their company. Either
way this requires a lot of investment of time to firstly decide what to do and
secondly to implement and maintain the infrastructure. There are many existing
tools that make parts of the process faster but many months of work is still
required to tie these together to deliver robust production infrastructure.

This project provides an example so you can get started quickly without having
to make many design choices. The aim is to standardize the approach and hence
achieve efficiency in delivery.

## Architecture

The training and inference pipeline uses sagemaker within step functions as follows.

![arch](reports/figures/training-inference.png)

## Usage

For instructions on how to use please see [Training and Inference Pipeline](modules/pipeline/README.md)

## Contributing

Thank you for your interest in contributing! Please see the [contributing
guide](contributing.md) for more information.

