from unittest.mock import patch

from typer.testing import CliRunner

from app.aws.session import AWSAuthenticationError
from app.cli.main import app


runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(
        app,
        ["version"],
    )

    assert result.exit_code == 0
    assert "cloud-auditor version 0.1.0" in result.output


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_default_options(mock_get_aws_session) -> None:
    result = runner.invoke(
        app,
        ["audit"],
    )

    assert result.exit_code == 0
    assert "provider=aws" in result.output
    assert "region=us-east-1" in result.output
    assert "resource=all" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )


def test_audit_custom_options() -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "gcp",
            "--region",
            "us-central1",
            "--resource",
            "compute",
        ],
    )

    assert result.exit_code == 0
    assert "provider=gcp" in result.output
    assert "region=us-central1" in result.output
    assert "resource=compute" in result.output


def test_audit_invalid_provider() -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "azure",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported provider" in result.output


def test_audit_invalid_resource() -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--resource",
            "database",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported resource" in result.output


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_default_aws_region(mock_get_aws_session) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
        ],
    )

    assert result.exit_code == 0
    assert "region=us-east-1" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_custom_aws_region(mock_get_aws_session) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--region",
            "ap-south-1",
        ],
    )

    assert result.exit_code == 0
    assert "region=ap-south-1" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="ap-south-1"
    )


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_invalid_aws_region(mock_get_aws_session) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--region",
            "invalid-region",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported AWS region" in result.output

    mock_get_aws_session.assert_not_called()


def test_audit_gcp_region() -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "gcp",
            "--region",
            "us-central1",
            "--resource",
            "compute",
        ],
    )

    assert result.exit_code == 0
    assert "provider=gcp" in result.output
    assert "region=us-central1" in result.output


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_aws_authentication_error(mock_get_aws_session) -> None:
    mock_get_aws_session.side_effect = AWSAuthenticationError(
        "AWS credentials were not found."
    )

    result = runner.invoke(
        app,
        ["audit"],
    )

    assert result.exit_code != 0
    assert "AWS credentials were not found." in result.output