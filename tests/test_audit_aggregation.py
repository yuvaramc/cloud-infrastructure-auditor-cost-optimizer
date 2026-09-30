from app.audit.aggregation import collect_findings
from app.audit.models import AuditFinding, FindingSeverity


def create_finding(
    resource_type: str,
    resource_id: str,
) -> AuditFinding:
    """Create a test audit finding."""

    return AuditFinding(
        resource_type=resource_type,
        resource_id=resource_id,
        region="us-east-1",
        severity=FindingSeverity.MEDIUM,
        description=f"Finding for {resource_id}",
    )


def test_collect_findings_from_multiple_scanners() -> None:
    """Findings from multiple scanners should be combined."""

    ebs_findings = [
        create_finding("EBS Volume", "vol-001"),
        create_finding("EBS Volume", "vol-002"),
    ]

    ec2_findings = [
        create_finding("EC2 Instance", "i-001"),
    ]

    findings = collect_findings([ebs_findings, ec2_findings])

    assert len(findings) == 3
    assert findings[0].resource_id == "vol-001"
    assert findings[1].resource_id == "vol-002"
    assert findings[2].resource_id == "i-001"


def test_collect_findings_handles_empty_scanner_result() -> None:
    """An empty scanner result should not affect collected findings."""

    ebs_findings = [
        create_finding("EBS Volume", "vol-001"),
    ]

    findings = collect_findings([ebs_findings, []])

    assert len(findings) == 1
    assert findings[0].resource_id == "vol-001"


def test_collect_findings_handles_all_empty_results() -> None:
    """Multiple scanners returning no findings should produce an empty list."""

    findings = collect_findings([[], []])

    assert findings == []
