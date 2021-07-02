# Tests

## Unit test suite

The unit test suite is run via PyTest:

```$ pytest```

## SageMaker Local Mode tests

This test suite includes examples of SageMaker "Local Mode" tests. These tests run the core `mlmax` scripts in the same Docker container environment they will run within during deployment, but utilise SageMaker's "Local Mode" to run them on the local system.

This means that environment and integration issues associated with deployment can be quickly identified and fixed, *without* having to wait for deployment to the managed SageMaker cloud environment.

### Running the Local Mode tests

The tests can be run by including the `--smlocal` flag:

```$ pytest --smlocal```

Due to their additional environment requirements and running time, these tests will be skipped unless the `--smlocal` flag is specified.

### Environment requirements

In order to run the `--smlocal` tests:

- AWS credentials must be available in the test environment
- Docker must be running

### `--inspectlocal` mode

The SageMaker Local Mode tests can be run with an `--inspectlocal` flag. This flag will run the code within its container in Python's inspect mode (e.g. as if the script was called with`python -i entrypoint.py`).

This means that the container instance will not exit on script success or failure. Instead, the container will stay running and the container instance can be entered for manual inspection.

This can be incredibly useful for debugging SageMaker container-specific issues.

A typical way to enter the container would be via `bash`, e.g.:

```
$ docker ps  # identify container ID
$ docker exec -it /bin/bash <container ID>
```

Tests running in `--inspectlocal` mode must be manually ended with `ctrl-c` and closing any open connections to the
container.

To run a single test/container for inspection, it must be specified, e.g.:

```
$ pytest tests/mlmax/test_local_deployments.py -k test_preprocessing_script_in_local_container --smlocal --inspectlocal
```

### Further information

For further information on SageMaker local mode, please refer to the [AWS Blog](https://aws.amazon.com/blogs/machine-learning/use-the-amazon-sagemaker-local-mode-to-train-on-your-notebook-instance/), [SageMaker SDK documentation](https://sagemaker.readthedocs.io/en/stable/overview.html#local-mode), and [`amazon-sagemaker-local-mode` repository](https://github.com/aws-samples/amazon-sagemaker-local-mode).
