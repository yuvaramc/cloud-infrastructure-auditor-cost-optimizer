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


def get_aws_session(profile_name: str | None = None):
    """
    Create and validate an AWS session.

    This is the main entry point that future AWS scanners
    can use to obtain an authenticated session.
    """
    session = create_aws_session(profile_name)
    validate_aws_credentials(session)
    return session