import boto3
import json
import uuid

iot_client = boto3.client("iot")

with open("job_template.json", "r") as f:
    job_doc = json.load(f)

def main(thing_arn: str, s3_download_role_arn: str):
    job_template = iot_client.create_job_template(
        jobTemplateId="JobTemplate",
        description="JobTemplate",
        document = json.dumps(job_doc),
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
        presignedUrlConfig={
            'roleArn': s3_download_role_arn,
            'expiresInSec': 3600
        },
    )
    response = iot_client.create_job(
        jobId = str(uuid.uuid4()),
        targets = [
            thing_arn
        ],
        jobTemplateArn=job_template["jobTemplateArn"],
    )
    print(f'Job created: {response["jobArn"]}')

if __name__ == "__main__":
    thing_arn = ""
    s3_download_role_arn = ""
    main(
        thing_arn=thing_arn,
        s3_download_role_arn=s3_download_role_arn
    )
