import unittest
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError, NoCredentialsError

from app.aws.session import (
    AWSAuthenticationError,
    create_aws_session,
    validate_aws_credentials,
    get_aws_session,
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
                "Message": "The security token included in the request is invalid",
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

        self.assertIs(result, mock_session)

        mock_create_session.assert_called_once_with("test-profile")
        mock_validate.assert_called_once_with(mock_session)


if __name__ == "__main__":
    unittest.main()