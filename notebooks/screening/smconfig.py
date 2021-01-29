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
        tag_team: str = "team_A",
        tag_project: str = "project_X",
    ) -> None:
        """Return mandatory kwargs to run SageMaker jobs on this particular AWS account.

        Args:
            role (str): SageMaker role.
            subnets (List[str], optional): List of subnets. Defaults to
                ["subnet-abcde"].
            network_isolation (bool, optional): Network isolation. Defaults to False.
            s3_kms_key (str, optional): KMS key for S3. Defaults to "abcde".
            sgs (List[str], optional): List of security groups. Defaults to
                ["sg-abcde"].
            volume_kms_key (str, optional): KMS key for EBS volume on job instances.
                Defaults to "abcde".
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
