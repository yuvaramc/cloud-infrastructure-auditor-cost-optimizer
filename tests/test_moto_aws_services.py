from unittest.mock import patch

import pytest

import boto3
from botocore.exceptions import ClientError
from moto import mock_aws

from app.aws.session import assume_aws_role, validate_aws_credentials
from app.cleanup.preview import build_cleanup_preview
from app.scanners.ebs import EBSScannerError, scan_ebs_volumes


@mock_aws
def test_scan_ebs_volume_with_moto():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    ec2 = session.client("ec2")

    response = ec2.create_volume(
        AvailabilityZone="ap-south-1a",
        Size=20,
        VolumeType="gp3",
    )

    volume_id = response["VolumeId"]

    findings = scan_ebs_volumes(session)

    assert len(findings) == 1
    assert findings[0].resource_id == volume_id
    assert findings[0].resource_type == "EBS Volume"
    assert findings[0].region == "ap-south-1"
    assert findings[0].metadata["state"] == "available"


@mock_aws
def test_scan_ebs_volumes_with_no_resources():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    findings = scan_ebs_volumes(session)

    assert findings == []


@mock_aws
def test_scan_ebs_ignores_attached_volume():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    ec2 = session.client("ec2")

    instance = ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
    )["Instances"][0]

    volume = ec2.create_volume(
        AvailabilityZone="ap-south-1a",
        Size=20,
        VolumeType="gp3",
    )

    ec2.attach_volume(
        VolumeId=volume["VolumeId"],
        InstanceId=instance["InstanceId"],
        Device="/dev/sdf",
    )

    findings = scan_ebs_volumes(session)

    assert findings == []


@mock_aws
def test_validate_aws_credentials_with_moto():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    assert validate_aws_credentials(session) is True


@mock_aws
def test_assume_aws_role_with_moto():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    assumed_session = assume_aws_role(
        session,
        "arn:aws:iam::123456789012:role/TestRole",
    )

    assert assumed_session.region_name == "ap-south-1"
    assert assumed_session.get_credentials() is not None


@mock_aws
def test_cleanup_preview_does_not_modify_moto_resource():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    ec2 = session.client("ec2")

    volume = ec2.create_volume(
        AvailabilityZone="ap-south-1a",
        Size=20,
        VolumeType="gp3",
    )

    volume_id = volume["VolumeId"]

    findings = scan_ebs_volumes(session)
    preview = build_cleanup_preview(findings)

    assert preview.total_actions == 1
    assert preview.actions[0].resource_id == volume_id

    remaining = ec2.describe_volumes(VolumeIds=[volume_id])

    assert remaining["Volumes"][0]["VolumeId"] == volume_id
    assert remaining["Volumes"][0]["State"] == "available"


@mock_aws
def test_scan_ebs_volumes_handles_aws_error():
    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name="ap-south-1",
    )

    error = ClientError(
        {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access denied",
            }
        },
        "DescribeVolumes",
    )

    with patch.object(session, "client", side_effect=error):
        try:
            scan_ebs_volumes(session)
            assert False, "Expected EBSScannerError"
        except EBSScannerError as exc:
            assert "Unable to scan EBS volumes" in str(exc)
