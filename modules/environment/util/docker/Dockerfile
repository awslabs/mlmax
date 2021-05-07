FROM amazonlinux:2
RUN yum update -y
RUN yum install -y \
        shadow-utils.x86_64 \
        zip unzip \
        gcc-c++ \
        make \
        openssl-devel \
        zlib-devel \
        readline-devel \
        git \
        blas blas-devel \
        lapack lapack-devel \
        wget \
        zsh \
        which \
        tmux \
        tar

# Install the AWS CDK
# ---------------------
RUN curl -sL https://rpm.nodesource.com/setup_10.x | bash - \
    && yum install -y nodejs \
    && npm install -g aws-cdk@1.97

# Install Miniconda
# ---------------------
ENV CONDA_DIR=/opt
ENV ENV_NAME=mlmax
ENV PYVERSION=3.8
RUN mkdir -p "${CONDA_DIR}"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O \
        "$CONDA_DIR/miniconda.sh"
RUN bash "$CONDA_DIR/miniconda.sh" -b -u -p "$CONDA_DIR/miniconda"

# Create conda environment
RUN source "$CONDA_DIR/miniconda/bin/activate" \
        && conda create -y -n $ENV_NAME python=$PYVERSION

# Set up zsh shell
# ---------------------
RUN wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O /opt/install.sh
RUN bash /opt/install.sh
RUN echo 'source "$CONDA_DIR/miniconda/bin/activate"' >> ~/.zshrc
RUN echo 'conda activate $ENV_NAME' >> ~/.zshrc

# Install python packages into conda env
# ---------------------
COPY requirements.txt /opt
RUN ${CONDA_DIR}/miniconda/envs/${ENV_NAME}/bin/pip install -r /opt/requirements.txt
# Alternatively, use conda installation
# RUN source "$CONDA_DIR/miniconda/bin/activate" \
#         && conda activate $ENV_NAME \
#         && conda install -y --file /opt/requirements.txt

# Copy over configuration files
# ---------------------
COPY .tmux.conf /root/.tmux.conf

WORKDIR /opt/app
