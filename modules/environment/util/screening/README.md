# Sceening utility

Check that access has been granted for using key AWS resources for ML.

They are designed as independent notebooks to run in one go without a kernel restart.  Hence, they only submit short running jobs.

### [Screen Entrypoint](./screen-entrypoint.ipynb)

This notebook checks that you can submit a Python script as *train* and *processing*

### [Screen Train and Batch Transform](./screen-train-bt.ipynb)

This notebook checks that you can perform *train* -> *register model* -> *batch transform* -> *delete model*.

### [Screen PySpark on SageMaker notebook](./screen-pyspark-smnb.ipynb)

This notebook checks that you can run PySpark on a SageMaker notebook instance. This is NOT intended to screen a PySpark processing job.
