"""
Workflow 2: Select from available jobs — SDK version  (jobs-workflow-device-online.html)

Uses iotjobs.IotJobsClient instead of raw MQTT topics.
Equivalent to workflow_2_select_from_available.py.
"""

import time
import uuid
from awscrt import mqtt
from awsiot import iotjobs
import mqtt3

THING_NAME = "IoTCoreJobThing"


def get_pending(jobs_client: iotjobs.IotJobsClient):
    """GetPendingJobExecutions — list all pending jobs."""
    jobs_client.publish_get_pending_job_executions(
        iotjobs.GetPendingJobExecutionsRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
    ).result()


def describe_job(jobs_client: iotjobs.IotJobsClient, job_id: str):
    """DescribeJobExecution — get job document and statusDetails."""
    jobs_client.publish_describe_job_execution(
        iotjobs.DescribeJobExecutionRequest(
            thing_name=THING_NAME,
            job_id=job_id,
            include_job_document=True,
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


def execute_job(
    jobs_client: iotjobs.IotJobsClient, execution: iotjobs.JobExecutionData
):
    job_id = execution.job_id
    job_doc = execution.job_document or {}
    version = execution.version_number or 1
    operation = job_doc.get("operation", "unknown")
    print(f"Executing jobId={job_id} operation={operation}")

    # Step 5: Mark IN_PROGRESS
    update(
        jobs_client, job_id, iotjobs.JobStatus.IN_PROGRESS, version, {"progress": "0%"}
    )
    version += 1

    # Step 6: Report progress (optional)
    time.sleep(1)
    update(
        jobs_client, job_id, iotjobs.JobStatus.IN_PROGRESS, version, {"progress": "50%"}
    )
    version += 1

    # Step 7: Report completion
    time.sleep(1)
    update(
        jobs_client, job_id, iotjobs.JobStatus.SUCCEEDED, version, {"progress": "100%"}
    )


def main():
    conn = mqtt3.get_connection()
    jobs_client = iotjobs.IotJobsClient(conn)

    # Step 1: Subscribe to notify and all response topics

    # $aws/things/{thingName}/jobs/notify
    jobs_client.subscribe_to_job_executions_changed_events(
        iotjobs.JobExecutionsChangedSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda event: get_pending(jobs_client) if event.jobs else None,
    )[0].result()

    # $aws/things/{thingName}/jobs/get/accepted
    def on_get_accepted(resp: iotjobs.GetPendingJobExecutionsResponse):
        all_pending = (resp.in_progress_jobs or []) + (resp.queued_jobs or [])
        if not all_pending:
            print("get/accepted: no pending jobs")
            return
        print(
            f"get/accepted: {len(resp.in_progress_jobs or [])} IN_PROGRESS, {len(resp.queued_jobs or [])} QUEUED"
        )
        # Step 3: select first job
        describe_job(jobs_client, all_pending[0].job_id)

    jobs_client.subscribe_to_get_pending_job_executions_accepted(
        iotjobs.GetPendingJobExecutionsSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=on_get_accepted,
    )[0].result()

    # $aws/things/{thingName}/jobs/get/rejected
    jobs_client.subscribe_to_get_pending_job_executions_rejected(
        iotjobs.GetPendingJobExecutionsSubscriptionRequest(thing_name=THING_NAME),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda err: print(f"get/rejected {err.code}: {err.message}"),
    )[0].result()

    # $aws/things/{thingName}/jobs/{jobId}/get/accepted
    jobs_client.subscribe_to_describe_job_execution_accepted(
        iotjobs.DescribeJobExecutionSubscriptionRequest(
            thing_name=THING_NAME, job_id="+"
        ),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda resp: (
            execute_job(jobs_client, resp.execution) if resp.execution else None
        ),
    )[0].result()

    # $aws/things/{thingName}/jobs/{jobId}/get/rejected
    jobs_client.subscribe_to_describe_job_execution_rejected(
        iotjobs.DescribeJobExecutionSubscriptionRequest(
            thing_name=THING_NAME, job_id="+"
        ),
        mqtt.QoS.AT_LEAST_ONCE,
        callback=lambda err: print(f"jobId/get/rejected {err.code}: {err.message}"),
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

    # Step 2: Query pending jobs on boot
    get_pending(jobs_client)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnecting...")
        conn.disconnect().result()


if __name__ == "__main__":
    main()
