import unittest

from app.audit.models import (
    AuditFinding,
    FindingSeverity,
    FindingStatus,
)


class TestAuditFinding(unittest.TestCase):

    def test_create_audit_finding(self):
        finding = AuditFinding(
            resource_type="EBS Volume",
            resource_id="vol-123456",
            region="ap-south-1",
            account_id="123456789012",
            severity=FindingSeverity.HIGH,
            status=FindingStatus.OPEN,
            description="EBS volume is unattached.",
            estimated_cost=10.50,
            estimated_savings=10.50,
            metadata={"volume_size_gb": 100},
        )

        self.assertEqual(finding.resource_type, "EBS Volume")
        self.assertEqual(finding.resource_id, "vol-123456")
        self.assertEqual(finding.region, "ap-south-1")
        self.assertEqual(finding.account_id, "123456789012")
        self.assertEqual(finding.severity, FindingSeverity.HIGH)
        self.assertEqual(finding.status, FindingStatus.OPEN)
        self.assertEqual(finding.estimated_cost, 10.50)
        self.assertEqual(finding.estimated_savings, 10.50)
        self.assertEqual(finding.metadata["volume_size_gb"], 100)

    def test_default_values(self):
        finding = AuditFinding(
            resource_type="EC2 Instance",
            resource_id="i-123456",
            region="us-east-1",
            severity=FindingSeverity.MEDIUM,
            description="Instance may be underutilized.",
        )

        self.assertEqual(finding.status, FindingStatus.OPEN)
        self.assertIsNone(finding.account_id)
        self.assertIsNone(finding.estimated_cost)
        self.assertIsNone(finding.estimated_savings)
        self.assertEqual(finding.metadata, {})

    def test_to_dict_serializes_enums(self):
        finding = AuditFinding(
            resource_type="S3 Bucket",
            resource_id="my-bucket",
            region="ap-south-1",
            severity=FindingSeverity.LOW,
            description="Bucket may have unnecessary storage.",
            metadata={"storage_class": "STANDARD"},
        )

        data = finding.to_dict()

        self.assertEqual(data["resource_type"], "S3 Bucket")
        self.assertEqual(data["resource_id"], "my-bucket")
        self.assertEqual(data["severity"], "LOW")
        self.assertEqual(data["status"], "OPEN")
        self.assertEqual(data["metadata"]["storage_class"], "STANDARD")

    def test_empty_required_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            AuditFinding(
                resource_type="",
                resource_id="vol-123",
                region="ap-south-1",
                severity=FindingSeverity.HIGH,
                description="Test finding",
            )

        with self.assertRaises(ValueError):
            AuditFinding(
                resource_type="EBS Volume",
                resource_id="",
                region="ap-south-1",
                severity=FindingSeverity.HIGH,
                description="Test finding",
            )

        with self.assertRaises(ValueError):
            AuditFinding(
                resource_type="EBS Volume",
                resource_id="vol-123",
                region="ap-south-1",
                severity=FindingSeverity.HIGH,
                description="",
            )

    def test_negative_cost_is_rejected(self):
        with self.assertRaises(ValueError):
            AuditFinding(
                resource_type="EBS Volume",
                resource_id="vol-123",
                region="ap-south-1",
                severity=FindingSeverity.HIGH,
                description="Test finding",
                estimated_cost=-10,
            )

    def test_negative_savings_is_rejected(self):
        with self.assertRaises(ValueError):
            AuditFinding(
                resource_type="EBS Volume",
                resource_id="vol-123",
                region="ap-south-1",
                severity=FindingSeverity.HIGH,
                description="Test finding",
                estimated_savings=-5,
            )

    def test_metadata_is_not_shared_between_findings(self):
        first = AuditFinding(
            resource_type="EBS Volume",
            resource_id="vol-1",
            region="ap-south-1",
            severity=FindingSeverity.LOW,
            description="First finding",
        )

        second = AuditFinding(
            resource_type="EBS Volume",
            resource_id="vol-2",
            region="ap-south-1",
            severity=FindingSeverity.LOW,
            description="Second finding",
        )

        first.metadata["size"] = 100

        self.assertNotIn("size", second.metadata)


if __name__ == "__main__":
    unittest.main()