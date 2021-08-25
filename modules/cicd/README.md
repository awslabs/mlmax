# Set up the CICD for the ML pipelines

## High level Architecture

![cicd_architecture](images/cicd_architecture.png)

## Getting Started
> make sure your aws cli in the `us-east-1` region
### Step 1: Create the cloudformation stack for the Codepipeline (CI/CD)

    cd modules/cicd
    ./deploy.sh <PACKAGE_BUCKET>
    
### Step 2: The first time you set up the above CICD CodePipeline, you need too use the Developer Tools console to complete a pending connection.
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
