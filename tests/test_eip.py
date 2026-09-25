import unittest
from unittest.mock import Mock

from botocore.exceptions import ClientError

from app.audit.models import FindingSeverity
from app.scanners.eip import EIPScannerError, scan_eips


class TestEIPScanner(unittest.TestCase):

    def create_session(self, pages):
        session = Mock()
        session.region_name = "ap-south-1"

        ec2_client = Mock()
        paginator = Mock()
        paginator.paginate.return_value = pages
        ec2_client.get_paginator.return_value = paginator

        session.client.return_value = ec2_client

        return session

    def test_unassociated_eip_creates_finding(self):
        pages = [
            {
                "Addresses": [
                    {
                        "AllocationId": "eipalloc-123",
                        "PublicIp": "13.233.10.20",
                    }
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_eips(session)

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(finding.resource_type, "Elastic IP")
        self.assertEqual(
            finding.resource_id,
            "eipalloc-123",
        )
        self.assertEqual(
            finding.region,
            "ap-south-1",
        )
        self.assertEqual(
            finding.severity,
            FindingSeverity.MEDIUM,
        )

        self.assertEqual(
            finding.metadata["allocation_id"],
            "eipalloc-123",
        )
        self.assertEqual(
            finding.metadata["public_ip"],
            "13.233.10.20",
        )
        self.assertEqual(
            finding.metadata["association_status"],
            "unassociated",
        )

    def test_associated_eip_is_ignored(self):
        pages = [
            {
                "Addresses": [
                    {
                        "AllocationId": "eipalloc-associated",
                        "PublicIp": "13.233.10.21",
                        "AssociationId": "eipassoc-123",
                        "InstanceId": "i-1234567890",
                    }
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_eips(session)

        self.assertEqual(findings, [])

    def test_mixed_associated_and_unassociated_eips(self):
        pages = [
            {
                "Addresses": [
                    {
                        "AllocationId": "eipalloc-associated",
                        "PublicIp": "13.233.10.21",
                        "AssociationId": "eipassoc-123",
                        "InstanceId": "i-1234567890",
                    },
                    {
                        "AllocationId": "eipalloc-unused",
                        "PublicIp": "13.233.10.22",
                    },
                ]
            }
        ]

        session = self.create_session(pages)

        findings = scan_eips(session)

        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0].resource_id,
            "eipalloc-unused",
        )

    def test_multiple_pages_are_scanned(self):
        pages = [
            {
                "Addresses": [
                    {
                        "AllocationId": "eipalloc-1",
                        "PublicIp": "13.233.10.23",
                    }
                ]
            },
            {
                "Addresses": [
                    {
                        "AllocationId": "eipalloc-2",
                        "PublicIp": "13.233.10.24",
                    }
                ]
            },
        ]

        session = self.create_session(pages)

        findings = scan_eips(session)

        self.assertEqual(len(findings), 2)

        resource_ids = {
            finding.resource_id
            for finding in findings
        }

        self.assertEqual(
            resource_ids,
            {
                "eipalloc-1",
                "eipalloc-2",
            },
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
            "DescribeAddresses",
        )

        session.client.return_value = ec2_client

        with self.assertRaises(EIPScannerError) as context:
            scan_eips(session)

        self.assertIn(
            "Unable to scan Elastic IP addresses",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()