FROM python:3.7-slim-buster

ARG PIP=pip3


# Installing numpy, pandas, scikit-learn, scipy
RUN ${PIP} --no-cache-dir install --upgrade pip

RUN ${PIP} install --no-cache --upgrade \
    numpy \
    pandas \
    scikit-learn==0.20.0 \
    boto3 \
    loguru


# Make sure python doesn't buffer stdout so we get logs ASAP.
ENV PYTHONUNBUFFERED=TRUE
ENTRYPOINT ["python3"]
