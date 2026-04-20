# Devices and Jobs

Based on [Devices and Jobs](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-devices.html).

## Files

| File                               | Description                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| `mqtt/get_next_job.py`             | Workflow 1: Get the next job — raw MQTT                      |
| `job-sdk/get_next_job.py`          | Workflow 1: Get the next job — `IotJobsClient` SDK           |
| `aws-sdk/get_next_job.py`          | Workflow 1: Get the next job — boto3 HTTP                    |
| `mqtt/select_from_available.py`    | Workflow 2: Select from available jobs — raw MQTT            |
| `job-sdk/select_from_available.py` | Workflow 2: Select from available jobs — `IotJobsClient` SDK |
| `aws-sdk/select_from_available.py` | Workflow 2: Select from available jobs — boto3 HTTP          |

## Workflow 1: Get the Next Job

Reference: [Device workflow — Get the next job](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-workflow-device-online.html)

The device subscribes to `notify-next` and uses `StartNextPendingJobExecution` to atomically
get and start the next pending job. When a job completes, `notify-next` fires and the device
loops back to request the next one.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 1. SUB: jobs/notify-next                   |
  |    SUB: jobs/start-next/accepted           |
  |    SUB: jobs/start-next/rejected           |
  |    SUB: jobs/+/update/accepted             |
  |    SUB: jobs/+/update/rejected             |
  |------------------------------------------->|
  |                                            |
  | 2. PUB: jobs/start-next                    |  ← StartNextPendingJobExecution
  |------------------------------------------->|    (DescribeJobExecution($next) +
  |                                            |     UpdateJobExecution(IN_PROGRESS))
  | RCV: jobs/start-next/accepted              |
  |<-------------------------------------------|
  | execution.status = IN_PROGRESS             |
  | execution.jobDocument = {...}              |
  |                                            |
  | 3-5. [Execute job, report progress]        |
  |                                            |
  | 6. PUB: jobs/{jobId}/update                |  ← UpdateJobExecution
  |    {"status":"IN_PROGRESS",                |
  |     "statusDetails":{"progress":"50%"},    |
  |     "expectedVersion": N}                  |
  |------------------------------------------->|
  |                                            |
  | 7. PUB: jobs/{jobId}/update                |  ← UpdateJobExecution (terminal)
  |    {"status":"SUCCEEDED",                  |
  |     "expectedVersion": N+1}                |
  |------------------------------------------->|
  |                                            |
  | 8. RCV: jobs/notify-next                   |  ← next job changed → loop to step 2
  |<-------------------------------------------|
  |                                            |
```

Key points:

`StartNextPendingJobExecution` is atomic: it both describes `$next` and sets it to `IN_PROGRESS`.
The job is already `IN_PROGRESS` when `start-next/accepted` arrives — no separate IN_PROGRESS update needed before executing.
`notify-next` fires only when the **first** job in the queue changes (not on every status change).
Use `expectedVersion` for optimistic locking; it increments with each successful `UpdateJobExecution`.

## Workflow 2: Select from Available Jobs

Reference: [Device workflow — Select from available jobs](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-workflow-device-online.html)

The device subscribes to `notify`, queries the full pending list, selects a job, describes it
to get the job document, then executes it. `notify` fires whenever the pending list changes.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 1. SUB: jobs/notify                        |
  |    SUB: jobs/get/accepted                  |
  |    SUB: jobs/get/rejected                  |
  |    SUB: jobs/+/get/accepted                |
  |    SUB: jobs/+/get/rejected                |
  |    SUB: jobs/+/update/accepted             |
  |    SUB: jobs/+/update/rejected             |
  |------------------------------------------->|
  |                                            |
  | 2. PUB: jobs/get                           |  ← GetPendingJobExecutions
  |------------------------------------------->|
  |                                            |
  | RCV: jobs/get/accepted                     |
  |<-------------------------------------------|
  | {"inProgressJobs":[...],"queuedJobs":[...]}|
  |                                            |
  | 3. [Select a job from the list]            |
  |                                            |
  | 4. PUB: jobs/{jobId}/get                   |  ← DescribeJobExecution
  |------------------------------------------->|
  |                                            |
  | RCV: jobs/{jobId}/get/accepted             |
  |<-------------------------------------------|
  | execution.jobDocument = {...}              |
  |                                            |
  | 5. PUB: jobs/{jobId}/update                |  ← UpdateJobExecution(IN_PROGRESS)
  |    {"status":"IN_PROGRESS",                |
  |     "expectedVersion": N}                  |
  |------------------------------------------->|
  |                                            |
  | 6-7. [Execute job, report progress]        |
  |                                            |
  | PUB: jobs/{jobId}/update                   |  ← UpdateJobExecution (progress)
  |    {"status":"IN_PROGRESS",                |
  |     "statusDetails":{"progress":"50%"},    |
  |     "expectedVersion": N+1}                |
  |------------------------------------------->|
  |                                            |
  | PUB: jobs/{jobId}/update                   |  ← UpdateJobExecution (terminal)
  |    {"status":"SUCCEEDED",                  |
  |     "expectedVersion": N+2}                |
  |------------------------------------------->|
  |                                            |
  | RCV: jobs/notify                           |  ← pending list changed → loop to step 2
  |<-------------------------------------------|
  |                                            |
```

Key points:

`notify` (ListNotification) contains up to 15 pending job summaries — `IN_PROGRESS` first, then `QUEUED`. It does **not** include the job document.
`notify` fires when a job is added to or removed from the pending list. It does **not** fire when a job transitions `QUEUED → IN_PROGRESS` (the job is still pending).
The device selects which job to run (step 3) — it can apply its own priority logic.
`DescribeJobExecution` (step 4) returns the full job document and any saved `statusDetails`.

## Jobs Notifications

Reference: [Jobs notifications](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-comm-notifications.html)

| Topic              | Type             | Fires when                                         |
| ------------------ | ---------------- | -------------------------------------------------- |
| `jobs/notify`      | ListNotification | A job is added to or removed from the pending list |
| `jobs/notify-next` | NextNotification | The **first** job in the queue changes             |

**notify payload** (`$aws/things/thingName/jobs/notify`):

```json
{
  "timestamp": 1517016948,
  "jobs": {
    "IN_PROGRESS": [
      {
        "jobId": "job1",
        "queuedAt": 1517016947,
        "lastUpdatedAt": 1517017472,
        "versionNumber": 2
      }
    ],
    "QUEUED": [
      {
        "jobId": "job2",
        "queuedAt": 1517017191,
        "lastUpdatedAt": 1517017191,
        "versionNumber": 1
      }
    ]
  }
}
```

**notify-next payload** (`$aws/things/thingName/jobs/notify-next`):

```json
{
  "timestamp": 1517016948,
  "execution": {
    "jobId": "job1",
    "status": "QUEUED",
    "queuedAt": 1517016947,
    "lastUpdatedAt": 1517016947,
    "versionNumber": 1,
    "executionNumber": 1,
    "jobDocument": { "operation": "test" }
  }
}
```

**Notification scenario** (from [AWS docs](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-comm-notifications.html)):

| Event                       | notify                 | notify-next                 |
| --------------------------- | ---------------------- | --------------------------- |
| `job1` created              | ✓ fires                | ✓ fires (job1 is now first) |
| `job2` created              | ✓ fires                | ✗ (job1 still first)        |
| `job1` → IN_PROGRESS        | ✗ (list unchanged)     | ✗ (job1 still first)        |
| `job3` created              | ✓ fires                | ✗ (job1 still first)        |
| `job1` → SUCCEEDED          | ✓ fires (job1 removed) | ✓ fires (job2 is now first) |
| `job3` forced → IN_PROGRESS | ✗                      | ✓ fires (job3 is now first) |
| `job2` → REJECTED           | ✓ fires (job2 removed) | ✗ (job3 still first)        |
| `job3` force-deleted        | ✓ fires                | ✓ fires (queue empty)       |
