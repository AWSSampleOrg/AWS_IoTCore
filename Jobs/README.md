# AWS IoT Jobs

Based on [AWS IoT Jobs documentation](https://docs.aws.amazon.com/iot/latest/developerguide/iot-jobs.html).

## Structure

```
Jobs/
├── managing-jobs/        → create-manage-jobs.html
├── job-configurations/   → jobs-configurations.html
├── devices-and-jobs/     → jobs-devices.html
├── api-operations/       → jobs-api.html
└── security/             → iot-jobs-security.html
```

## Device Workflows

There are two phases in the Jobs MQTT flow: **Job Retrieval** and **Job Execution**.
Job retrieval can be either passive (subscribe and wait) or active (publish to query).

### Phase 1: Job Retrieval

#### 1-1. Passive Retrieval (Subscribe and Wait)

The device subscribes to notification topics and waits for jobs to arrive.
This is the normal steady-state behavior when the device is online.

```
Device                                    AWS IoT Jobs          Cloud (Console/CLI)
  |                                            |                       |
  | 1. SUB: $aws/things/{thingName}/           |                       |
  |         jobs/notify                        |                       |
  |------------------------------------------->|                       |
  |                                            |                       |
  | 2. SUB: $aws/things/{thingName}/           |                       |
  |         jobs/notify-next                   |                       |
  |------------------------------------------->|                       |
  |                                            |                       |
  |    (device is now waiting for jobs)        |                       |
  |                                            |                       |
  |                                            |    CreateJob(iot-job01)|
  |                                            |<----------------------|
  |                                            |                       |
  | 3. RCV on /jobs/notify:                    |                       |
  |    {"jobs":{"QUEUED":[{"jobId":            |                       |
  |     "iot-job01",...}]}}                     |                       |
  |<-------------------------------------------|                       |
  |                                            |                       |
  | 4. RCV on /jobs/notify-next:               |                       |
  |    {"execution":{"jobId":"iot-job01",      |                       |
  |     "status":"QUEUED",                     |                       |
  |     "jobDocument":{...}}}                  |                       |
  |<-------------------------------------------|                       |
  |                                            |                       |
```

Key behaviors of the two notification topics:

- **`/jobs/notify`** (ListNotification) — Publishes whenever a job is added to or removed from the pending list. Contains up to 15 pending job summaries (IN_PROGRESS first, then QUEUED). Does NOT include the jobDocument. Does NOT fire when a job simply moves from QUEUED → IN_PROGRESS (it's still pending).
- **`/jobs/notify-next`** (NextNotification) — Publishes only when the "first" (next-to-execute) job in the list changes. Includes the full jobDocument. Does NOT fire when additional jobs are added behind the current first job.

Example: If `iot-job01` is already QUEUED and you create `iot-job02`:

- `/jobs/notify` fires (now lists both jobs)
- `/jobs/notify-next` does NOT fire (the next job is still `iot-job01`)

Example: When `iot-job01` transitions from QUEUED → IN_PROGRESS:

- Neither `/jobs/notify` nor `/jobs/notify-next` fires (the pending list is unchanged, and `iot-job01` is still the first job)

#### 1-2. Active Retrieval (Query on Boot)

When a device comes online after being offline (missed notifications), it actively queries for pending jobs using `DescribeJobExecution` with `$next`.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 1. SUB: $aws/things/{thingName}/           |
  |         jobs/+/get/accepted                |
  |------------------------------------------->|
  |                                            |
  | 2. SUB: $aws/things/{thingName}/           |
  |         jobs/+/get/rejected                |
  |------------------------------------------->|
  |                                            |
  | 3. PUB: $aws/things/{thingName}/           |
  |         jobs/$next/get                     |
  |    payload: {}                             |
  |------------------------------------------->|
  |                                            |
  | 4. RCV on /jobs/$next/get/accepted:        |
  |    {"execution":{"jobId":"iot-job01",      |
  |     "status":"QUEUED",                     |
  |     "versionNumber":1,                     |
  |     "jobDocument":{...}}}                  |
  |<-------------------------------------------|
  |                                            |
```

- The `$next` keyword is a special jobId that returns the next pending job (IN_PROGRESS or QUEUED).
- The wildcard `+` in subscribe topics matches any jobId, so you don't need to know the jobId in advance.
- If no pending jobs exist, the response will have `"execution": {}`.

### Phase 2: Job Execution (UpdateJobExecution)

Once the device has the job details, it executes the job and reports progress by publishing to the update topic. The `versionNumber` increments with each update, and `expectedVersion` provides optimistic locking.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 0. SUB: $aws/things/{thingName}/           |
  |         jobs/+/update/accepted             |
  |------------------------------------------->|
  |    SUB: $aws/things/{thingName}/           |
  |         jobs/+/update/rejected             |
  |------------------------------------------->|
  |                                            |
  |--- Step 1: Mark IN_PROGRESS ---------------|
  |                                            |
  | 1. PUB: $aws/things/{thingName}/           |
  |         jobs/{jobId}/update                |
  |    {"status":"IN_PROGRESS",                |
  |     "expectedVersion":1,                   |
  |     "clientToken":"token-001"}             |
  |------------------------------------------->|
  |                                            |
  | RCV on /jobs/{jobId}/update/accepted:      |
  |    {"clientToken":"token-001",...}          |
  |<-------------------------------------------|
  |    (versionNumber is now 2)                |
  |                                            |
  |--- Step 2: Report Progress (optional) -----|
  |                                            |
  | 2. PUB: $aws/things/{thingName}/           |
  |         jobs/{jobId}/update                |
  |    {"status":"IN_PROGRESS",                |
  |     "statusDetails":                       |
  |       {"step":"downloading","progress":"50%"},|
  |     "expectedVersion":2,                   |
  |     "clientToken":"token-002"}             |
  |------------------------------------------->|
  |                                            |
  | RCV on /jobs/{jobId}/update/accepted:      |
  |    {"clientToken":"token-002",...}          |
  |<-------------------------------------------|
  |    (versionNumber is now 3)                |
  |                                            |
  |--- Step 3: Mark SUCCEEDED or FAILED -------|
  |                                            |
  | 3. PUB: $aws/things/{thingName}/           |
  |         jobs/{jobId}/update                |
  |    {"status":"SUCCEEDED",                  |
  |     "statusDetails":                       |
  |       {"step":"complete"},                 |
  |     "expectedVersion":3,                   |
  |     "clientToken":"token-003"}             |
  |------------------------------------------->|
  |                                            |
  | RCV on /jobs/{jobId}/update/accepted:      |
  |    {"clientToken":"token-003",...}          |
  |<-------------------------------------------|
  |                                            |
  |--- Next Job Notification ------------------|
  |                                            |
  | RCV on /jobs/notify-next:                  |
  |    (next pending job, or empty if none)    |
  |<-------------------------------------------|
  |                                            |
  | RCV on /jobs/notify:                       |
  |    (updated pending job list)              |
  |<-------------------------------------------|
  |                                            |
```

Key points about the update flow:

- **`expectedVersion`** — Optimistic locking. Must match the current `versionNumber` on the server. Increments with each successful update. If mismatched, the update is rejected with `VersionMismatch`.
- **`clientToken`** — An arbitrary string set by the device. The same token is echoed back in the `/accepted` response, allowing the device to correlate which request a response belongs to. Especially useful when subscribing with wildcards like `/jobs/+/update/accepted`.
- **`statusDetails`** — Optional key-value pairs for tracking progress. Not included by default; the device must explicitly set them.
- **`stepTimeoutInMinutes`** — Optional. If set, the job execution times out if not updated to a terminal state before the timer expires.

### Workflow 1: Get Next Job (Recommended)

Combines passive retrieval + execution. Uses `StartNextPendingJobExecution` to atomically get and start the next job.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 1. SUB: /jobs/notify-next                  |
  |------------------------------------------->|
  |                                            |
  | 2. PUB: /jobs/start-next                   |
  |    {"clientToken":"..."}                   |
  |------------------------------------------->|
  |                                            |
  | RCV: /jobs/start-next/accepted             |
  |<-------------------------------------------|
  | (job already IN_PROGRESS + jobDocument)    |
  |                                            |
  | 3. [Execute job...]                        |
  |                                            |
  | 4. PUB: /jobs/{jobId}/update               |
  |    (status: SUCCEEDED/FAILED)              |
  |------------------------------------------->|
  |                                            |
  | RCV: /jobs/{jobId}/update/accepted         |
  |<-------------------------------------------|
  |                                            |
  | RCV: /jobs/notify-next                     |
  |<-------------------------------------------|
  | (next job or empty → loop back to step 2)  |
  |                                            |
```

`StartNextPendingJobExecution` combines DescribeJobExecution($next) + UpdateJobExecution(IN_PROGRESS) into a single atomic call.

### Workflow 2: Select From Available Jobs

The device gets the full list and picks which job to execute.

```
Device                                    AWS IoT Jobs
  |                                            |
  | 1. SUB: /jobs/notify                       |
  |------------------------------------------->|
  |                                            |
  | 2. PUB: /jobs/get                          |
  |------------------------------------------->|
  |                                            |
  | RCV: /jobs/get/accepted                    |
  |<-------------------------------------------|
  | {"inProgressJobs":[...],"queuedJobs":[...]}|
  |                                            |
  | 3. [Select job from list]                  |
  |                                            |
  | 4. PUB: /jobs/{jobId}/get                  |
  |------------------------------------------->|
  |                                            |
  | RCV: /jobs/{jobId}/get/accepted            |
  |<-------------------------------------------|
  | (job document + details)                   |
  |                                            |
  | 5. PUB: /jobs/{jobId}/update               |
  |    (status: IN_PROGRESS)                   |
  |------------------------------------------->|
  |                                            |
  | 6. [Execute and complete job...]           |
  |                                            |
```

### Full Lifecycle with Events (Cloud-Side Monitoring)

```
Cloud App          AWS IoT Jobs          Device          Event Subscribers
    |                   |                  |                    |
    | CreateJob         |                  |                    |
    |------------------>|                  |                    |
    |                   |                  |                    |
    |                   | /jobs/notify     |                    |
    |                   | /jobs/notify-next|                    |
    |                   |----------------->|                    |
    |                   |                  |                    |
    |                   |                  | start-next         |
    |                   |<-----------------|                    |
    |                   |                  |                    |
    |                   |  (status now IN_PROGRESS,            |
    |                   |   versionNumber incremented)         |
    |                   |                  |                    |
    |                   |                  | update: IN_PROGRESS|
    |                   |                  | (with statusDetails|
    |                   |                  |  and progress)     |
    |                   |<-----------------|                    |
    |                   |                  |                    |
    |                   |                  | update: SUCCEEDED  |
    |                   |<-----------------|                    |
    |                   |                  |                    |
    |                   | /events/jobExecution/{jobId}/succeeded|
    |                   |-------------------------------------->|
    |                   |                  |                    |
    |                   | /events/job/{jobId}/completed         |
    |                   |-------------------------------------->|
    |                   |                  |                    |
    |                   | /jobs/notify-next|                    |
    |                   |----------------->|                    |
    |                   | (next job or empty)                  |
    |                   |                  |                    |
```

## MQTT Topics

### Device Topics (Request/Response)

| Topic                                                  | Operation                    | Direction        |
| ------------------------------------------------------ | ---------------------------- | ---------------- |
| `$aws/things/{thingName}/jobs/get`                     | GetPendingJobExecutions      | Device → Service |
| `$aws/things/{thingName}/jobs/get/accepted`            | Response                     | Service → Device |
| `$aws/things/{thingName}/jobs/get/rejected`            | Error                        | Service → Device |
| `$aws/things/{thingName}/jobs/start-next`              | StartNextPendingJobExecution | Device → Service |
| `$aws/things/{thingName}/jobs/start-next/accepted`     | Response                     | Service → Device |
| `$aws/things/{thingName}/jobs/start-next/rejected`     | Error                        | Service → Device |
| `$aws/things/{thingName}/jobs/{jobId}/get`             | DescribeJobExecution         | Device → Service |
| `$aws/things/{thingName}/jobs/{jobId}/get/accepted`    | Response                     | Service → Device |
| `$aws/things/{thingName}/jobs/{jobId}/get/rejected`    | Error                        | Service → Device |
| `$aws/things/{thingName}/jobs/{jobId}/update`          | UpdateJobExecution           | Device → Service |
| `$aws/things/{thingName}/jobs/{jobId}/update/accepted` | Response                     | Service → Device |
| `$aws/things/{thingName}/jobs/{jobId}/update/rejected` | Error                        | Service → Device |

### Notification Topics (Service → Device)

| Topic                                      | When Published                      |
| ------------------------------------------ | ----------------------------------- |
| `$aws/things/{thingName}/jobs/notify`      | Job added/removed from pending list |
| `$aws/things/{thingName}/jobs/notify-next` | Next pending job changed            |

**notify payload:**

```json
{
  "timestamp": 1517016948,
  "jobs": {
    "IN_PROGRESS": [{"jobId": "job1", ...}],
    "QUEUED": [{"jobId": "job2", ...}]
  }
}
```

**notify-next payload:**

```json
{
  "timestamp": 1517016948,
  "execution": {
    "jobId": "job1",
    "status": "QUEUED",
    "jobDocument": {...}
  }
}
```

### Event Topics (Service → Cloud)

**Job-Level Events:**
| Topic | Trigger |
|-------|---------|
| `$aws/events/job/{jobId}/completed` | All executions completed |
| `$aws/events/job/{jobId}/canceled` | Job canceled |
| `$aws/events/job/{jobId}/cancellation_in_progress` | Job cancellation started |
| `$aws/events/job/{jobId}/deleted` | Job deleted |
| `$aws/events/job/{jobId}/deletion_in_progress` | Job deletion started |

**Job Execution Events:**
| Topic | Trigger |
|-------|---------|
| `$aws/events/jobExecution/{jobId}/succeeded` | Execution succeeded |
| `$aws/events/jobExecution/{jobId}/failed` | Execution failed |
| `$aws/events/jobExecution/{jobId}/rejected` | Execution rejected by device |
| `$aws/events/jobExecution/{jobId}/canceled` | Execution canceled |
| `$aws/events/jobExecution/{jobId}/timed_out` | Execution timed out |
| `$aws/events/jobExecution/{jobId}/removed` | Execution removed |
| `$aws/events/jobExecution/{jobId}/deleted` | Execution deleted |

## Communication Patterns

| Pattern              | Direction        | Subscribe Required  | Use Case                    |
| -------------------- | ---------------- | ------------------- | --------------------------- |
| **Request/Response** | Device → Service | No (direct receive) | Device queries/updates jobs |
| **Notify**           | Service → Device | Yes                 | Real-time job notifications |
| **Events**           | Service → Cloud  | Yes                 | Fleet monitoring            |

## Notification Behavior

**notify** (ListNotification) publishes when:

- A new job execution is added to the pending list (QUEUED)
- A job execution is removed from the pending list (moved to a terminal state: SUCCEEDED, FAILED, REJECTED, CANCELED, TIMED_OUT, REMOVED)
- Does NOT fire when a job simply transitions from QUEUED → IN_PROGRESS (the job is still in the pending list)
- Contains up to 15 pending executions, sorted by status (IN_PROGRESS first, then QUEUED)

**notify-next** (NextNotification) publishes when:

- The "first" (next-to-execute) job execution in the list changes. Specifically:
  - A new job is created and it becomes the first in the queue
  - The current first job completes (terminal state) and the next one takes its place
  - A different job is moved to IN_PROGRESS out of order, making it the new "first"
- Does NOT fire when a second/third job is added while the first job is unchanged
- Does NOT fire when the current first job transitions from QUEUED → IN_PROGRESS (it's still the first job)

Example scenario (from [official docs](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-comm-notifications.html)):

1. `job1` created → both `notify` and `notify-next` fire
2. `job2` created → only `notify` fires (next job is still `job1`)
3. `job1` moves to IN_PROGRESS → neither fires (list unchanged, next job unchanged)
4. `job3` created → only `notify` fires (next job is still `job1`)
5. `job1` completes (SUCCEEDED) → both fire (`job1` removed from list, `job2` becomes next)
6. `job3` forced to IN_PROGRESS (out of order) → only `notify-next` fires (`job3` is now "first" because IN_PROGRESS sorts before QUEUED)
7. `job2` rejected (REJECTED) → only `notify` fires (`job2` removed from list)
8. `job3` force-deleted → both fire (list is now empty)

## Job Execution States

**Non-Terminal:**

`QUEUED` - Waiting to execute
`IN_PROGRESS` - Currently executing

**Terminal:**

`SUCCEEDED` - Completed successfully
`FAILED` - Execution failed
`REJECTED` - Device rejected the job
`CANCELED` - Job was canceled
`TIMED_OUT` - Execution exceeded timeout
`REMOVED` - Execution was removed

## References

- [AWS IoT Jobs](https://docs.aws.amazon.com/iot/latest/developerguide/iot-jobs.html)
- [Devices and Jobs](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-devices.html)
- [Device Workflow](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-workflow-device-online.html)
- [Jobs Workflow](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-workflow-jobs-online.html)
- [Jobs Notifications](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-comm-notifications.html)
- [Jobs MQTT API](https://docs.aws.amazon.com/iot/latest/developerguide/jobs-mqtt-api.html)
- [Reserved MQTT Topics](https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html#reserved-topics-job)
