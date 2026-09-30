from app.audit.aggregation import AggregatedAuditResult
from app.audit.models import AuditFinding, FindingSeverity


def create_finding(
    resource_type: str,
    resource_id: str,
    severity: FindingSeverity = FindingSeverity.MEDIUM,
    estimated_savings: float | None = None,
    metadata: dict[str, object] | None = None,
) -> AuditFinding:
    """Create a test audit finding."""

    return AuditFinding(
        resource_type=resource_type,
        resource_id=resource_id,
        region="us-east-1",
        severity=severity,
        description=f"Test finding for {resource_id}",
        estimated_savings=estimated_savings,
        metadata=metadata or {},
    )


def test_collect_findings_combines_multiple_scanners() -> None:
    """Findings from multiple scanners should be combined."""

    from app.audit.aggregation import collect_findings

    ebs_findings = [
        create_finding("EBS Volume", "vol-001"),
    ]

    ec2_findings = [
        create_finding("EC2 Instance", "i-001"),
        create_finding("EC2 Instance", "i-002"),
    ]

    result = collect_findings([ebs_findings, ec2_findings])

    assert len(result) == 3
    assert result[0].resource_id == "vol-001"
    assert result[1].resource_id == "i-001"
    assert result[2].resource_id == "i-002"


def test_collect_findings_handles_empty_scanner_result() -> None:
    """An empty scanner result should not affect collection."""

    from app.audit.aggregation import collect_findings

    ebs_findings = [
        create_finding("EBS Volume", "vol-001"),
    ]

    result = collect_findings([ebs_findings, []])

    assert len(result) == 1
    assert result[0].resource_id == "vol-001"


def test_collect_findings_handles_all_empty_results() -> None:
    """All empty scanner results should produce an empty collection."""

    from app.audit.aggregation import collect_findings

    result = collect_findings([[], []])

    assert result == []


def test_aggregated_result_reports_total_findings() -> None:
    """Aggregated result should report the total number of findings."""

    findings = [
        create_finding("EBS Volume", "vol-001"),
        create_finding("EC2 Instance", "i-001"),
        create_finding("EC2 Instance", "i-002"),
    ]

    result = AggregatedAuditResult(findings)

    assert result.total_findings == 3


def test_aggregated_result_groups_findings_by_resource_type() -> None:
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


def test_aggregated_result_groups_findings_by_severity() -> None:
    """Findings should be grouped by severity."""

    findings = [
        create_finding(
            "EBS Volume",
            "vol-001",
            severity=FindingSeverity.HIGH,
        ),
        create_finding(
            "EC2 Instance",
            "i-001",
            severity=FindingSeverity.MEDIUM,
        ),
        create_finding(
            "EC2 Instance",
            "i-002",
            severity=FindingSeverity.HIGH,
        ),
    ]

    result = AggregatedAuditResult(findings)

    assert result.findings_by_severity == {
        "HIGH": 2,
        "MEDIUM": 1,
    }


def test_aggregated_result_calculates_potential_savings() -> None:
    """Aggregated result should calculate total potential savings."""

    findings = [
        create_finding(
            "EBS Volume",
            "vol-001",
            estimated_savings=12.50,
        ),
        create_finding(
            "EC2 Instance",
            "i-001",
            estimated_savings=25.00,
        ),
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


def test_aggregated_result_groups_findings_by_finding_type() -> None:
    """Findings should be grouped by their finding type."""

    findings = [
        create_finding(
            "EBS Volume",
            "vol-001",
            metadata={"finding_type": "unattached_volume"},
        ),
        create_finding(
            "EBS Volume",
            "vol-002",
            metadata={"finding_type": "unattached_volume"},
        ),
        create_finding(
            "EC2 Instance",
            "i-001",
            metadata={"finding_type": "oversized_instance"},
        ),
    ]

    result = AggregatedAuditResult(findings)

    assert result.findings_by_finding_type == {
        "unattached_volume": 2,
        "oversized_instance": 1,
    }


def test_aggregated_result_uses_unknown_for_missing_finding_type() -> None:
    """Findings without a finding type should use the unknown category."""

    findings = [
        create_finding("EBS Volume", "vol-001"),
    ]

    result = AggregatedAuditResult(findings)

    assert result.findings_by_finding_type == {
        "unknown": 1,
    }