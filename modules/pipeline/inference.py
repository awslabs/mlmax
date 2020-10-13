import os
import numpy as np
import json
import pandas as pd
from io import StringIO

try:
    from sklearn.externals import joblib
except:
    import joblib


# inference functions
def model_fn(model_dir):
    """
    This loads returns a Scikit-learn Classifier from a model.joblib file in
    the SageMaker model directory model_dir.
    """
    print("MODEL_FN")
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf


def _pre_processing(lines):
    arrs = []
    for line in lines:
        # we know it is CSV format
        line = line.strip()
        ds = line.split(",")
        if len(ds) < 2:
            break
        try:
            ds_arr = np.array([float(x) for x in ds])
        except:
            print(f"Fail to convert to float {line}")
            continue
        arrs.append(ds_arr)
    if len(arrs) == 0:
        print("use the single dummy input")
        return np.array(
            [
                [
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    -0.15995098710975894,
                    -0.23711755042386387,
                    -0.1683331768964402,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ]
            ],
            dtype=np.float,
        )
    else:
        print("return the multi-element array")
        return np.stack(arrs)


# please check "default" implementation of the following functions, and change as necessary
# https://github.com/aws/sagemaker-scikit-learn-container/blob/master/src/sagemaker_sklearn_container/serving.py

# from sagemaker_containers.beta.framework import content_types, encoders

# TODO try to comment out the "input_fn" function below, see what happens?
def input_fn(request_body, request_content_type):
    """
    Takes request data and de-serializes the data into an object for
    prediction.  When an InvokeEndpoint operation is made against an Endpoint
    running SageMaker model server, the model server receives two pieces of
    information:
        - The request Content-Type, for example "application/json"
        - The request data, which is at most 5 MB (5 * 1024 * 1024 bytes) in size.
    The input_fn is responsible to take the request data and pre-process it
    before prediction.
    Args:
        input_data (obj): the request data.
        content_type (str): the request Content-Type.
    Returns:
        (obj): data ready for prediction.
    """

    print("INPUT_FN")
    print(f"request_body (type is {type(request_body)}): {request_body}")
    if isinstance(request_body, bytes):
        request_body = request_body.decode()
        print(f"converted request_body to {type(request_body)}")
    print(f"request_content_type: {request_content_type}")
    lines = request_body.split(os.linesep)  # Split by lines
    print(f"nb of lines in request_body = {len(lines)}")
    arr_preprocessed = _pre_processing(lines)
    print(f"arr_preprocessed.shape = {arr_preprocessed.shape}")
    return arr_preprocessed


def output_fn(prediction, response_content_type):
    print("OUTPUT_FN")
    print(f"prediction type is {type(prediction)}")
    print(f"prediction shape is {prediction.shape}")
    print(f"prediction content type is {response_content_type}")
    print(f"prediction is {prediction}")
    strio = StringIO()
    print("strio = StringIO()")
    pd.DataFrame(prediction).to_csv(strio, header=False, index=False)
    return strio.getvalue()
