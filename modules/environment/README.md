# Development Environment

The Environment module manages the provisioning of resources and manages access
controls, providing the environment for data scientists and engineers to
develop solutions.

## Design Principles

| Principle                                          | Description                                                                                                                                                                                                                                                          |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Promote basic software development best practices. | Many data scientists come from a non-CS background, and thus it is important emphasize the benefit of tools and techniques of software development.                                                                                                                  |
| Provide a flexible set of baseline services.       | Data Scientists should be enabled to develop code in any environment capable to run remote python interpreter including modern IDEs (e.g., VS Code,), traditional IDEs (e.g., vim) or jupyter notebooks. There should not be a single, "one-size-fits-all" approach. |
| Operate in an isolated environment                 | This means resources will have to reside in a private VPC and VPC endpoints will need to be created.                                                                                                                                                                 |
| Data encryption in transit and at rest             | One aspect to enforce here is S3 encryption for all content at rest and requirement for data upload encryption header to be specified.                                                                                                                               |

## Quick Start

1) Update the following config in `config/config.ini`
    - KeyName: Existing EC2 key pair name that you have access to the private file
    - S3BucketName: Unique S3 bucket name for project
    - VpcCIDR: The Cidr range for the VPC

2) Prepare a S3 bucket in the same region to store cloudformation
intermediate metedata. This could be an existing bucket or a new bucket. You
must be able to write to this bucket. This is a different bucket than the one
specified in Step 1.

3) To deploy, run the command `deploy.sh [stack-name] [cloudformation-bucket] [region]`
   - Cloundformation bucket be in the same region specified by `region` argument.
   - If no `region` argument is provided, default region in `.aws/config` will be used.
   - E.g. `deploy.sh my-stack my-cfn-s3bucket ap-southeast-1`

## Architecture

Very often in a regulated industry such as Financial Services or Healthcare
where data security is critical, the customer will have stringent requirements
to be compliant for data science work. This template will setup the
minimum service such as bastianless EC2 instance, SageMaker Notebook and S3
bucket for Data Scientist to start working on customer engagement.

![](https://github.com/awslabs/mlmax/raw/main/modules/environment/images/vpc-without-internet.png)

**S3**

- Enforce service side encryption with customer managed key
- Data Scientist or developer is responsible to specify kmsid for AWSCLI, SDK or BOTO3 for any data upload to S3

**SageMaker**

- Encrypted EBS volume with customer manged key
- Restricted access to default encrypted S3 bucket

**VPC Endpoint**

The following endpoints have been added by default, additional endpoint can be added as necessary.

- s3
- git-codecommit, codecommit
- sagemaker.api, sagemaker.runtime
- ecr.api, ec.dkr
- sts
- logs
- ssm
- states

**KMS**

- Generate a customer managed key

**VPC**

- Two Private Subnets only across different avaiability zones

**EC2**

- SSM Agent to support remote SSH using exisitng key pair
- First verify that Session Manager Plugin is installed on your local workstation by running the command below or follow the instruction [here](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-verify) to install SSM agent
- Your current active aws profile keypair should be the same as the deployment profile.

```
aws ssm start-session --target <ec2-instance-id>
```

- Update SSH config to be able to SSH to EC2 using command `ssh ec2-ssm`.

```
# Add the following in your SSH config

Host ec2-ssm
    HostName <ec2-instance-id>
    User ec2-user
    IdentityFile /path/to/keypair/pemfile
    ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'"

```

## Security Patching

It is recommended that you patch the EC2 instance regularly whenever there is security updates. Run the following commands in EC2 for patching.

```
sudo yum-config-manager --disable libnvidia-container
sudo yum-config-manager --disable neuron
sudo yum-config-manager --disable nvidia-container-runtime
sudo yum-config-manager --disable nvidia-docker
sudo yum update-minimal --sec-severity=critical,important --bugfix
```
