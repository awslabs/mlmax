# Base container
FROM python:3.6

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Set up the program in the image
RUN mkdir -p /opt/program
WORKDIR /opt/program
COPY requirements.txt /opt/program/requirements.txt
RUN pip3 --no-cache-dir install -r /opt/program/requirements.txt

# Copy all application file
COPY . /opt/program/