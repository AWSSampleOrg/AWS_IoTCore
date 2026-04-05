#!/usr/bin/env python3
import boto3
import json
import time

# Configuration
THING_NAME = "Thing1"

# Get IoT endpoint
iot_jobs = boto3.client("iot-jobs-data")

# Get pending jobs
jobs = iot_jobs.get_pending_job_executions(thingName=THING_NAME)
print(
    f"Pending jobs: {len(jobs.get('inProgressJobs', []) + jobs.get('queuedJobs', []))}"
)

for job in jobs.get("queuedJobs", []):
    job_id = job["jobId"]

    # Describe job execution
    execution = iot_jobs.describe_job_execution(jobId=job_id, thingName=THING_NAME)
    job_doc = json.loads(execution["execution"]["jobDocument"])

    print(f"\nJob ID: {job_id}")
    print(f"Operation: {job_doc.get('operation')}")
    print(f"Version: {job_doc.get('version')}")

    # Update to IN_PROGRESS
    iot_jobs.update_job_execution(
        jobId=job_id, thingName=THING_NAME, status="IN_PROGRESS"
    )
    print("Status: IN_PROGRESS")

    # Simulate work
    time.sleep(2)

    # Update to SUCCEEDED
    iot_jobs.update_job_execution(
        jobId=job_id, thingName=THING_NAME, status="SUCCEEDED"
    )
    print("Status: SUCCEEDED")
