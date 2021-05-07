#!/bin/bash
IMAGE_NAME=data-science-env
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/opt/app ${IMAGE_NAME} zsh
