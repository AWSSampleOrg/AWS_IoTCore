"""
Workflow 1: Get the next job  (jobs-workflow-device-online.html)

Steps:

Subscribe to notify-next
Call StartNextPendingJobExecution (combines DescribeJobExecution($next) +
     UpdateJobExecution(IN_PROGRESS) in one atomic call)

Receive job via start-next/accepted → execute → UpdateJobExecution(SUCCEEDED/FAILED)
notify-next fires when the next job changes → loop back to step 2
"""

from logging import getLogger, StreamHandler, DEBUG
import os
import json
import time
import uuid
import awscrt
import mqtt3

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(os.getenv("LOG_LEVEL", DEBUG))
logger.addHandler(handler)
logger.propagate = False

THING_NAME = "IoTCoreJobThing"


def _publish(conn: awscrt.mqtt.Connection, topic: str, payload):
    conn.publish(
        topic=topic, payload=json.dumps(payload), qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
    )


def _start_next(conn: awscrt.mqtt.Connection):
    """Step 2: StartNextPendingJobExecution — atomically get and start the next job."""
    _publish(
        conn,
        f"$aws/things/{THING_NAME}/jobs/start-next",
        {"clientToken": str(uuid.uuid4())},
    )
    logger.debug("Published start-next")


def _update(
    conn: awscrt.mqtt.Connection, job_id: str, status, version, status_details=None
):
    """Step 3/7: UpdateJobExecution — report progress or terminal status."""
    payload = {
        "status": status,
        "expectedVersion": version,
        "clientToken": str(uuid.uuid4()),
    }
    if status_details:
        payload["statusDetails"] = status_details
    _publish(conn, f"$aws/things/{THING_NAME}/jobs/{job_id}/update", payload)
    logger.info(f"UpdateJobExecution jobId={job_id} status={status}")


def execute_job(conn: awscrt.mqtt.Connection, execution):
    """Perform the actions specified by the job document (step 5)."""
    job_id = execution["jobId"]
    job_doc = execution.get("jobDocument", {})
    version = execution.get("versionNumber", 1)
    operation = job_doc.get("operation", "unknown")
    logger.info(f"Executing jobId={job_id} operation={operation}")

    # Report progress (optional — step 5)
    _update(conn, job_id, "IN_PROGRESS", version, {"progress": "50%"})
    version += 1

    # Simulate work
    time.sleep(1)

    # Report completion (step 7)
    _update(conn, job_id, "SUCCEEDED", version, {"progress": "100%"})


# --- Callbacks ---


def on_start_next_accepted(conn: awscrt.mqtt.Connection):
    """start-next/accepted: job is already IN_PROGRESS, contains jobDocument."""

    def _cb(topic: str, payload, **kwargs):
        execution = json.loads(payload).get("execution")
        if not execution:
            logger.info("No pending jobs")
            return
        logger.info(
            f"start-next/accepted jobId={execution['jobId']} versionNumber={execution.get('versionNumber')}"
        )
        execute_job(conn, execution)

    return _cb


def on_start_next_rejected(topic: str, payload, **kwargs):
    err = json.loads(payload)
    logger.error(f"start-next/rejected {err.get('code')}: {err.get('message')}")


def on_update_accepted(topic: str, payload, **kwargs):
    logger.info(f"update/accepted clientToken={json.loads(payload).get('clientToken')}")


def on_update_rejected(topic: str, payload, **kwargs):
    err = json.loads(payload)
    logger.error(f"update/rejected {err.get('code')}: {err.get('message')}")


def on_notify_next(conn: awscrt.mqtt.Connection):
    """
    notify-next fires when the first job in the queue changes (step 8 / loop trigger).
    Does NOT fire when a job transitions QUEUED→IN_PROGRESS while remaining first.
    """

    def _cb(topic: str, payload, **kwargs):
        data = json.loads(payload)
        if data.get("execution"):
            logger.debug("notify-next: next job changed → requesting start-next")
            _start_next(conn)
        else:
            logger.info("notify-next: no more pending jobs")

    return _cb


def main():
    mqtt3.PATH_TO_CERT = os.path.join(
        os.path.dirname(__file__), "certificates/device_cert_filename.pem"
    )
    mqtt3.PATH_TO_KEY = os.path.join(
        os.path.dirname(__file__), "certificates/device_cert_key_filename.key"
    )
    mqtt3.PATH_TO_ROOT = os.path.join(
        os.path.dirname(__file__), "certificates/AmazonRootCA1.pem"
    )

    conn = mqtt3.get_connection()

    # Step 1: Subscribe to notify-next and all response topics
    for topic, cb in [
        (f"$aws/things/{THING_NAME}/jobs/notify-next", on_notify_next(conn)),
        (
            f"$aws/things/{THING_NAME}/jobs/start-next/accepted",
            on_start_next_accepted(conn),
        ),
        (f"$aws/things/{THING_NAME}/jobs/start-next/rejected", on_start_next_rejected),
        (f"$aws/things/{THING_NAME}/jobs/+/update/accepted", on_update_accepted),
        (f"$aws/things/{THING_NAME}/jobs/+/update/rejected", on_update_rejected),
    ]:
        conn.subscribe(topic=topic, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE, callback=cb)[
            0
        ].result()
        logger.debug(f"Subscribed: {topic}")

    # Step 2: Kick off — get and start the next pending job
    _start_next(conn)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Disconnecting...")
        conn.disconnect().result()


if __name__ == "__main__":
    main()
