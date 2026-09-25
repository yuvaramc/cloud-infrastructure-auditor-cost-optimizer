from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.audit.models import AuditFinding, FindingSeverity
from app.aws.session import AWSAuthenticationError


class EIPScannerError(Exception):
    """Raised when the Elastic IP scanner cannot retrieve AWS address data."""


def scan_eips(session) -> list[AuditFinding]:
    """
    Scan Elastic IP addresses and return findings for unused addresses.

    Args:
        session: An authenticated boto3.Session.

    Returns:
        A list of AuditFinding objects for unassociated Elastic IPs.

    Raises:
        EIPScannerError: If AWS address retrieval fails.
    """
    try:
        ec2_client = session.client("ec2")
        region = session.region_name or "unknown"

        findings: list[AuditFinding] = []

        paginator = ec2_client.get_paginator("describe_addresses")

        for page in paginator.paginate():
            for address in page.get("Addresses", []):
                if address.get("AssociationId"):
                    continue

                allocation_id = address.get("AllocationId", "unknown")
                public_ip = address.get("PublicIp", "unknown")

                metadata: dict[str, Any] = {
                    "allocation_id": allocation_id,
                    "public_ip": public_ip,
                    "association_status": "unassociated",
                }

                findings.append(
                    AuditFinding(
                        resource_type="Elastic IP",
                        resource_id=allocation_id,
                        region=region,
                        severity=FindingSeverity.MEDIUM,
                        description=(
                            f"Elastic IP {public_ip} is allocated but is not "
                            "associated with an active AWS resource and may "
                            "be unused."
                        ),
                        metadata=metadata,
                    )
                )

        return findings

    except (
        AWSAuthenticationError,
        BotoCoreError,
        ClientError,
    ) as exc:
        raise EIPScannerError(
            f"Unable to scan Elastic IP addresses: {exc}"
        ) from exc