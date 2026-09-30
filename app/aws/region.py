"""AWS region configuration."""

DEFAULT_AWS_REGION = "us-east-1"

SUPPORTED_AWS_REGIONS = {
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-northeast-1",
    "eu-west-1",
    "eu-west-2",
    "eu-central-1",
}


def validate_aws_region(region: str) -> str:
    """Validate and return a supported AWS region."""
    normalized_region = region.strip().lower()

    if normalized_region not in SUPPORTED_AWS_REGIONS:
        raise ValueError(
            f"Unsupported AWS region '{region}'. "
            f"Supported regions: {', '.join(sorted(SUPPORTED_AWS_REGIONS))}"
        )

    return normalized_region