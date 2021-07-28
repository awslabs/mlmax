# Tests

## Unit test suite

The unit test suite is run via PyTest from the project root directory:

```bash
user@machine:mlmax$ pytest
```

## SageMaker Local Mode tests

This test suite includes examples of SageMaker "Local Mode" tests. These tests run the core `mlmax` scripts in the same Docker container environment they will run within during deployment, but utilise SageMaker's "Local Mode" to run them on the local system.

This means that environment and integration issues associated with deployment can be quickly identified and fixed, *without* having to wait for deployment to the managed SageMaker cloud environment.

### Running the Local Mode tests

The tests can be run by including the `--smlocal` flag:

```bash
user@machine:mlmax$ pytest --smlocal
```

Due to their additional environment requirements and running time, these tests will be skipped unless the `--smlocal` flag is specified.

### Environment requirements

In order to run the `--smlocal` tests:

- AWS credentials must be available in the test environment
- Docker must be running

### `--inspectlocal` mode

The SageMaker Local Mode tests can be run with an `--inspectlocal` flag. This flag will run the code within its container in Python's inspect mode (e.g. as if the script was called with`python -i entrypoint.py`).

This means that the container instance will not exit on script success or failure. Instead, the container will stay running and the container instance can be entered for manual inspection.

This can be incredibly useful for debugging SageMaker container-specific issues.

However, this does mean that the test will effectively hang, and must be manually ended with `ctrl-c` and closing any open Docker connections to the
container. A walkthrough of this process is provided below.

#### Typical workflow

A typical workflow for an `--inspectlocal` call is as follows:

1. The specific test/container to be inspect is specified with the `-k` flag, and the `--smlocal` and `--inspectlocal` flags are appended:

The test framework will begin, announce that the test is being run, and appear to hang:

```bash
user@machine:mlmax$ pytest tests/mlmax/test_local_deployments.py -k test_preprocessing_script_in_local_container --smlocal --inspectlocal
> =============== test session starts ===================
> platform darwin -- Python 3.7.10, pytest-6.2.4, py-1.10.0, pluggy-0.13.1 -- /Users/user/Projects/mlmax/venv/bin/python
> cachedir: .pytest_cache
> rootdir: /Users/user/Projects/mlmax, configfile: tox.ini
> plugins: cov-2.12.1, datatest-0.11.1
>
> collected 4 items / 3 deselected / 1 selected
>
> tests/mlmax/test_local_deployments.py::test_inference_script_in_local_container
```
2. A new terminal must now be opened.
   In this new terminal, the ID for the container just launched is identified with the `docker ps` command:

```bash
user@machine:mlmax$ docker ps  # identify container ID
> CONTAINER ID   IMAGE                                                                                     COMMAND                  CREATED         STATUS         PORTS     NAMES
> e1e0c76cc5f5   783357654285.dkr.ecr.ap-southeast-2.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3   "python3 /opt/ml/pro…"   3 minutes ago   Up 3 minutes             elpuqgbzps-algo-1-kdmha
```

3. The container can now be entered via the `docker exec` command, e.g.:

```bash
user@machine:mlmax$ docker exec -it e1e0 /bin/bash  # Note that a shortened version of the ID can be used
root@e1e0c76cc5f5:/#  # Now in a Bash terminal inside the container - ready for inspection and debugging
```

At this point the container can be explored via typical `bash` commands:

```bash
root@e1e0c76cc5f5:/# ls /opt/ml/code
> train.py
```

4. When inspection and debugging is complete, the `bash` terminal running inside the container must be closed:

```bash
root@e1e0c76cc5f5:/# exit
> exit
user@machine:mlmax$
```

5. Finally, the test framework in the **original** terminal must be manually shut down with `ctrl-c`, marked by `^C` in the example below:

```bash
> =============== test session starts ===================
> platform darwin -- Python 3.7.10, pytest-6.2.4, py-1.10.0, pluggy-0.13.1 -- /Users/user/Projects/mlmax/venv/bin/python
> cachedir: .pytest_cache
> rootdir: /Users/user/Projects/mlmax, configfile: tox.ini
> plugins: cov-2.12.1, datatest-0.11.1
>
> collected 4 items / 3 deselected / 1 selected
>
> tests/mlmax/test_local_deployments.py::test_inference_script_in_local_container ^C
> !!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!
> /Users/user/Projects/mlmax/venv/lib/python3.7/site-packages/sagemaker/local/image.py:889: KeyboardInterrupt
```

### Further information

For further information on SageMaker local mode, please refer to the [AWS Blog](https://aws.amazon.com/blogs/machine-learning/use-the-amazon-sagemaker-local-mode-to-train-on-your-notebook-instance/), [SageMaker SDK documentation](https://sagemaker.readthedocs.io/en/stable/overview.html#local-mode), and [`amazon-sagemaker-local-mode` repository](https://github.com/aws-samples/amazon-sagemaker-local-mode).
