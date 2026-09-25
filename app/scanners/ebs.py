from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.audit.models import AuditFinding, FindingSeverity
from app.aws.session import AWSAuthenticationError


class EBSScannerError(Exception):
    """Raised when the EBS scanner cannot retrieve AWS volume data."""


def scan_ebs_volumes(session) -> list[AuditFinding]:
    """
    Scan EBS volumes and return findings for unattached volumes.

    Args:
        session: An authenticated boto3.Session.

    Returns:
        A list of AuditFinding objects for unattached EBS volumes.

    Raises:
        EBSScannerError: If AWS volume retrieval fails.
    """
    try:
        ec2_client = session.client("ec2")
        region = session.region_name or "unknown"

        account_id = _get_account_id(session)

        findings: list[AuditFinding] = []

        paginator = ec2_client.get_paginator("describe_volumes")

        for page in paginator.paginate():
            for volume in page.get("Volumes", []):
                if volume.get("Attachments"):
                    continue

                volume_id = volume["VolumeId"]
                size = volume.get("Size")
                state = volume.get("State")
                volume_type = volume.get("VolumeType")

                metadata: dict[str, Any] = {
                    "size_gb": size,
                    "state": state,
                    "volume_type": volume_type,
                }

                if "CreateTime" in volume:
                    metadata["create_time"] = volume["CreateTime"].isoformat()

                findings.append(
                    AuditFinding(
                        resource_type="EBS Volume",
                        resource_id=volume_id,
                        region=region,
                        severity=FindingSeverity.MEDIUM,
                        description=(
                            f"EBS volume {volume_id} is not attached "
                            "to any EC2 instance and may be unused."
                        ),
                        account_id=account_id,
                        metadata=metadata,
                    )
                )

        return findings

    except (AWSAuthenticationError, BotoCoreError, ClientError) as exc:
        raise EBSScannerError(
            f"Unable to scan EBS volumes: {exc}"
        ) from exc


def _get_account_id(session) -> str | None:
    """Retrieve the AWS account ID associated with the session."""

    try:
        sts_client = session.client("sts")
        identity = sts_client.get_caller_identity()
        return identity.get("Account")
    except (BotoCoreError, ClientError):
        return None