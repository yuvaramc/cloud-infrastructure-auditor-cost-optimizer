from typer.testing import CliRunner

from app.cli.main import app


runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(
        app,
        ["version"],
    )

    assert result.exit_code == 0
    assert "cloud-auditor version 0.1.0" in result.output


def test_audit_default_options() -> None:
    result = runner.invoke(
        app,
        ["audit"],
    )

    assert result.exit_code == 0
    assert "provider=aws" in result.output
    assert "region=us-east-1" in result.output
    assert "resource=all" in result.output


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


def test_audit_default_aws_region() -> None:
    result = runner.invoke(
        app,
        [
            "audit",
        ],
    )

    assert result.exit_code == 0
    assert "region=us-east-1" in result.output


def test_audit_custom_aws_region() -> None:
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


def test_audit_invalid_aws_region() -> None:
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