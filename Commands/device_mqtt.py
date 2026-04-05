import base64
import json
from logging import getLogger, StreamHandler, DEBUG
import os
import time
import mqtt3
import awscrt

# Command topics (wildcard for any execution ID)
THING_NAME = "Thing1"
COMMAND_REQUEST_TOPIC = f"$aws/commands/things/{THING_NAME}/executions/+/request/json"

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False


def on_command_received(mqtt_connection: awscrt.mqtt.Connection):
    def _on_command_received(topic, payload, **kwargs):
        logger.debug(
            "------------------------on_command_received------------------------"
        )
        logger.debug(f"Topic: {topic}")

        # Extract execution ID from topic
        topic_parts = topic.split("/")
        execution_id = topic_parts[5]
        logger.debug(f"Execution ID: {execution_id}")

        # Decode bytes to string if needed
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        # The payload is base64-encoded directly
        try:
            decoded_payload = base64.b64decode(payload).decode("utf-8")
            logger.debug(
                "------------------------Decoded Payload------------------------"
            )
            logger.info(decoded_payload)
            command_data = json.loads(decoded_payload)
            logger.info(command_data)
        except Exception as e:
            logger.warning(f"Could not decode payload: {e}")
            command_data = {}

        # Response topic for this specific execution
        response_topic = (
            f"$aws/commands/things/{THING_NAME}/executions/{execution_id}/response/json"
        )

        # Update to IN_PROGRESS
        mqtt_connection.publish(
            topic=response_topic,
            payload=json.dumps(
                {
                    "status": "IN_PROGRESS",
                    "statusReason": {
                        "reasonCode": "PROCESSING",
                        "reasonDescription": "Device is processing the command",
                    },
                }
            ),
            qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        )
        logger.info("Status: IN_PROGRESS")

        # Simulate command processing
        time.sleep(1)

        # Update to SUCCEEDED
        mqtt_connection.publish(
            topic=response_topic,
            payload=json.dumps(
                {
                    "status": "SUCCEEDED",
                    "statusReason": {
                        "reasonCode": "SUCCESS",
                        "reasonDescription": "Command executed successfully",
                    },
                    "result": {
                        "message": {"s": "Command processed by Thing1"},
                        "timestamp": {"s": str(int(time.time()))},
                    },
                }
            ),
            qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        )
        logger.info("Status: SUCCEEDED")

    return _on_command_received


def main():
    # Configuration
    mqtt3.CLIENT_ID = "claim-device"
    mqtt3.PATH_TO_CERT = "certificates/claim.cert.pem"
    mqtt3.PATH_TO_KEY = "certificates/claim.private.key"
    mqtt3.PATH_TO_ROOT = "certificates/AmazonRootCA1.pem"

    mqtt_connection = mqtt3.get_connection()

    logger.debug(f"Subscribing to topic '{COMMAND_REQUEST_TOPIC}'...")

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=COMMAND_REQUEST_TOPIC,
        qos=awscrt.mqtt.QoS.AT_LEAST_ONCE,
        callback=on_command_received(mqtt_connection),
    )
    subscribe_result = subscribe_future.result()
    logger.debug(
        f"Subscribed with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}"
    )

    logger.info(f"Device {THING_NAME} is ready to receive commands...")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nDisconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()


if __name__ == "__main__":
    main()
