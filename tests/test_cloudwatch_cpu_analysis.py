from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from app.audit.models import FindingSeverity
from app.providers.aws.cloudwatch import CloudWatchCPUAnalyzer
from app.providers.aws.retry import AWSRetryError


END_TIME = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


def create_cloudwatch_client(datapoints):
    client = MagicMock()
    client.get_metric_statistics.return_value = {
        "Datapoints": datapoints,
    }
    return client


def test_calculate_average_cpu():
    client = create_cloudwatch_client(
        [
            {"Average": 10.0},
            {"Average": 20.0},
            {"Average": 30.0},
        ]
    )

    analyzer = CloudWatchCPUAnalyzer(client)

    average = analyzer.calculate_average_cpu(
        "i-1234567890",
        end_time=END_TIME,
    )

    assert average == pytest.approx(20.0)

    client.get_metric_statistics.assert_called_once()

    call_kwargs = client.get_metric_statistics.call_args.kwargs

    assert call_kwargs["Namespace"] == "AWS/EC2"
    assert call_kwargs["MetricName"] == "CPUUtilization"
    assert call_kwargs["Dimensions"] == [
        {
            "Name": "InstanceId",
            "Value": "i-1234567890",
        }
    ]
    assert call_kwargs["StartTime"] == END_TIME - timedelta(days=14)
    assert call_kwargs["EndTime"] == END_TIME
    assert call_kwargs["Statistics"] == ["Average"]
    assert call_kwargs["Unit"] == "Percent"


def test_low_cpu_creates_audit_finding():
    client = create_cloudwatch_client(
        [
            {"Average": 8.0},
            {"Average": 12.0},
            {"Average": 10.0},
        ]
    )

    analyzer = CloudWatchCPUAnalyzer(
        client,
        low_cpu_threshold=20.0,
    )

    finding = analyzer.analyze_instance(
        instance_id="i-lowcpu",
        region="ap-south-1",
        account_id="123456789012",
        end_time=END_TIME,
    )

    assert finding is not None
    assert finding.resource_type == "EC2 Instance"
    assert finding.resource_id == "i-lowcpu"
    assert finding.region == "ap-south-1"
    assert finding.account_id == "123456789012"
    assert finding.severity == FindingSeverity.MEDIUM

    assert finding.metadata["metric"] == "CPUUtilization"
    assert finding.metadata["average_cpu_utilization"] == 10.0
    assert finding.metadata["low_cpu_threshold"] == 20.0
    assert finding.metadata["analysis_period_days"] == 14


def test_cpu_above_threshold_does_not_create_finding():
    client = create_cloudwatch_client(
        [
            {"Average": 40.0},
            {"Average": 50.0},
            {"Average": 60.0},
        ]
    )

    analyzer = CloudWatchCPUAnalyzer(
        client,
        low_cpu_threshold=20.0,
    )

    finding = analyzer.analyze_instance(
        instance_id="i-normal",
        region="ap-south-1",
        end_time=END_TIME,
    )

    assert finding is None


def test_missing_cloudwatch_data_is_handled_gracefully():
    client = create_cloudwatch_client([])

    analyzer = CloudWatchCPUAnalyzer(client)

    average = analyzer.calculate_average_cpu(
        "i-no-data",
        end_time=END_TIME,
    )

    assert average is None

    finding = analyzer.analyze_instance(
        instance_id="i-no-data",
        region="ap-south-1",
        end_time=END_TIME,
    )

    assert finding is None


def test_datapoints_without_average_are_ignored():
    client = create_cloudwatch_client(
        [
            {},
            {"Average": None},
            {"Average": 10.0},
            {"Average": 20.0},
        ]
    )

    analyzer = CloudWatchCPUAnalyzer(client)

    average = analyzer.calculate_average_cpu(
        "i-partial-data",
        end_time=END_TIME,
    )

    assert average == pytest.approx(15.0)


def test_custom_cpu_threshold_is_used():
    client = create_cloudwatch_client(
        [
            {"Average": 25.0},
            {"Average": 30.0},
        ]
    )

    # Average CPU = 27.5%.
    # With threshold 25%, 27.5% is not low enough.
    analyzer = CloudWatchCPUAnalyzer(
        client,
        low_cpu_threshold=25.0,
    )

    finding = analyzer.analyze_instance(
        instance_id="i-custom-threshold",
        region="ap-south-1",
        end_time=END_TIME,
    )

    assert finding is None

    # With threshold 30%, 27.5% is below the threshold.
    analyzer = CloudWatchCPUAnalyzer(
        client,
        low_cpu_threshold=30.0,
    )

    finding = analyzer.analyze_instance(
        instance_id="i-custom-threshold",
        region="ap-south-1",
        end_time=END_TIME,
    )

    assert finding is not None
    assert finding.metadata["low_cpu_threshold"] == 30.0


def test_retryable_cloudwatch_error_is_retried():
    error = ClientError(
        {
            "Error": {
                "Code": "ThrottlingException",
                "Message": "Rate exceeded",
            }
        },
        "GetMetricStatistics",
    )

    client = MagicMock()

    client.get_metric_statistics.side_effect = [
        error,
        error,
        {
            "Datapoints": [
                {"Average": 10.0},
            ]
        },
    ]

    analyzer = CloudWatchCPUAnalyzer(client)

    with patch("app.providers.aws.retry.time.sleep"):
        average = analyzer.calculate_average_cpu(
            "i-retry",
            end_time=END_TIME,
        )

    assert average == pytest.approx(10.0)
    assert client.get_metric_statistics.call_count == 3


def test_retryable_error_raises_after_retries_are_exhausted():
    error = ClientError(
        {
            "Error": {
                "Code": "ThrottlingException",
                "Message": "Rate exceeded",
            }
        },
        "GetMetricStatistics",
    )

    client = MagicMock()
    client.get_metric_statistics.side_effect = error

    analyzer = CloudWatchCPUAnalyzer(client)

    with (
        patch("app.providers.aws.retry.time.sleep"),
        pytest.raises(AWSRetryError),
    ):
        analyzer.calculate_average_cpu(
            "i-exhausted",
            end_time=END_TIME,
        )

    # Initial attempt + 3 retries.
    assert client.get_metric_statistics.call_count == 4


def test_non_retryable_cloudwatch_error_is_not_retried():
    error = ClientError(
        {
            "Error": {
                "Code": "AccessDeniedException",
                "Message": "Access denied",
            }
        },
        "GetMetricStatistics",
    )

    client = MagicMock()
    client.get_metric_statistics.side_effect = error

    analyzer = CloudWatchCPUAnalyzer(client)

    with pytest.raises(ClientError):
        analyzer.calculate_average_cpu(
            "i-access-denied",
            end_time=END_TIME,
        )

    assert client.get_metric_statistics.call_count == 1


def test_invalid_threshold_is_rejected():
    client = MagicMock()

    with pytest.raises(ValueError):
        CloudWatchCPUAnalyzer(
            client,
            low_cpu_threshold=101.0,
        )


def test_multiple_instances_return_only_low_cpu_findings():
    client = MagicMock()

    client.get_metric_statistics.side_effect = [
        {
            "Datapoints": [
                {"Average": 10.0},
                {"Average": 15.0},
            ]
        },
        {
            "Datapoints": [
                {"Average": 40.0},
                {"Average": 50.0},
            ]
        },
    ]

    analyzer = CloudWatchCPUAnalyzer(
        client,
        low_cpu_threshold=20.0,
    )

    findings = analyzer.analyze_instances(
        instance_ids=["i-low", "i-normal"],
        region="ap-south-1",
        end_time=END_TIME,
    )

    assert len(findings) == 1
    assert findings[0].resource_id == "i-low"