# Set up the CICD for the ML pipelines

## High level Architecture

![cicd_architecture](images/cicd_architecture.png)

The CICD can be set up using a AWS codepipeline, as shown in the chart, it involves 5 accounts: (The accounts in red are needed to be created)

- `Devops Account`: The account manages the build and deployment of the mlops.

- `ML DEV Account`: The account data scientists and ML engineers can experiment their ML/AI models and pipelines.

- `ML Staging Account`: The account where the automated model training and testing happens.

- `ML Production Account`: The account where the production ML inference pipeline is deployed.

- `Data/Arifacts Account`: The account manages the datalake, model artefacts and ML model predictions.

Also it consists of 5 stages:

- `Build`: In this stage, when there is new changes pushed into the git repo, the codeBuild is used to build the cloudformation templates for the training and inference pipelines.

- `Train`: In this stage, the training pipeline in the staging account is automatically triggered and a model is trained.

- `Inference/Test`: In this stage, the inference pipeline in the staging account is automatically triggered and it uses the trained model to do inference. This is a good integration test to see if the inference pipeline works fine, and check if the trained model and inference pipeline are ready to be deployed into production.

- `Manual Approval`: In this stage, add the manual approval to ensure everything is fine before the deployment.

- `Deploy`: Deploy the ML inference pipeline into the production account.

**For simplicity, this implementation assume all the accounts are the same here.**

## Getting Started
> make sure your aws cli in the `us-east-1` region

### Step 1: Set up cross account IAM roles

#### In `Devops Account` AWS cli, run the command line below:


    source config/cicd.ini
    TARGET_ENV="devops"
    aws cloudformation deploy \
      --region=${Region} \
      --stack-name ${StackNameRoles}-${TARGET_ENV} \
      --template-file ./cicd_roles.yaml \
      --parameter-overrides $(cat config/cicd.ini) TargetEnv=${TARGET_ENV} \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

#### In `Stage Account` AWS cli, run the command line below:

    source config/cicd.ini
    TARGET_ENV="stage"
    aws cloudformation deploy \
      --region=${Region} \
      --stack-name ${StackNameRoles}-${TARGET_ENV} \
      --template-file ./cicd_roles.yaml \
      --parameter-overrides $(cat config/cicd.ini) TargetEnv=${TARGET_ENV} \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND


#### In `Prod Account` AWS cli, run the command line below:

    source config/cicd.ini
    TARGET_ENV="prod"
    aws cloudformation deploy \
      --region=${Region} \
      --stack-name ${StackNameRoles}-${TARGET_ENV} \
      --template-file ./cicd_roles.yaml \
      --parameter-overrides $(cat config/cicd.ini) TargetEnv=${TARGET_ENV} \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND

### Step 2: Set up cross account S3 bucket for CodePipeline Artifacts, Go to the Devops Account AWS console.

To do:
- Automate adding the S3 bucket policy.

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::161422014849:role/mlmax-demo-cicd-pipeline-roles-deploy-role",
                    "arn:aws:iam::497394617784:role/mlmax-demo-cicd-pipeline-roles-deploy-role",
                    "arn:aws:iam::161422014849:role/mlmax-demo-cicd-pipeline-roles-InvokeStepFunctionRole",
                    "arn:aws:iam::497394617784:role/MlMaxPipelineDemo-SageMakerRole-prod",
                    "arn:aws:iam::161422014849:role/MlMaxPipelineDemo-SageMakerRole-stage"
                ]
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::sagemaker-us-east-1-783128296767",
                "arn:aws:s3:::sagemaker-us-east-1-783128296767/*"
            ]
        }
    ]
}

### Step 3: Go to the Devops Account, Create the cloudformation stack for the Codepipeline (CI/CD)

    cd modules/cicd
    ./deploy.sh <PACKAGE_BUCKET>

### Step 4: The first time you set up the above CICD CodePipeline, you need too use the Developer Tools console to complete a pending connection.
1. Open the AWS Developer Tools console at https://console.aws.amazon.com/codesuite/settings/connections.

2. Choose **Settings > Connections**. The names of all connections associated with your AWS account are displayed.

3. In Name, choose the name of the pending connection you want to update. Update a pending connection is enabled when you choose a connection with a Pending status.

4. Choose Update a pending connection.

5. Choose **Authorize AWS Connector for GitHub**. The connection page displays and shows the GitHub Apps field.
![github-conn-access.png](images/github-conn-access.png)

6. Under GitHub Apps, choose an app installation or choose **Install a new app** to create one.
![github-conn-access-app.png](images/github-conn-access-app.png)

7. On the Install AWS Connector for GitHub page, choose the account where you want to install the app.
![github-conn-access-app-install1.png](images/github-conn-access-app-install1.png)

8. On the Install AWS Connector for GitHub page, leave the defaults, and choose Install.
![github-conn-access-app-install2.png](images/github-conn-access-app-install2.png)

9. On the **Connect to GitHub page**, the connection ID for your new installation appears in GitHub Apps. Choose **Connect**.

### Step 3: Go to your CodePipeline and release changes to trigger the running of the CodePipeline.
1. open the CodePipeline console at http://console.aws.amazon.com/codesuite/codepipeline/home.

2. In Name, choose `mlmax-demo-cicd-pipeline-codepipeline`.

3. On the pipeline details page, choose Release change. This starts the most recent revision available in each source location specified in a source action through the pipeline.
![codepipeline-screenshot.png](images/codepipeline-screenshot.png)

### Step 4: Check the run results.


## To do
- Support deploy in multiple regions
- Add support fork from mlmax to automatically trigger the Codepipeline
- Clean the cicd.ini and deploy-xxx-xxx.ini to avoid duplicate parameters
- Automatically create s3 artifact bucket.
