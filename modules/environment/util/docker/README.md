# Developing with Docker

Create an interactive development environment with docker.

1. (Optional) Customize the requirements.txt to your liking
2. (Optional) update the Dockerfile (e.g., specify python version)
2. ```./build.sh && ./run.sh``` (requires internet access) to test out locally.
3. Push to your desired repository
4. Pull to into your development environment (e.g., EC2)
5. `./run.sh`

**Features:**
- amazon linux 2 base
- python version management with conda
- mount your current directory and aws credential directory
- AWS CDK installation
- zsh shell

Once it's set up, the command prompt should look something such as this:

![](https://github.com/awslabs/mlmax/raw/main/modules/environment/util/docker/images/cli.png)
