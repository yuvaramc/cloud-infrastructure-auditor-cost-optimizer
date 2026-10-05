from unittest.mock import patch

from typer.testing import CliRunner

from app.audit.models import AuditFinding, FindingSeverity
from app.aws.session import AWSAuthenticationError
from app.cli.main import app
from app.scanners.ebs import EBSScannerError


runner = CliRunner()


def make_finding():
    return AuditFinding(
        resource_type="EBS Volume",
        resource_id="vol-123456",
        region="ap-south-1",
        severity=FindingSeverity.MEDIUM,
        description="Unattached EBS volume",
        metadata={"state": "available"},
    )


class TestCleanupCLI:
    @patch("app.cli.commands.cleanup.scan_ebs_volumes")
    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_dry_run_displays_cleanup_preview(
        self, mock_session, mock_scan
    ):
        mock_scan.return_value = [make_finding()]

        result = runner.invoke(
            app,
            ["cleanup", "--dry-run", "--region", "ap-south-1"],
        )

        assert result.exit_code == 0
        assert "CLEANUP DRY-RUN PREVIEW" in result.output
        assert "vol-123456" in result.output
        assert "Delete unattached EBS volume" in result.output
        assert "No AWS resources were deleted or modified" in result.output

        mock_session.assert_called_once_with(region="ap-south-1")
        mock_scan.assert_called_once_with(mock_session.return_value)

    @patch("app.cli.commands.cleanup.scan_ebs_volumes", return_value=[])
    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_empty_scan_displays_no_candidates(
        self, mock_session, mock_scan
    ):
        result = runner.invoke(app, ["cleanup", "--dry-run"])

        assert result.exit_code == 0
        assert "No eligible resources found for cleanup." in result.output
        assert "Your cloud infrastructure was not modified." in result.output

    @patch("app.cli.commands.cleanup.scan_ebs_volumes")
    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_execute_is_rejected_without_aws_access(
        self, mock_session, mock_scan
    ):
        result = runner.invoke(app, ["cleanup", "--execute"])

        assert result.exit_code == 2
        assert "Cleanup execution is not implemented" in result.output
        mock_session.assert_not_called()
        mock_scan.assert_not_called()

    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_unsupported_provider_is_rejected(self, mock_session):
        result = runner.invoke(
            app, ["cleanup", "--provider", "gcp"]
        )

        assert result.exit_code != 0
        assert "Unsupported provider" in result.output
        mock_session.assert_not_called()

    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_unsupported_resource_is_rejected(self, mock_session):
        result = runner.invoke(
            app, ["cleanup", "--resource", "compute"]
        )

        assert result.exit_code != 0
        assert "Unsupported resource" in result.output
        mock_session.assert_not_called()

    @patch("app.cli.commands.cleanup.scan_ebs_volumes")
    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_invalid_region_is_rejected(
        self, mock_session, mock_scan
    ):
        result = runner.invoke(
            app, ["cleanup", "--region", "invalid-region"]
        )

        assert result.exit_code != 0
        mock_session.assert_not_called()
        mock_scan.assert_not_called()

    @patch(
        "app.cli.commands.cleanup.get_aws_session",
        side_effect=AWSAuthenticationError("AWS authentication failed"),
    )
    def test_authentication_error_is_handled(self, mock_session):
        result = runner.invoke(app, ["cleanup", "--dry-run"])

        assert result.exit_code == 1
        assert "AWS authentication failed" in result.output

    @patch("app.cli.commands.cleanup.scan_ebs_volumes")
    @patch("app.cli.commands.cleanup.get_aws_session")
    def test_scanner_error_is_handled(
        self, mock_session, mock_scan
    ):
        mock_scan.side_effect = EBSScannerError("EBS scan failed")

        result = runner.invoke(app, ["cleanup", "--dry-run"])

        assert result.exit_code == 1
        assert "EBS scan failed" in result.output
