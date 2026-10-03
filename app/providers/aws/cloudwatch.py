from datetime import datetime, timedelta, timezone
from statistics import fmean
from typing import Any

from app.audit.models import AuditFinding, FindingSeverity
from app.providers.aws.retry import retry_aws_operation


DEFAULT_ANALYSIS_PERIOD_DAYS = 14
DEFAULT_LOW_CPU_THRESHOLD = 20.0
DEFAULT_PERIOD_SECONDS = 3600


class CloudWatchCPUAnalyzer:
    """Analyze EC2 CPU utilization using CloudWatch metrics."""

    def __init__(
        self,
        cloudwatch_client: Any,
        low_cpu_threshold: float = DEFAULT_LOW_CPU_THRESHOLD,
        analysis_period_days: int = DEFAULT_ANALYSIS_PERIOD_DAYS,
        period_seconds: int = DEFAULT_PERIOD_SECONDS,
    ) -> None:
        if not 0 <= low_cpu_threshold <= 100:
            raise ValueError("low_cpu_threshold must be between 0 and 100.")

        if analysis_period_days <= 0:
            raise ValueError("analysis_period_days must be greater than 0.")

        if period_seconds <= 0:
            raise ValueError("period_seconds must be greater than 0.")

        self.cloudwatch_client = cloudwatch_client
        self.low_cpu_threshold = low_cpu_threshold
        self.analysis_period_days = analysis_period_days
        self.period_seconds = period_seconds

    @retry_aws_operation()
    def _get_cpu_datapoints(
        self,
        instance_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Retrieve CPU utilization datapoints from CloudWatch."""
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": instance_id,
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=self.period_seconds,
            Statistics=["Average"],
            Unit="Percent",
        )

        return response.get("Datapoints", [])

    def calculate_average_cpu(
        self,
        instance_id: str,
        end_time: datetime | None = None,
    ) -> float | None:
        """
        Calculate average CPU utilization for the configured analysis period.

        Returns None when CloudWatch has no usable CPU datapoints.
        """
        if not instance_id.strip():
            raise ValueError("instance_id cannot be empty.")

        if end_time is None:
            end_time = datetime.now(timezone.utc)

        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        start_time = end_time - timedelta(days=self.analysis_period_days)

        datapoints = self._get_cpu_datapoints(
            instance_id=instance_id,
            start_time=start_time,
            end_time=end_time,
        )

        cpu_values = [
            float(datapoint["Average"])
            for datapoint in datapoints
            if datapoint.get("Average") is not None
        ]

        if not cpu_values:
            return None

        return fmean(cpu_values)

    def analyze_instance(
        self,
        instance_id: str,
        region: str,
        account_id: str | None = None,
        end_time: datetime | None = None,
    ) -> AuditFinding | None:
        """
        Analyze one EC2 instance and create a finding when CPU utilization
        is below the configured threshold.

        Returns None when there is insufficient CloudWatch data or when
        utilization is not below the threshold.
        """
        average_cpu = self.calculate_average_cpu(
            instance_id=instance_id,
            end_time=end_time,
        )

        if average_cpu is None:
            return None

        if average_cpu >= self.low_cpu_threshold:
            return None

        description = (
            f"EC2 instance '{instance_id}' has average CPU utilization of "
            f"{average_cpu:.2f}% over the last "
            f"{self.analysis_period_days} days, which is below the configured "
            f"low-utilization threshold of {self.low_cpu_threshold:.2f}%."
        )

        return AuditFinding(
            resource_type="EC2 Instance",
            resource_id=instance_id,
            region=region,
            account_id=account_id,
            severity=FindingSeverity.MEDIUM,
            description=description,
            metadata={
                "metric": "CPUUtilization",
                "namespace": "AWS/EC2",
                "average_cpu_utilization": round(average_cpu, 2),
                "low_cpu_threshold": self.low_cpu_threshold,
                "analysis_period_days": self.analysis_period_days,
            },
        )

    def analyze_instances(
        self,
        instance_ids: list[str],
        region: str,
        account_id: str | None = None,
        end_time: datetime | None = None,
    ) -> list[AuditFinding]:
        """Analyze multiple EC2 instances and return low-utilization findings."""
        findings: list[AuditFinding] = []

        for instance_id in instance_ids:
            finding = self.analyze_instance(
                instance_id=instance_id,
                region=region,
                account_id=account_id,
                end_time=end_time,
            )

            if finding is not None:
                findings.append(finding)

        return findings