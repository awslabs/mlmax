# ML technology best practices

Delivering ML solutions to production is hard. It is difficult to know where to
start, what tools to use, and whether you are doing it right. Often each
individual professional does it a different way based on their individual
experience or they use prescribed tools developed within their company. Either
way this requires a lot of investment of time to firstly decide what to do and
secondly to implement and maintain the infrastructure. There are many existing
tools that make parts of the process faster but many months of work is still
required to tie these together to deliver robust production infrastructure.

This project provides an example so you can get started quickly without having
to make many design choices. The aim is to standardize the approach and hence
achieve efficiency in delivery. There are nine independent yet coherent
modules:

## Quick Start Guide
```
conda create --name <name> python=3.7
conda activate <name>
git clone codecommit::us-east-1://mlmax
cd mlmax
pip3 install -r requirements.txt
cd modules/pipeline
python training_pipeline_create.py
#./deploy.sh <region> <target_env> <stack_prefix>
./deploy.sh us-east-1 dev MlMax-Training-Pipeline-Demo
python training_pipeline_run.py
```

After creating the step function you should be able to execute the
step function. This can be done from the command line or the console.
