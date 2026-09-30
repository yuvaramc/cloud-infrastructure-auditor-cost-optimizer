from unittest.mock import MagicMock, patch

import pytest

from app.aws.session import (
    AWSAuthenticationError,
    create_aws_session,
)


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_uses_default_region(mock_session):
    create_aws_session()

    mock_session.assert_called_once_with(
        region_name="us-east-1",
    )


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_uses_custom_region(mock_session):
    create_aws_session(region="ap-south-1")

    mock_session.assert_called_once_with(
        region_name="ap-south-1",
    )


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_uses_profile_and_region(mock_session):
    create_aws_session(
        profile_name="development",
        region="eu-west-1",
    )

    mock_session.assert_called_once_with(
        profile_name="development",
        region_name="eu-west-1",
    )


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_normalizes_region(mock_session):
    create_aws_session(region=" AP-SOUTH-1 ")

    mock_session.assert_called_once_with(
        region_name="ap-south-1",
    )


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_rejects_invalid_region(mock_session):
    with pytest.raises(AWSAuthenticationError, match="Unsupported AWS region"):
        create_aws_session(region="invalid-region")

    mock_session.assert_not_called()


@patch("app.aws.session.boto3.Session")
def test_create_aws_session_passes_region_to_boto3(mock_session):
    mock_session.return_value = MagicMock()

    session = create_aws_session(region="us-west-2")

    assert session == mock_session.return_value
    mock_session.assert_called_once_with(
        region_name="us-west-2",
    )