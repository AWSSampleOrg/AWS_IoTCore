from logging import getLogger, StreamHandler, DEBUG
import os
import boto3
import json
import base64
import time
from datetime import datetime

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

iot_client = boto3.client("iot")
endpoint_response = iot_client.describe_endpoint(endpointType="iot:Data-ATS")
endpoint = endpoint_response["endpointAddress"]

iot_data_client = boto3.client("iot-jobs-data", endpoint_url=f"https://{endpoint}")


def create_command(command_id, payload_content):
    """Create a command with the given payload"""
    logger.info(f"\n=== Creating Command: {command_id} ===")

    # Encode payload to base64
    payload_bytes = json.dumps(payload_content).encode("utf-8")
    payload_base64 = base64.b64encode(payload_bytes).decode("utf-8")

    try:
        response = iot_client.create_command(
            commandId=command_id,
            displayName=f"Test Command {datetime.now().strftime('%H:%M:%S')}",
            description="Test command created by test_commands.py",
            namespace="AWS-IoT",
            payload={"content": payload_base64, "contentType": "application/json"},
        )
        logger.info(f"✓ Command created: {response['commandArn']}")
        return response
    except iot_client.exceptions.ResourceAlreadyExistsException:
        logger.warning(f"✓ Command already exists: {command_id}")
    except Exception as e:
        logger.error(f"✗ Error creating command: {e}")
        raise


def start_command_execution(command_arn: str, target_arn: str, timeout_seconds=300):
    """Start command execution on the target thing"""
    logger.info(f"\n=== Starting Command Execution ===")

    try:
        response = iot_data_client.start_command_execution(
            commandArn=command_arn,
            targetArn=target_arn,
            executionTimeoutSeconds=timeout_seconds,
        )
        execution_id = response["executionId"]
        logger.info(f"✓ Execution started: {execution_id}")
        return execution_id
    except Exception as e:
        logger.error(f"✗ Error starting execution: {e}")
        raise


def get_command_execution(execution_id: str, target_arn: str):
    """Get command execution status"""

    try:
        response = iot_client.get_command_execution(
            executionId=execution_id, targetArn=target_arn, includeResult=True
        )
        return response
    except Exception as e:
        logger.error(f"✗ Error getting execution: {e}")
        raise


def monitor_execution(execution_id: str, target_arn: str, max_wait=30):
    """Monitor command execution until completion or timeout"""
    logger.info(f"\n=== Monitoring Execution ===")

    start_time = time.time()
    while time.time() - start_time < max_wait:
        execution = get_command_execution(execution_id, target_arn)
        status = execution["status"]

        logger.debug(f"Status: {status}", end="")

        if "statusReason" in execution:
            reason = execution["statusReason"]
            logger.debug(
                f" - {reason.get('reasonCode', '')}: {reason.get('reasonDescription', '')}"
            )

        # Terminal statuses
        if status in ["SUCCEEDED", "FAILED", "REJECTED"]:
            logger.info(f"\n✓ Execution completed with status: {status}")
            if "result" in execution:
                logger.debug(f"Result: {json.dumps(execution['result'], indent=2)}")
            return execution

        if status == "TIMED_OUT":
            logger.warning(f"\n:warning: Execution timed out")
            return execution

        time.sleep(2)

    logger.warning(f"\n:warning: Monitoring timeout after {max_wait}s")
    return get_command_execution(execution_id, target_arn)


def main(target_arn: str):
    logger.debug("=" * 60)
    logger.debug("AWS IoT Remote Commands Test")
    logger.debug("=" * 60)

    # Test 1: Simple Hello Command
    command_id = f"HelloCommand-{int(time.time())}"
    payload = {
        "message": "Hello from IoT Core!",
        "action": "test",
        "timestamp": datetime.now().isoformat(),
    }

    # Create command
    command_response = create_command(command_id, payload)
    command_arn = command_response["commandArn"]

    # Start execution
    execution_id = start_command_execution(command_arn, target_arn)

    # Monitor execution
    final_status = monitor_execution(execution_id, target_arn)

    logger.info("\n" + "=" * 60)
    logger.info("Test Complete")
    logger.info("=" * 60)
    logger.debug(f"\nCommand ID: {command_id}")
    logger.debug(f"Execution ID: {execution_id}")
    logger.debug(f"Final Status: {final_status['status']}")

    # Cleanup option
    logger.info(f"\nTo delete the command, run:")
    logger.info(f"aws iot delete-command --command-id {command_id}")


if __name__ == "__main__":
    target_arn = ""
    main(target_arn)
