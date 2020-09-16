# mlmax

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

## Usage

For instructions on how to use the various modules, see the relevant subdirectories:

- [Training Pipeline](modules/pipeline/README.md)
- Inference Pipeline - Coming soon!
- [Environment](modules/env/regulated_environment/README.md)

For instructions on how to transfer a repo to another (non-isengard) repo, ou
can follow the steps in Part 1 of this [blog
post](https://aws.amazon.com/blogs/devops/replicating-and-automating-sync-ups-for-a-repository-with-aws-codecommit/)

## Contributing

Thank you for your interest in contributing! Please see the [contributing
guide](contributing.md) for more information.

## Notes on version management

This template hardcodes the version in `setup.py` as the baseline. However, we
recommend [versioneer](https://github.com/warner/python-versioneer/)
which is also used by some mature projects such as
[pandas](https://github.com/pandas-dev/pandas/).

Follow these [steps](https://github.com/warner/python-versioneer/blob/master/INSTALL.md).

## Misc. notes

Full-blown templates are maintained in branch `feature/fullblown-ds-project`.
