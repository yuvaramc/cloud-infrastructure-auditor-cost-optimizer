import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


class AWSAuthenticationError(Exception):
    """Raised when AWS authentication fails."""


def create_aws_session(profile_name: str | None = None):
    """
    Create a Boto3 session using the user's AWS configuration.

    Args:
        profile_name: Optional AWS profile name.

    Returns:
        A configured boto3.Session object.
    """
    try:
        if profile_name:
            return boto3.Session(profile_name=profile_name)

        return boto3.Session()

    except (BotoCoreError, ValueError) as exc:
        raise AWSAuthenticationError(
            f"Unable to create AWS session: {exc}"
        ) from exc


def assume_aws_role(session, role_arn: str):
    """
    Assume an IAM role using AWS STS and return a temporary
    Boto3 session.

    Args:
        session: Source boto3.Session used to call STS.
        role_arn: ARN of the IAM role to assume.

    Returns:
        A boto3.Session configured with temporary credentials.

    Raises:
        AWSAuthenticationError: If role assumption fails.
    """
    if not role_arn or not role_arn.strip():
        raise AWSAuthenticationError(
            "IAM role ARN cannot be empty."
        )

    try:
        sts_client = session.client("sts")

        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="cloud-infrastructure-auditor",
        )

        credentials = response["Credentials"]

        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=session.region_name,
        )

    except ClientError as exc:
        raise AWSAuthenticationError(
            f"Unable to assume IAM role '{role_arn}'. "
            "Please check the role ARN and permissions."
        ) from exc

    except (BotoCoreError, KeyError) as exc:
        raise AWSAuthenticationError(
            "Unable to obtain temporary AWS credentials "
            "from the IAM role."
        ) from exc


def validate_aws_credentials(session) -> bool:
    """
    Validate the AWS session by calling STS GetCallerIdentity.

    Args:
        session: A boto3.Session object.

    Returns:
        True if AWS credentials are valid.

    Raises:
        AWSAuthenticationError: If credentials are missing or invalid.
    """
    try:
        sts_client = session.client("sts")
        sts_client.get_caller_identity()
        return True

    except NoCredentialsError as exc:
        raise AWSAuthenticationError(
            "AWS credentials were not found. "
            "Please configure your AWS credentials or AWS profile."
        ) from exc

    except ClientError as exc:
        raise AWSAuthenticationError(
            "AWS authentication failed. "
            "Please check your AWS credentials and profile."
        ) from exc

    except BotoCoreError as exc:
        raise AWSAuthenticationError(
            f"Unable to validate AWS credentials: {exc}"
        ) from exc


def get_aws_session(
    profile_name: str | None = None,
    role_arn: str | None = None,
):
    """
    Create and validate an AWS session.

    If role_arn is provided, the initial session is used to
    assume the IAM role and a temporary-credential session
    is returned.

    Args:
        profile_name: Optional AWS profile name.
        role_arn: Optional IAM role ARN.

    Returns:
        An authenticated boto3.Session object.
    """
    session = create_aws_session(profile_name)

    if role_arn:
        session = assume_aws_role(session, role_arn)

    validate_aws_credentials(session)

    return session