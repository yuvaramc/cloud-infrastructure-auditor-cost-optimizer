import pytest

from app.aws.region import (
    DEFAULT_AWS_REGION,
    SUPPORTED_AWS_REGIONS,
    validate_aws_region,
)


def test_default_aws_region():
    assert DEFAULT_AWS_REGION == "us-east-1"


def test_supported_regions_are_defined():
    assert "us-east-1" in SUPPORTED_AWS_REGIONS
    assert "ap-south-1" in SUPPORTED_AWS_REGIONS


def test_validate_aws_region_returns_normalized_region():
    assert validate_aws_region("AP-SOUTH-1") == "ap-south-1"


def test_validate_aws_region_strips_whitespace():
    assert validate_aws_region("  ap-south-1  ") == "ap-south-1"


def test_validate_aws_region_rejects_invalid_region():
    with pytest.raises(ValueError, match="Unsupported AWS region"):
        validate_aws_region("invalid-region")