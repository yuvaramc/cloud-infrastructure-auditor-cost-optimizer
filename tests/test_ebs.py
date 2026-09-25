import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from botocore.exceptions import ClientError

from app.audit.models import FindingSeverity
from app.scanners.ebs import EBSScannerError, scan_ebs_volumes


class TestEBSScanner(unittest.TestCase):

    def create_session(self, pages, account_id="123456789012"):
        session = Mock()
        session.region_name = "ap-south-1"

        ec2_client = Mock()
        paginator = Mock()
        paginator.paginate.return_value = pages
        ec2_client.get_paginator.return_value = paginator

        sts_client = Mock()
        sts_client.get_caller_identity.return_value = {
            "Account": account_id
        }

        def client(service_name):
            if service_name == "ec2":
                return ec2_client
            if service_name == "sts":
                return sts_client
            raise ValueError(f"Unexpected service: {service_name}")

        session.client.side_effect = client

        return session

    def test_unattached_volume_creates_finding(self):
        pages = [
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-123",
                        "Size": 50,
                        "State": "available",
                        "VolumeType": "gp3",
                        "CreateTime": datetime(
                            2026, 9, 1, tzinfo=timezone.utc
                        ),
                        "Attachments": [],
                    }
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_ebs_volumes(session)

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(finding.resource_type, "EBS Volume")
        self.assertEqual(finding.resource_id, "vol-123")
        self.assertEqual(finding.region, "ap-south-1")
        self.assertEqual(finding.account_id, "123456789012")
        self.assertEqual(finding.severity, FindingSeverity.MEDIUM)

        self.assertEqual(finding.metadata["size_gb"], 50)
        self.assertEqual(finding.metadata["state"], "available")
        self.assertEqual(finding.metadata["volume_type"], "gp3")

    def test_attached_volume_is_ignored(self):
        pages = [
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-attached",
                        "Size": 100,
                        "State": "in-use",
                        "VolumeType": "gp3",
                        "Attachments": [
                            {
                                "InstanceId": "i-1234567890"
                            }
                        ],
                    }
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_ebs_volumes(session)

        self.assertEqual(findings, [])

    def test_mixed_attached_and_unattached_volumes(self):
        pages = [
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-attached",
                        "Size": 100,
                        "State": "in-use",
                        "VolumeType": "gp3",
                        "Attachments": [
                            {
                                "InstanceId": "i-1234567890"
                            }
                        ],
                    },
                    {
                        "VolumeId": "vol-unattached",
                        "Size": 20,
                        "State": "available",
                        "VolumeType": "gp3",
                        "Attachments": [],
                    },
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_ebs_volumes(session)

        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0].resource_id,
            "vol-unattached",
        )

    def test_multiple_pages_are_scanned(self):
        pages = [
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-1",
                        "Size": 10,
                        "State": "available",
                        "VolumeType": "gp3",
                        "Attachments": [],
                    }
                ]
            },
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-2",
                        "Size": 20,
                        "State": "available",
                        "VolumeType": "gp3",
                        "Attachments": [],
                    }
                ]
            },
        ]

        session = self.create_session(pages)

        findings = scan_ebs_volumes(session)

        self.assertEqual(len(findings), 2)

        resource_ids = {
            finding.resource_id
            for finding in findings
        }

        self.assertEqual(
            resource_ids,
            {"vol-1", "vol-2"},
        )

    def test_api_error_is_handled(self):
        session = Mock()
        session.region_name = "ap-south-1"

        ec2_client = Mock()
        error_response = {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied",
            }
        }

        ec2_client.get_paginator.side_effect = ClientError(
            error_response,
            "DescribeVolumes",
        )

        session.client.return_value = ec2_client

        with self.assertRaises(EBSScannerError) as context:
            scan_ebs_volumes(session)

        self.assertIn(
            "Unable to scan EBS volumes",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()