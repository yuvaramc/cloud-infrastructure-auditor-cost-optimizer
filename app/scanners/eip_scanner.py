
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.audit.models import AuditFinding, FindingSeverity
from app.aws.session import AWSAuthenticationError


class EIPScannerError(Exception):
    """Raised when the Elastic IP scanner cannot retrieve address data."""


def scan_elastic_ips(session) -> list[AuditFinding]:
    """Find Elastic IP addresses that are not associated with resources."""
    try:
        ec2_client = session.client("ec2")
        region = session.region_name or "unknown"
        account_id = _get_account_id(session)
        findings: list[AuditFinding] = []

        paginator = ec2_client.get_paginator("describe_addresses")

        for page in paginator.paginate():
            for address in page.get("Addresses", []):
                if address.get("AssociationId"):
                    continue

                public_ip = address.get("PublicIp")
                allocation_id = address.get("AllocationId")
                resource_id = allocation_id or public_ip

                if not resource_id:
                    continue

                metadata: dict[str, Any] = {
                    "public_ip": public_ip,
                    "allocation_id": allocation_id,
                    "domain": address.get("Domain"),
                    "network_interface_id": address.get("NetworkInterfaceId"),
                    "instance_id": address.get("InstanceId"),
                    "tags": address.get("Tags", []),
                }

                findings.append(
                    AuditFinding(
                        resource_type="Elastic IP",
                        resource_id=resource_id,
                        region=region,
                        severity=FindingSeverity.MEDIUM,
                        description=(
                            f"Elastic IP {public_ip or resource_id} is "
                            "unassociated and may be unused. Verify before "
                            "releasing it."
                        ),
                        account_id=account_id,
                        metadata=metadata,
                    )
                )

        return findings

    except (AWSAuthenticationError, BotoCoreError, ClientError) as exc:
        raise EIPScannerError(
            f"Unable to scan Elastic IP addresses: {exc}"
        ) from exc


def _get_account_id(session) -> str | None:
    """Retrieve the AWS account ID associated with the session."""
    try:
        sts_client = session.client("sts")
        return sts_client.get_caller_identity().get("Account")
    except (BotoCoreError, ClientError):
        return None
