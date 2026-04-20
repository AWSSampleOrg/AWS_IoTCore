"""
Workflow 1: Get the next job — SDK version  (jobs-workflow-device-online.html)

Uses iotjobs.IotJobsClient instead of raw MQTT topics.
Equivalent to workflow_1_get_next_job.py.
"""

import time
import uuid
from awscrt import mqtt
from awsiot import iotjobs
import mqtt3

THING_NAME = "IoTCoreJobThing"


def start_next(jobs_client: iotjobs.IotJobsClient):
    """StartNextPendingJobExecution — atomically get and start the next job."""
    jobs_client.publish_start_next_pending_job_execution(
        iotjobs.StartNextPendingJobExecutionRequest(
            thing_name=THING_NAME,
            client_token=str(uuid.uuid4()),
        ),
        mqtt.QoS.AT_LEAST_ONCE,
    ).result()


def update(
    jobs_client: iotjobs.IotJobsClient,
    job_id: str,
    status: iotjobs.JobStatus,
    version: int,
    status_details: dict = None,
):
    """UpdateJobExecution — report progress or terminal status."""
    jobs_client.publish_update_job_execution(
        iotjobs.UpdateJobExecutionRequest(
            thing_name=THING_NAME,
            job_id=job_id,
            status=status,
            expected_version=version,
            client_token=str(uuid.uuid4()),
            status_details=status_details,
        ),
        mqtt.QoS.AT_LEAST_ONCE,
    ).result()
    print(f"UpdateJobExecution jobId={job_id} status={status}")


def execute_job(jobs_client: iotjobs.IotJobsClient, execution: iotjobs.JobExecution):
    job_id = execution.job_id
    job_doc = execution.job_document or {}
    version = execution.version_number or 1
    operation = job_doc.get("operation", "unknown")
    print(f"Executing jobId={job_id} operation={operation}")

    # Report progress (optional)
    update(
        jobs_client, job_id, iotjobs.JobStatus.IN_PROGRESS, version, {"progress": "50%"}
    )
    version += 1

    time.sleep(1)

    # Report completion
    update(
        jobs_client, job_id, iotjobs.JobStatus.SUCCEEDED, version, {"progress": "100%"}
    )


def main():
    conn = mqtt3.get_connection()
    jobs_client = iotjobs.IotJobsClient(conn)

    # Step 1: Subscribe to notify-next and all response topics
    # $aws/things/{thingName}/jobs/notify-next
    jobs_client.subscribe_to_next_job_execution_changed_events(
        iotjobs.NextJobExecutionChangedSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda event: (
            start_next(jobs_client)
            if event.execution
            else print("notify-next: no more pending jobs")
        ),
    )[0].result()

    # $aws/things/{thingName}/jobs/start-next/accepted
    jobs_client.subscribe_to_start_next_pending_job_execution_accepted(
        iotjobs.StartNextPendingJobExecutionSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda resp: (
            execute_job(jobs_client, resp.execution)
            if resp.execution
            else print("start-next/accepted: no pending jobs")
        ),
    )[0].result()

    # $aws/things/{thingName}/jobs/start-next/rejected
    jobs_client.subscribe_to_start_next_pending_job_execution_rejected(
        iotjobs.StartNextPendingJobExecutionSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda err: print(f"start-next/rejected {err.code}: {err.message}"),
    )[0].result()

    # $aws/things/{thingName}/jobs/+/update/accepted
    jobs_client.subscribe_to_update_job_execution_accepted(
        iotjobs.UpdateJobExecutionSubscriptionRequest(
            thing_name=THING_NAME, job_id="+"
        ),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda resp: print(f"update/accepted clientToken={resp.client_token}"),
    )[0].result()

    # $aws/things/{thingName}/jobs/+/update/rejected
    jobs_client.subscribe_to_update_job_execution_rejected(
        iotjobs.UpdateJobExecutionSubscriptionRequest(
            thing_name=THING_NAME, job_id="+"
        ),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda err: print(f"update/rejected {err.code}: {err.message}"),
    )[0].result()

    # Step 2: Kick off — get and start the next pending job
    start_next(jobs_client)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        conn.disconnect().result()


if __name__ == "__main__":
    main()
