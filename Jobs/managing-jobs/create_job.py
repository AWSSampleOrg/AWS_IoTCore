import boto3
import json
import uuid

iot_client = boto3.client("iot")


def main(thing_arn: str, s3_download_role_arn: str):
    response = iot_client.create_job(
        jobId=str(uuid.uuid4()),
        targets=[thing_arn],
        document=json.dumps(
            {
                "operation": "update",
                "version": "2.0.1",
                "file": "${aws:iot:s3-presigned-url-v2:https://<bucket>.s3.<region>.amazonaws.com/AWSIoT/Jobs/test.txt}",
            }
        ),
        # timeoutConfig={ "inProgressTimeoutInMinutes": 100 },
        # jobExecutionsRolloutConfig={
        #     "exponentialRate": {
        #         "baseRatePerMinute": 50,
        #         "incrementFactor": 2,
        #         "rateIncreaseCriteria": {
        #         "numberOfNotifiedThings": 1000,
        #         "numberOfSucceededThings": 1000
        #         }
        #     },
        #     "maximumPerMinute": 1000
        # },
        # targetSelection = "SNAPSHOT",
        # abortConfig={
        #     "criteriaList": [
        #         {
        #             "action": "CANCEL",
        #             "failureType": "FAILED",
        #             "minNumberOfExecutedThings": 100,
        #             "thresholdPercentage": 20
        #         },
        #         {
        #             "action": "CANCEL",
        #             "failureType": "TIMED_OUT",
        #             "minNumberOfExecutedThings": 200,
        #             "thresholdPercentage": 50
        #         }
        #     ]
        # },
        presignedUrlConfig={"roleArn": s3_download_role_arn, "expiresInSec": 3600},
    )
    print(f'Job created: {response["jobArn"]}')


if __name__ == "__main__":
    thing_arn = ""
    s3_download_role_arn = ""
    main(thing_arn=thing_arn, s3_download_role_arn=s3_download_role_arn)
