from app.audit.aggregation import AggregatedAuditResult, collect_findings
from app.audit.models import AuditFinding, FindingSeverity


def create_finding(
    resource_type: str,
    resource_id: str,
    severity: FindingSeverity = FindingSeverity.MEDIUM,
    estimated_savings: float | None = None,
) -> AuditFinding:
    """Create a test audit finding."""

    return AuditFinding(
        resource_type=resource_type,
        resource_id=resource_id,
        region="us-east-1",
        severity=severity,
        description=f"Finding for {resource_id}",
        estimated_savings=estimated_savings,
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


def test_aggregated_result_tracks_total_findings() -> None:
    """Aggregated results should expose the total finding count."""

    findings = [
        create_finding("EBS Volume", "vol-001"),
        create_finding("EC2 Instance", "i-001"),
    ]

    result = AggregatedAuditResult(findings)

    assert result.total_findings == 2


def test_aggregated_result_groups_by_resource_type() -> None:
    """Findings should be grouped by resource type."""

    findings = [
        create_finding("EBS Volume", "vol-001"),
        create_finding("EBS Volume", "vol-002"),
        create_finding("EC2 Instance", "i-001"),
    ]

    result = AggregatedAuditResult(findings)

    assert result.findings_by_resource_type == {
        "EBS Volume": 2,
        "EC2 Instance": 1,
    }


def test_aggregated_result_groups_by_severity() -> None:
    """Findings should be grouped by severity."""

    findings = [
        create_finding("EBS Volume", "vol-001", FindingSeverity.MEDIUM),
        create_finding("EBS Volume", "vol-002", FindingSeverity.HIGH),
        create_finding("EC2 Instance", "i-001", FindingSeverity.HIGH),
    ]

    result = AggregatedAuditResult(findings)

    assert result.findings_by_severity == {
        "MEDIUM": 1,
        "HIGH": 2,
    }


def test_aggregated_result_calculates_potential_savings() -> None:
    """Potential savings should be summed across findings."""

    findings = [
        create_finding("EBS Volume", "vol-001", estimated_savings=12.50),
        create_finding("EC2 Instance", "i-001", estimated_savings=25.00),
        create_finding("EBS Volume", "vol-002"),
    ]

    result = AggregatedAuditResult(findings)

    assert result.total_potential_savings == 37.50

def test_aggregate_scanner_results_returns_unified_result() -> None:
    """Scanner results should be converted into an aggregated result."""

    from app.audit.aggregation import aggregate_scanner_results

    ebs_findings = [
        create_finding("EBS Volume", "vol-001"),
    ]

    ec2_findings = [
        create_finding("EC2 Instance", "i-001"),
        create_finding("EC2 Instance", "i-002"),
    ]

    result = aggregate_scanner_results([ebs_findings, ec2_findings])

    assert result.total_findings == 3
    assert result.findings_by_resource_type == {
        "EBS Volume": 1,
        "EC2 Instance": 2,
    }
