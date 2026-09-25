import unittest
from unittest.mock import patch

from botocore.exceptions import ClientError

from app.providers.aws.retry import (
    AWSRetryError,
    is_retryable_error,
    retry_aws_operation,
)


def client_error(code: str) -> ClientError:
    return ClientError(
        {
            "Error": {
                "Code": code,
                "Message": "AWS error",
            }
        },
        "TestOperation",
    )


class TestAWSRetry(unittest.TestCase):

    def test_throttling_error_is_retryable(self):
        error = client_error("ThrottlingException")

        self.assertTrue(is_retryable_error(error))

    def test_temporary_service_error_is_retryable(self):
        error = client_error("ServiceUnavailable")

        self.assertTrue(is_retryable_error(error))

    def test_non_retryable_error(self):
        error = client_error("AccessDenied")

        self.assertFalse(is_retryable_error(error))

    @patch("app.providers.aws.retry.time.sleep")
    def test_operation_retries_after_throttling(
        self,
        mock_sleep,
    ):
        attempts = 0

        @retry_aws_operation(
            max_retries=2,
            backoff_factor=1,
        )
        def operation():
            nonlocal attempts
            attempts += 1

            if attempts < 3:
                raise client_error("ThrottlingException")

            return "success"

        result = operation()

        self.assertEqual(result, "success")
        self.assertEqual(attempts, 3)

        self.assertEqual(
            mock_sleep.call_count,
            2,
        )

        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)

    @patch("app.providers.aws.retry.time.sleep")
    def test_non_retryable_error_is_not_retried(
        self,
        mock_sleep,
    ):
        attempts = 0

        @retry_aws_operation(
            max_retries=3,
            backoff_factor=1,
        )
        def operation():
            nonlocal attempts
            attempts += 1
            raise client_error("AccessDenied")

        with self.assertRaises(ClientError):
            operation()

        self.assertEqual(attempts, 1)
        mock_sleep.assert_not_called()

    @patch("app.providers.aws.retry.time.sleep")
    def test_exhausted_retries_raise_clear_error(
        self,
        mock_sleep,
    ):
        attempts = 0

        @retry_aws_operation(
            max_retries=2,
            backoff_factor=1,
        )
        def operation():
            nonlocal attempts
            attempts += 1
            raise client_error("ThrottlingException")

        with self.assertRaises(AWSRetryError) as context:
            operation()

        self.assertEqual(attempts, 3)

        self.assertIn(
            "failed after 2 retries",
            str(context.exception),
        )

        self.assertEqual(
            mock_sleep.call_count,
            2,
        )

    def test_invalid_retry_configuration(self):
        with self.assertRaises(ValueError):
            retry_aws_operation(max_retries=-1)

        with self.assertRaises(ValueError):
            retry_aws_operation(backoff_factor=-1)


if __name__ == "__main__":
    unittest.main()