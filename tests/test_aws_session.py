import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, NoCredentialsError

from app.aws.session import (
    AWSAuthenticationError,
    assume_aws_role,
    create_aws_session,
    get_aws_session,
    validate_aws_credentials,
)


class TestAWSSession(unittest.TestCase):

    @patch("app.aws.session.boto3.Session")
    def test_create_default_session(self, mock_session):
        create_aws_session()

        mock_session.assert_called_once_with()

    @patch("app.aws.session.boto3.Session")
    def test_create_session_with_profile(self, mock_session):
        create_aws_session("test-profile")

        mock_session.assert_called_once_with(
            profile_name="test-profile"
        )

    @patch("app.aws.session.boto3.Session")
    def test_create_session_with_invalid_profile(self, mock_session):
        mock_session.side_effect = ValueError(
            "The config profile (invalid-profile) could not be found"
        )

        with self.assertRaises(AWSAuthenticationError) as context:
            create_aws_session("invalid-profile")

        self.assertIn(
            "Unable to create AWS session",
            str(context.exception)
        )

    def test_assume_aws_role(self):
        mock_session = Mock()
        mock_sts = Mock()

        mock_session.client.return_value = mock_sts
        mock_session.region_name = "us-east-1"

        mock_sts.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "temporary-access-key",
                "SecretAccessKey": "temporary-secret-key",
                "SessionToken": "temporary-session-token",
            }
        }

        with patch("app.aws.session.boto3.Session") as mock_boto_session:
            result = assume_aws_role(
                mock_session,
                "arn:aws:iam::123456789012:role/TestRole",
            )

        mock_sts.assume_role.assert_called_once_with(
            RoleArn="arn:aws:iam::123456789012:role/TestRole",
            RoleSessionName="cloud-infrastructure-auditor",
        )

        mock_boto_session.assert_called_once_with(
            aws_access_key_id="temporary-access-key",
            aws_secret_access_key="temporary-secret-key",
            aws_session_token="temporary-session-token",
            region_name="us-east-1",
        )

        self.assertEqual(
            result,
            mock_boto_session.return_value,
        )

    def test_assume_aws_role_with_empty_arn(self):
        mock_session = Mock()

        with self.assertRaises(AWSAuthenticationError) as context:
            assume_aws_role(mock_session, "")

        self.assertIn(
            "IAM role ARN cannot be empty",
            str(context.exception),
        )

        mock_session.client.assert_not_called()

    def test_assume_aws_role_failure(self):
        mock_session = Mock()
        mock_sts = Mock()

        mock_session.client.return_value = mock_sts

        error_response = {
            "Error": {
                "Code": "AccessDenied",
                "Message": "User is not authorized to assume the role",
            }
        }

        mock_sts.assume_role.side_effect = ClientError(
            error_response,
            "AssumeRole",
        )

        with self.assertRaises(AWSAuthenticationError) as context:
            assume_aws_role(
                mock_session,
                "arn:aws:iam::123456789012:role/TestRole",
            )

        self.assertIn(
            "Unable to assume IAM role",
            str(context.exception),
        )

    def test_validate_valid_credentials(self):
        mock_session = Mock()
        mock_sts = Mock()

        mock_session.client.return_value = mock_sts

        result = validate_aws_credentials(mock_session)

        self.assertTrue(result)
        mock_sts.get_caller_identity.assert_called_once()

    def test_validate_missing_credentials(self):
        mock_session = Mock()

        mock_session.client.side_effect = NoCredentialsError(
            error_msg="Credentials not found"
        )

        with self.assertRaises(AWSAuthenticationError) as context:
            validate_aws_credentials(mock_session)

        self.assertIn(
            "AWS credentials were not found",
            str(context.exception)
        )

    def test_validate_invalid_credentials(self):
        mock_session = Mock()

        error_response = {
            "Error": {
                "Code": "InvalidClientTokenId",
                "Message": (
                    "The security token included in the request is invalid"
                ),
            }
        }

        mock_session.client.side_effect = ClientError(
            error_response,
            "GetCallerIdentity",
        )

        with self.assertRaises(AWSAuthenticationError) as context:
            validate_aws_credentials(mock_session)

        self.assertIn(
            "AWS authentication failed",
            str(context.exception)
        )

    @patch("app.aws.session.validate_aws_credentials")
    @patch("app.aws.session.create_aws_session")
    def test_get_aws_session(
        self,
        mock_create_session,
        mock_validate,
    ):
        mock_session = Mock()
        mock_create_session.return_value = mock_session

        result = get_aws_session("test-profile")

        mock_create_session.assert_called_once_with("test-profile")
        mock_validate.assert_called_once_with(mock_session)

        self.assertEqual(result, mock_session)

    @patch("app.aws.session.validate_aws_credentials")
    @patch("app.aws.session.assume_aws_role")
    @patch("app.aws.session.create_aws_session")
    def test_get_aws_session_with_role(
        self,
        mock_create_session,
        mock_assume_role,
        mock_validate,
    ):
        source_session = Mock()
        assumed_role_session = Mock()

        mock_create_session.return_value = source_session
        mock_assume_role.return_value = assumed_role_session

        result = get_aws_session(
            profile_name="test-profile",
            role_arn="arn:aws:iam::123456789012:role/TestRole",
        )

        mock_create_session.assert_called_once_with("test-profile")
        mock_assume_role.assert_called_once_with(
            source_session,
            "arn:aws:iam::123456789012:role/TestRole",
        )
        mock_validate.assert_called_once_with(assumed_role_session)

        self.assertEqual(result, assumed_role_session)


if __name__ == "__main__":
    unittest.main()