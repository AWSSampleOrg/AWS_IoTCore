"""
Workflow 2: Select from available jobs  (jobs-workflow-device-online.html)

Steps:

Subscribe to notify
Call GetPendingJobExecutions to get the list of pending jobs
Select a job from the list
Call DescribeJobExecution to get the job document and statusDetails
Call UpdateJobExecution(IN_PROGRESS) to start the job
Perform the actions specified by the job document; report progress via UpdateJobExecution
Call UpdateJobExecution(SUCCEEDED/FAILED) when done
  notify fires when a new pending job becomes available → loop back to step 2
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


def _publish(conn: awscrt.mqtt.Connection, topic, payload):
    conn.publish(
        topic=topic, payload=json.dumps(payload), qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
    )


def _get_pending(conn: awscrt.mqtt.Connection):
    """Step 2: GetPendingJobExecutions — list all pending jobs."""
    _publish(conn, f"$aws/things/{THING_NAME}/jobs/get", {})
    logger.debug("Published jobs/get")


def _describe_job(conn, job_id):
    """Step 4: DescribeJobExecution — get job document and statusDetails."""
    _publish(
        conn,
        f"$aws/things/{THING_NAME}/jobs/{job_id}/get",
        {"includeJobDocument": True, "clientToken": str(uuid.uuid4())},
    )
    logger.debug(f"Published jobs/{job_id}/get")


def _update(conn: awscrt.mqtt.Connection, job_id, status, version, status_details=None):
    """Steps 5/6/7: UpdateJobExecution — mark IN_PROGRESS, report progress, or complete."""
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
    """Perform the actions specified by the job document (steps 5–7)."""
    job_id = execution["jobId"]
    job_doc = execution.get("jobDocument", {})
    version = execution.get("versionNumber", 1)
    operation = job_doc.get("operation", "unknown")
    logger.info(f"Executing jobId={job_id} operation={operation}")

    # Step 5: Mark IN_PROGRESS
    _update(conn, job_id, "IN_PROGRESS", version, {"progress": "0%"})
    version += 1

    # Step 6: Report progress (optional)
    time.sleep(1)
    _update(conn, job_id, "IN_PROGRESS", version, {"progress": "50%"})
    version += 1

    # Step 7: Report completion
    time.sleep(1)
    _update(conn, job_id, "SUCCEEDED", version, {"progress": "100%"})


# --- Callbacks ---


def on_get_accepted(conn: awscrt.mqtt.Connection):
    """
    jobs/get/accepted: contains inProgressJobs and queuedJobs lists.
    Step 3: select a job; step 4: describe it.
    """

    def _cb(topic: str, payload, **kwargs):
        data = json.loads(payload)
        queued = data.get("queuedJobs", [])
        in_progress = data.get("inProgressJobs", [])
        all_pending = in_progress + queued
        if not all_pending:
            logger.info("get/accepted: no pending jobs")
            return
        logger.info(
            f"get/accepted: {len(in_progress)} IN_PROGRESS, {len(queued)} QUEUED"
        )
        # Step 3: select first job (device can apply its own selection logic here)
        selected = all_pending[0]
        logger.info(f"Selected jobId={selected['jobId']}")
        # Step 4: describe to get full job document
        _describe_job(conn, selected["jobId"])

    return _cb


def on_get_rejected(topic: str, payload, **kwargs):
    err = json.loads(payload)
    logger.error(f"get/rejected {err.get('code')}: {err.get('message')}")


def on_job_get_accepted(conn: awscrt.mqtt.Connection):
    """jobs/{jobId}/get/accepted: full execution including jobDocument."""

    def _cb(topic: str, payload, **kwargs):
        execution = json.loads(payload).get("execution", {})
        if not execution:
            logger.info("jobId/get/accepted: no execution")
            return
        logger.info(
            f"jobId/get/accepted jobId={execution['jobId']} status={execution.get('status')}"
        )
        execute_job(conn, execution)

    return _cb


def on_job_get_rejected(topic: str, payload, **kwargs):
    err = json.loads(payload)
    logger.error(f"jobId/get/rejected {err.get('code')}: {err.get('message')}")


def on_update_accepted(topic: str, payload, **kwargs):
    logger.info(f"update/accepted clientToken={json.loads(payload).get('clientToken')}")


def on_update_rejected(topic: str, payload, **kwargs):
    err = json.loads(payload)
    logger.error(f"update/rejected {err.get('code')}: {err.get('message')}")


def on_notify(conn: awscrt.mqtt.Connection):
    """
    notify fires when a job is added to or removed from the pending list
    (ListNotification — up to 15 summaries, IN_PROGRESS first then QUEUED).
    Loop trigger: re-query the full list via GetPendingJobExecutions.
    """

    def _cb(topic: str, payload, **kwargs):
        jobs = json.loads(payload).get("jobs", {})
        in_progress = jobs.get("IN_PROGRESS", [])
        queued = jobs.get("QUEUED", [])
        logger.info(f"notify: {len(in_progress)} IN_PROGRESS, {len(queued)} QUEUED")
        if in_progress or queued:
            _get_pending(conn)

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

    # Step 1: Subscribe to notify and all response topics
    for topic, cb in [
        (f"$aws/things/{THING_NAME}/jobs/notify", on_notify(conn)),
        (f"$aws/things/{THING_NAME}/jobs/get/accepted", on_get_accepted(conn)),
        (f"$aws/things/{THING_NAME}/jobs/get/rejected", on_get_rejected),
        (f"$aws/things/{THING_NAME}/jobs/+/get/accepted", on_job_get_accepted(conn)),
        (f"$aws/things/{THING_NAME}/jobs/+/get/rejected", on_job_get_rejected),
        (f"$aws/things/{THING_NAME}/jobs/+/update/accepted", on_update_accepted),
        (f"$aws/things/{THING_NAME}/jobs/+/update/rejected", on_update_rejected),
    ]:
        conn.subscribe(topic=topic, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE, callback=cb)[
            0
        ].result()
        logger.debug(f"Subscribed: {topic}")

    # Step 2: Query pending jobs on boot
    _get_pending(conn)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Disconnecting...")
        conn.disconnect().result()


if __name__ == "__main__":
    main()
