
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from app.scanners.eip_scanner import (
    EIPScannerError,
    scan_elastic_ips,
)


def make_session(addresses):
    """Create a mocked AWS session for scanner tests."""
    session = MagicMock()
    session.region_name = "ap-south-1"

    ec2 = MagicMock()
    sts = MagicMock()

    session.client.side_effect = lambda service: {
        "ec2": ec2,
        "sts": sts,
    }[service]

    sts.get_caller_identity.return_value = {
        "Account": "123456789012"
    }

    paginator = MagicMock()
    paginator.paginate.return_value = [
        {"Addresses": addresses}
    ]
    ec2.get_paginator.return_value = paginator

    return session, ec2


def test_detects_unassociated_elastic_ip():
    """An unassociated Elastic IP should produce a finding."""
    session, _ = make_session([
        {
            "PublicIp": "203.0.113.10",
            "AllocationId": "eipalloc-unused",
            "Domain": "vpc",
            "Tags": [{"Key": "Environment", "Value": "test"}],
        }
    ])

    findings = scan_elastic_ips(session)

    assert len(findings) == 1
    assert findings[0].resource_type == "Elastic IP"
    assert findings[0].resource_id == "eipalloc-unused"
    assert findings[0].region == "ap-south-1"
    assert findings[0].account_id == "123456789012"
    assert findings[0].metadata["public_ip"] == "203.0.113.10"
    assert findings[0].severity.value == "MEDIUM"


def test_ignores_associated_elastic_ip():
    """An associated Elastic IP should not produce a finding."""
    session, _ = make_session([
        {
            "PublicIp": "203.0.113.11",
            "AllocationId": "eipalloc-used",
            "AssociationId": "eipassoc-example",
            "NetworkInterfaceId": "eni-example",
            "InstanceId": "i-example",
        }
    ])

    findings = scan_elastic_ips(session)

    assert findings == []


def test_handles_multiple_pages():
    """The scanner should process every paginator page."""
    session, ec2 = make_session([])

    paginator = ec2.get_paginator.return_value
    paginator.paginate.return_value = [
        {
            "Addresses": [
                {
                    "PublicIp": "203.0.113.10",
                    "AllocationId": "eipalloc-one",
                }
            ]
        },
        {
            "Addresses": [
                {
                    "PublicIp": "203.0.113.11",
                    "AllocationId": "eipalloc-two",
                }
            ]
        },
    ]

    findings = scan_elastic_ips(session)

    assert len(findings) == 2
    assert {finding.resource_id for finding in findings} == {
        "eipalloc-one",
        "eipalloc-two",
    }


def test_wraps_aws_api_errors():
    """AWS API errors should be wrapped in EIPScannerError."""
    session, ec2 = make_session([])

    ec2.get_paginator.side_effect = ClientError(
        {
            "Error": {
                "Code": "UnauthorizedOperation",
                "Message": "Not authorized",
            }
        },
        "DescribeAddresses",
    )

    with pytest.raises(EIPScannerError):
        scan_elastic_ips(session)


def test_handles_address_without_allocation_id():
    """An unassociated address can use its public IP as the resource ID."""
    session, _ = make_session([
        {
            "PublicIp": "203.0.113.12",
            "Domain": "standard",
        }
    ])

    findings = scan_elastic_ips(session)

    assert len(findings) == 1
    assert findings[0].resource_id == "203.0.113.12"


def test_returns_empty_list_when_no_addresses_exist():
    """No addresses should produce no findings."""
    session, _ = make_session([])

    findings = scan_elastic_ips(session)

    assert findings == []
