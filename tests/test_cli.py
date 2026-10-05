from unittest.mock import patch

from typer.testing import CliRunner

from app.audit.models import AuditFinding, FindingSeverity
from app.aws.session import AWSAuthenticationError
from app.cli.main import app
from app.scanners.ebs import EBSScannerError

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


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_region_with_whitespace_and_uppercase(
    mock_get_aws_session,
) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--region",
            " AP-SOUTH-1 ",
        ],
    )

    assert result.exit_code == 0
    assert "region=ap-south-1" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="ap-south-1"
    )


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_unsupported_region_does_not_create_session(
    mock_get_aws_session,
) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--region",
            "moon-west-1",
        ],
    )

    assert result.exit_code != 0
    assert "Unsupported AWS region" in result.output

    mock_get_aws_session.assert_not_called()


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_uses_default_region_when_region_option_is_omitted(
    mock_get_aws_session,
) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "aws",
        ],
    )

    assert result.exit_code == 0
    assert "provider=aws" in result.output
    assert "region=us-east-1" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )


@patch("app.cli.commands.audit.get_aws_session")
def test_audit_default_region_is_used_for_all_resources(
    mock_get_aws_session,
) -> None:
    result = runner.invoke(
        app,
        [
            "audit",
            "--resource",
            "all",
        ],
    )

    assert result.exit_code == 0
    assert "region=us-east-1" in result.output
    assert "resource=all" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )


@patch("app.cli.commands.audit.scan_ebs_volumes")
@patch("app.cli.commands.audit.get_aws_session")
def test_audit_all_scans_ebs_resources(
    mock_get_aws_session,
    mock_scan_ebs_volumes,
) -> None:
    finding = AuditFinding(
        resource_type="EBS Volume",
        resource_id="vol-123456",
        region="us-east-1",
        severity=FindingSeverity.MEDIUM,
        description=(
            "EBS volume vol-123456 is not attached "
            "to any EC2 instance."
        ),
        estimated_savings=12.50,
    )

    mock_session = object()
    mock_get_aws_session.return_value = mock_session
    mock_scan_ebs_volumes.return_value = [finding]

    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "aws",
            "--region",
            "us-east-1",
            "--resource",
            "all",
        ],
    )

    assert result.exit_code == 0
    assert "EBS Volume" in result.output
    assert "Audit completed: provider=aws" in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )
    mock_scan_ebs_volumes.assert_called_once_with(mock_session)


@patch("app.cli.commands.audit.scan_ebs_volumes")
@patch("app.cli.commands.audit.get_aws_session")
def test_audit_storage_scans_ebs_resources(
    mock_get_aws_session,
    mock_scan_ebs_volumes,
) -> None:
    mock_session = object()
    mock_get_aws_session.return_value = mock_session
    mock_scan_ebs_volumes.return_value = []

    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "aws",
            "--region",
            "ap-south-1",
            "--resource",
            "storage",
        ],
    )

    assert result.exit_code == 0
    assert "No audit findings were found." in result.output

    mock_get_aws_session.assert_called_once_with(
        region="ap-south-1"
    )
    mock_scan_ebs_volumes.assert_called_once_with(mock_session)


@patch("app.cli.commands.audit.scan_ebs_volumes")
@patch("app.cli.commands.audit.get_aws_session")
def test_audit_ebs_scanner_failure(
    mock_get_aws_session,
    mock_scan_ebs_volumes,
) -> None:
    mock_session = object()
    mock_get_aws_session.return_value = mock_session
    mock_scan_ebs_volumes.side_effect = EBSScannerError(
        "Unable to scan EBS volumes."
    )

    result = runner.invoke(
        app,
        [
            "audit",
            "--provider",
            "aws",
            "--region",
            "us-east-1",
            "--resource",
            "storage",
        ],
    )

    assert result.exit_code == 1
    assert "EBS scanner failed: Unable to scan EBS volumes." in result.output

    mock_get_aws_session.assert_called_once_with(
        region="us-east-1"
    )
    mock_scan_ebs_volumes.assert_called_once_with(mock_session)
