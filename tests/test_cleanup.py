import unittest

from app.audit.aggregation.aggregator import AggregatedAuditResult
from app.audit.models import (
    AuditFinding,
    FindingSeverity,
    FindingStatus,
)
from app.cleanup.eligibility import (
    get_cleanup_actions,
    is_cleanup_eligible,
)
from app.cleanup.formatter import format_cleanup_preview
from app.cleanup.models import CleanupAction, CleanupPreview
from app.cleanup.preview import build_cleanup_preview


class TestCleanupEligibility(unittest.TestCase):

    def create_finding(
        self,
        resource_type="EBS Volume",
        resource_id="vol-123",
        state="available",
        status=FindingStatus.OPEN,
        estimated_savings=25.50,
    ):
        return AuditFinding(
            resource_type=resource_type,
            resource_id=resource_id,
            region="ap-south-1",
            severity=FindingSeverity.MEDIUM,
            description="Unattached cloud resource.",
            account_id="123456789012",
            status=status,
            estimated_savings=estimated_savings,
            metadata={"state": state},
        )

    def test_available_open_ebs_volume_is_eligible(self):
        finding = self.create_finding()

        self.assertTrue(is_cleanup_eligible(finding))

    def test_resolved_finding_is_not_eligible(self):
        finding = self.create_finding(
            status=FindingStatus.RESOLVED
        )

        self.assertFalse(is_cleanup_eligible(finding))

    def test_ignored_finding_is_not_eligible(self):
        finding = self.create_finding(
            status=FindingStatus.IGNORED
        )

        self.assertFalse(is_cleanup_eligible(finding))

    def test_in_use_ebs_volume_is_not_eligible(self):
        finding = self.create_finding(state="in-use")

        self.assertFalse(is_cleanup_eligible(finding))

    def test_unknown_ebs_state_is_not_eligible(self):
        finding = self.create_finding(state=None)

        self.assertFalse(is_cleanup_eligible(finding))

    def test_unsupported_resource_type_is_not_eligible(self):
        finding = self.create_finding(
            resource_type="EC2 Instance"
        )

        self.assertFalse(is_cleanup_eligible(finding))

    def test_only_eligible_findings_create_actions(self):
        eligible = self.create_finding(
            resource_id="vol-eligible"
        )
        attached = self.create_finding(
            resource_id="vol-attached",
            state="in-use",
        )
        resolved = self.create_finding(
            resource_id="vol-resolved",
            status=FindingStatus.RESOLVED,
        )

        actions = get_cleanup_actions(
            [eligible, attached, resolved]
        )

        self.assertEqual(len(actions), 1)
        self.assertEqual(
            actions[0].resource_id,
            "vol-eligible",
        )

    def test_cleanup_action_preserves_finding_details(self):
        finding = self.create_finding()

        actions = get_cleanup_actions([finding])

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].resource_type, "EBS Volume")
        self.assertEqual(actions[0].resource_id, "vol-123")
        self.assertEqual(actions[0].region, "ap-south-1")
        self.assertEqual(actions[0].account_id, "123456789012")
        self.assertEqual(actions[0].estimated_savings, 25.50)
        self.assertEqual(
            actions[0].action,
            "Delete unattached EBS volume",
        )

    def test_missing_estimated_savings_is_supported(self):
        finding = self.create_finding(
            estimated_savings=None
        )

        actions = get_cleanup_actions([finding])

        self.assertIsNone(actions[0].estimated_savings)


class TestCleanupPreview(unittest.TestCase):

    def create_finding(self, resource_id="vol-123"):
        return AuditFinding(
            resource_type="EBS Volume",
            resource_id=resource_id,
            region="ap-south-1",
            severity=FindingSeverity.MEDIUM,
            description="Unattached EBS volume.",
            metadata={"state": "available"},
        )

    def test_build_preview_from_findings(self):
        findings = [
            self.create_finding("vol-1"),
            self.create_finding("vol-2"),
        ]

        preview = build_cleanup_preview(findings)

        self.assertEqual(preview.total_actions, 2)
        self.assertTrue(preview.has_actions)

    def test_build_preview_from_aggregated_results(self):
        findings = [
            self.create_finding("vol-1"),
        ]
        aggregated = AggregatedAuditResult(findings)

        preview = build_cleanup_preview(aggregated)

        self.assertEqual(preview.total_actions, 1)
        self.assertEqual(
            preview.actions[0].resource_id,
            "vol-1",
        )

    def test_empty_findings_create_empty_preview(self):
        preview = build_cleanup_preview([])

        self.assertEqual(preview.total_actions, 0)
        self.assertFalse(preview.has_actions)
        self.assertEqual(preview.actions, ())

    def test_generator_findings_are_supported(self):
        findings = (
            self.create_finding(f"vol-{index}")
            for index in range(3)
        )

        preview = build_cleanup_preview(findings)

        self.assertEqual(preview.total_actions, 3)


class TestCleanupFormatter(unittest.TestCase):

    def test_empty_preview_message(self):
        preview = CleanupPreview(actions=())

        output = format_cleanup_preview(preview)

        self.assertIn("CLEANUP DRY-RUN PREVIEW", output)
        self.assertIn("Eligible resources: 0", output)
        self.assertIn(
            "No eligible resources found for cleanup.",
            output,
        )
        self.assertIn(
            "Your cloud infrastructure was not modified.",
            output,
        )

    def test_preview_displays_proposed_action(self):
        action = CleanupAction(
            resource_type="EBS Volume",
            resource_id="vol-123",
            region="ap-south-1",
            action="Delete unattached EBS volume",
            description="Unattached and available.",
            estimated_savings=25.50,
        )
        preview = CleanupPreview(actions=(action,))

        output = format_cleanup_preview(preview)

        self.assertIn("Mode: DRY RUN", output)
        self.assertIn("vol-123", output)
        self.assertIn("ap-south-1", output)
        self.assertIn(
            "Delete unattached EBS volume",
            output,
        )
        self.assertIn("25.50", output)
        self.assertIn("PREVIEW ONLY", output)


if __name__ == "__main__":
    unittest.main()
