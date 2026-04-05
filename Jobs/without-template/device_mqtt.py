from logging import getLogger, StreamHandler, DEBUG
import os
import json
import time
import boto3
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# logger setting
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

# Configuration
iot_client = boto3.client("iot")
ENDPOINT = iot_client.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]

THING_NAME = "Thing1"
PATH_TO_CERT = os.path.join(
    os.path.dirname(__file__), "certificates/device_cert_filename.pem"
)
PATH_TO_KEY = os.path.join(
    os.path.dirname(__file__), "certificates/device_cert_key_filename.key"
)
PATH_TO_ROOT = os.path.join(os.path.dirname(__file__), "certificates/AmazonRootCA1.pem")

# Job topics
NOTIFY_NEXT_TOPIC = f"$aws/things/{THING_NAME}/jobs/notify-next"
START_NEXT_TOPIC = f"$aws/things/{THING_NAME}/jobs/start-next"


def on_job_received(mqtt_connection: mqtt.Connection):
    def _on_job_received(topic, payload, **kwargs):
        logger.debug("------------------------on_job_received------------------------")
        job = json.loads(payload)
        logger.info(job)
        execution = job.get("execution", {})
        if not execution:
            logger.info("No pending jobs")
            return
        job_id = execution["jobId"]
        job_doc = execution["jobDocument"]
        logger.debug("------------------------jobDocument------------------------")
        logger.info(job_doc)

        # Update to IN_PROGRESS
        update_topic = f"$aws/things/{THING_NAME}/jobs/{job_id}/update"
        mqtt_connection.publish(
            topic=update_topic,
            payload=json.dumps({"status": "IN_PROGRESS"}),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        logger.info("Status: IN_PROGRESS")

        # Update to SUCCEEDED
        mqtt_connection.publish(
            topic=update_topic,
            payload=json.dumps({"status": "SUCCEEDED"}),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        logger.info("Status: SUCCEEDED")

    return _on_job_received


def get_connection() -> mqtt.Connection:
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=PATH_TO_CERT,
        pri_key_filepath=PATH_TO_KEY,
        client_bootstrap=client_bootstrap,
        ca_filepath=PATH_TO_ROOT,
        client_id=THING_NAME,
        clean_session=False,
        keep_alive_secs=6,
    )
    logger.debug(f"Connecting to {ENDPOINT} with client ID '{THING_NAME}'...")
    connect_future = mqtt_connection.connect()
    connect_future.result()

    return mqtt_connection


def main():
    mqtt_connection = get_connection()

    logger.debug(f"Subscribing to topic '{NOTIFY_NEXT_TOPIC}'...")

    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=NOTIFY_NEXT_TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_job_received(mqtt_connection),
    )
    subscribe_result = subscribe_future.result()
    logger.debug(
        f"Subscribed with qos: {str(subscribe_result['qos'])}, packet_id: {packet_id}"
    )

    # Request next job
    mqtt_connection.publish(
        topic=START_NEXT_TOPIC, payload=json.dumps({}), qos=mqtt.QoS.AT_LEAST_ONCE
    )
    logger.debug("Requested next job\n")

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
