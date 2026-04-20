"""
Workflow 2: Select from available jobs — boto3 version  (jobs-workflow-device-online.html)

Uses iot-jobs-data HTTP API instead of MQTT.
No notifications available over HTTP — polls via get_pending_job_executions.
Equivalent to workflow_2_select_from_available.py.
"""

import time
import boto3

THING_NAME = "IoTCoreJobThing"

iot_jobs = boto3.client("iot-jobs-data")


def update(job_id, status, version, status_details=None):
    """UpdateJobExecution — report progress or terminal status."""
    params = {
        "jobId": job_id,
        "thingName": THING_NAME,
        "status": status,
        "expectedVersion": version,
    }
    if status_details:
        params["statusDetails"] = status_details
    iot_jobs.update_job_execution(**params)
    print(f"UpdateJobExecution jobId={job_id} status={status}")


def execute_job(execution):
    job_id = execution["jobId"]
    job_doc = execution.get("jobDocument", {})
    version = execution.get("versionNumber", 1)
    operation = job_doc.get("operation", "unknown")
    print(f"Executing jobId={job_id} operation={operation}")

    # Step 5: Mark IN_PROGRESS
    update(job_id, "IN_PROGRESS", version, {"progress": "0%"})
    version += 1

    # Step 6: Report progress (optional)
    time.sleep(1)
    update(job_id, "IN_PROGRESS", version, {"progress": "50%"})
    version += 1

    # Step 7: Report completion
    time.sleep(1)
    update(job_id, "SUCCEEDED", version, {"progress": "100%"})


def main():
    print(f"Workflow 2 (boto3) started for thing: {THING_NAME}")
    try:
        while True:
            # Step 2: GetPendingJobExecutions
            resp = iot_jobs.get_pending_job_executions(thingName=THING_NAME)
            in_progress = resp.get("inProgressJobs", [])
            queued = resp.get("queuedJobs", [])
            all_pending = in_progress + queued

            if not all_pending:
                print("No pending jobs, polling again in 10s...")
                time.sleep(10)
                continue

            print(f"Pending: {len(in_progress)} IN_PROGRESS, {len(queued)} QUEUED")

            # Step 3: Select a job (first in list)
            selected_id = all_pending[0]["jobId"]

            # Step 4: DescribeJobExecution — get full job document
            desc = iot_jobs.describe_job_execution(
                jobId=selected_id, thingName=THING_NAME
            )
            execution = desc.get("execution")
            if execution:
                execute_job(execution)

    except KeyboardInterrupt:
        print("Stopped")


if __name__ == "__main__":
    main()
