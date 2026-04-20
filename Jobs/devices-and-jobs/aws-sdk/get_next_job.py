"""
Workflow 1: Get the next job — boto3 version  (jobs-workflow-device-online.html)

Uses iot-jobs-data HTTP API instead of MQTT.
No notifications available over HTTP — polls via start_next_pending_job_execution.
Equivalent to workflow_1_get_next_job.py.
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

    # Report progress (optional)
    update(job_id, "IN_PROGRESS", version, {"progress": "50%"})
    version += 1

    time.sleep(1)

    # Report completion
    update(job_id, "SUCCEEDED", version, {"progress": "100%"})


def main():
    print(f"Workflow 1 (boto3) started for thing: {THING_NAME}")
    try:
        while True:
            # StartNextPendingJobExecution — atomically get and start the next job
            resp = iot_jobs.start_next_pending_job_execution(thingName=THING_NAME)
            execution = resp.get("execution")
            if execution:
                execute_job(execution)
            else:
                print("No pending jobs, polling again in 10s...")
                time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped")


if __name__ == "__main__":
    main()
