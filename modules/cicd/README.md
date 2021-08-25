# Set up the CICD for the ML pipelines

## High level Architecture

![cicd_architecture](images/cicd_architecture.png)

## Getting Started
> make sure your aws cli in the `us-east-1` region
1. Create the cloudformation stack for the CICD

    ```
    cd modules/cicd
    ./deploy.sh <PACKAGE_BUCKET>
    ```
    
2. Follow the instructions on https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-update.html to set up your github connection.

3. Go to your CodePipeline and release changes to trigger the running of the CodePipeline.
