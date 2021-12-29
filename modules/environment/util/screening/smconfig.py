from typing import Any, Dict, List

from sagemaker.network import NetworkConfig

# typedefs
Kwargs = Dict[str, Any]
Tag = Dict[str, str]
Tags = List[Tag]
VpcConfig = Dict[str, List[str]]

# Change me!
s3_bucket = (
    "s3://abcd"  # or os.environ['S3_BUCKET'], depending on your particular setup.
)


class SmPrivateKwargs:
    """Change me!"""

    def __init__(
        self,
        role: str,
        subnets: List[str] = ["subnet-abcde"],
        network_isolation: bool = False,
        s3_kms_key: str = "abcde",
        sgs: List[str] = ["sg-abcde"],
        volume_kms_key: str = "abcde",
        encrypt_inter_container_traffic: bool = True,
        tag_team: str = "team_A",
        tag_project: str = "project_X",
    ) -> None:
        """Return mandatory kwargs to run SageMaker jobs on this particular AWS account.

        Args:
            role (str): SageMaker role.
            subnets (List[str], optional): List of subnets. Defaults to
                ["subnet-abcde"].
            network_isolation (bool, optional): Network isolation. Defaults to False.
            s3_kms_key (str, optional): KMS key for S3. Per the API documentation
                (https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputDataConfig.html#sagemaker-Type-OutputDataConfig-KmsKeyId),
                if not provided, SageMaker uses the default KMS key for Amazon S3 of the
                account linked to your IAM role. Also according to the same
                documentation, the accepted formats are (1) KMS Key ID, (2) ARN of a KMS
                key, (3) KMS Key alias, and (4) ARN of a KMS key alias. Defaults to
                "abcde".
            sgs (List[str], optional): List of security groups. Defaults to
                ["sg-abcde"].
            volume_kms_key (str, optional): KMS key for EBS volume on job instances. You
                cannot use an AWS Managed Key such as ``alias/aws/ebs`` because its key
                policy cannot be edited, so cross-account permissions cannot be granted
                for these key policies. Please ensure that the customer-managed key
                allows cross-account use in its policy
                (https://docs.aws.amazon.com/sagemaker/latest/dg/sms-security-kms-permissions.html).
                Accepted formats are (1) KMS key ID, and (2) ARN of a KMS key (see
                https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ResourceConfig.html#sagemaker-Type-ResourceConfig-VolumeKmsKeyId).
                Also note that when using instances with local NVMe (e.g., instance type
                with ``d``, you must set this to `False` otherwise the ``Create*Job``
                API will fail (refer to the before-mentioned documentation URL).
                Defaults to "abcde".
            encrypt_inter_container_traffic (bool): Whether to traffic between job
                containers is encrypted. Applicable for training and processing. For
                implementer of this class: model monitor requires inter-container
                traffic encryption disabled (see
                `sagemaker.model_monitor.model_monitoring.ModelMonitor._validate_network_config()`).
                Hence, implementers must ignore this flag when setting the
                `NetworkConfig` for model monitor. Defaults to True.
            tag_team (str, optional): Team name as mandated by your IT or billing
                department. Defaults to "team_A".
            tag_project (str, optional): Project name as mandated by your IT or billing
                department. Defaults to "project_X".
        """
        self.role = role
        self.subnets = subnets
        self.network_isolation = network_isolation
        self.s3_kms_key = s3_kms_key
        self.sgs = sgs
        self.volume_kms_key = volume_kms_key
        self.encrypt_inter_container_traffic = encrypt_inter_container_traffic
        self.raw_tags = {"team": tag_team, "project": tag_project}

    @property
    def tags(self) -> Tags:
        """Return tags in boto3 format."""
        if not hasattr(self, "_tags"):
            self._tags = [
                {"Key": tag, "Value": value} for tag, value in self.raw_tags.items()
            ]
        return self._tags

    @property
    def vpc_config(self) -> VpcConfig:
        """Return the VPC config for some APIs such as `create_model()`."""
        if not hasattr(self, "_vpc_config"):
            self._vpc_config = {
                "Subnets": self.subnets,
                "SecurityGroupIds": self.sgs,
            }
        return self._vpc_config

    @property
    def train(self) -> Kwargs:
        """Return the mandatory kwargs for `Estimator`."""
        if not hasattr(self, "_train"):
            self._train = dict(
                enable_network_isolation=self.network_isolation,
                output_kms_key=self.s3_kms_key,
                role=self.role,
                security_group_ids=self.sgs,
                subnets=self.subnets,
                tags=self.tags,
                volume_kms_key=self.volume_kms_key,
                encrypt_inter_container_traffic=self.encrypt_inter_container_traffic,
            )
        return self._train

    @property
    def model(self) -> Kwargs:
        """Return the mandatory kwargs for `create_model()`."""
        if not hasattr(self, "_model"):
            self._model = dict(
                enable_network_isolation=self.network_isolation,
                model_kms_key=self.s3_kms_key,
                role=self.role,
                vpc_config=self.vpc_config,
            )
        return self._model

    @property
    def bt(self) -> Kwargs:
        """Return the mandatory kwargs for `model.transformer()`."""
        if not hasattr(self, "_bt"):
            self._bt = dict(
                output_kms_key=self.s3_kms_key,
                tags=self.tags,
                volume_kms_key=self.volume_kms_key,
            )
        return self._bt

    @property
    def processing(self) -> Kwargs:
        """Return the mandatory kwargs for `Processing`."""
        if not hasattr(self, "_processing"):
            self._processing = dict(
                role=self.role,
                tags=self.tags,
                volume_kms_key=self.volume_kms_key,
                output_kms_key=self.s3_kms_key,
                network_config=NetworkConfig(
                    enable_network_isolation=self.network_isolation,
                    security_group_ids=self.sgs,
                    subnets=self.subnets,
                    encrypt_inter_container_traffic=(
                        self.encrypt_inter_container_traffic
                    ),
                ),
            )
        return self._processing


class SmNoKwargs:
    """Default kwargs to whatever in the SageMaker SDK."""

    def __init__(self, role):
        self.d = dict(role=role)

    @property
    def tags(self) -> None:
        return None

    @property
    def train(self) -> Kwargs:
        return self.d

    @property
    def model(self) -> Kwargs:
        return self.d

    @property
    def bt(self) -> Kwargs:
        return {}

    @property
    def processing(self) -> Kwargs:
        return self.d


def endslash(s: str) -> str:
    if s[-1] != "/":
        s += "/"
    return s


# Change me!
# - SmNoKwargs: when using SageMaker default config.
# - SmPrivateKwargs: when using specific settings (e.g., your private VPC).
#   You need to review and make necessary changes to this class.
SmKwargs = SmPrivateKwargs
# SmKwargs = SmNoKwargs

# Force every new project to review the above mandatory configurations.
raise NotImplementedError("Please review this module, then disable this exception")
