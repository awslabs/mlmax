.PHONY: clean create_env install_rain install_scheduler_cli docker install_pd_profiler

#################################
# Assumption:
# Commands are run on MacOS
# Python3 version is defaulted to MacOS python installation
#################################
PYTHON_INTERPRETER = python3

# Build docker images and send to ECR
docker:
	cd container; ./build_docker.sh $(image_name)
	@echo Completed building docker $(image_name)

## Create virtual env
create_env:
	#rm -rf ./.env
	python3 -m venv .env
	source .env/bin/activate; pip install -r requirements.txt
	@echo "Environment completed - You can set IDE to use the new virtual environment"

## Install Panda Profiler
install_pd_profiler:
	mkdir -p library_source
	wget https://github.com/pandas-profiling/pandas-profiling/archive/master.zip -O library_source/master.zip
	unzip -o library_source/master.zip -d library_source/
	cd library_source/pandas-profiling-master; $(PYTHON_INTERPRETER) setup.py install
	$(PYTHON_INTERPRETER) -m pip show pandas-profiling
	rm -rf library_source

## Install Rain 
install_rain:
	mkdir -p rain_source
	wget https://github.com/aws-cloudformation/rain/releases/download/v0.7.2/rain-v0.7.2_osx-i386.zip -O rain_source/rain.zip
	unzip -o rain_source/rain.zip -d rain_source/
	cp rain_source/dist/rain-v0.7.2_osx-i386/rain /usr/local/bin/
	rm -rf ./rain_source
	@echo "Installation completed - rain"

## Install Schedule CLI
install_scheduler_cli:
	mkdir -p ./scheduler_cli
	wget https://s3.amazonaws.com/solutions-reference/aws-instance-scheduler/latest/scheduler-cli.zip -O scheduler_cli/scheduler_cli.zip
	unzip -o scheduler_cli/scheduler_cli.zip -d scheduler_cli/
	# each line trigger subprocess
	cd scheduler_cli; $(PYTHON_INTERPRETER) setup.py install
	rm -rf ./scheduler_cli
	@echo "Installation completed - ec2 scheduler"

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete