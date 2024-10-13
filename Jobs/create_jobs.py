import boto3
import json
import uuid
import sys

iot_client = boto3.client("iot")
client = boto3.client("sts")

def main(thing_name: str, thing_arn: str, s3_download_role_arn: str):
    job_id = str(uuid.uuid4())

    firmware_bucket_name = ""
    s3_key = ""
    iot_client.create_job(
        jobId = job_id,
        targets = [
            thing_arn
        ],
        document = json.dumps({
            'operation': 'update',
            'url': '${aws:iot:s3-presigned-url:https://s3.amazonaws.com/%s/%s}' % (firmware_bucket_name, s3_key)
        }),
        documentSource="",
        timeoutConfig={ "inProgressTimeoutInMinutes": 100 },
        jobExecutionsRolloutConfig={
            "exponentialRate": {
                "baseRatePerMinute": 50,
                "incrementFactor": 2,
                "rateIncreaseCriteria": {
                "numberOfNotifiedThings": 1000,
                "numberOfSucceededThings": 1000
                }
            },
            "maximumPerMinute": 1000
        },
        targetSelection = "SNAPSHOT",
        abortConfig={
            "criteriaList": [
                {
                    "action": "CANCEL",
                    "failureType": "FAILED",
                    "minNumberOfExecutedThings": 100,
                    "thresholdPercentage": 20
                },
                {
                    "action": "CANCEL",
                    "failureType": "TIMED_OUT",
                    "minNumberOfExecutedThings": 200,
                    "thresholdPercentage": 50
                }
            ]
        },
        presignedUrlConfig={
            'roleArn': s3_download_role_arn,
            'expiresInSec': 3600
        },
    )
    response = iot_client.describe_job_execution(
        jobId = job_id,
        thingName = thing_name
    )
    print(response['execution']["status"])

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) == 4:
        thing_name = argv[1]
        thing_arn = argv[2]
        s3_download_role_arn = argv[3]
        main(
            thing_name=thing_name,
            thing_arn=thing_arn,
            s3_download_role_arn=s3_download_role_arn
        )
