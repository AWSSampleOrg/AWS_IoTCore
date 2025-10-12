https://docs.aws.amazon.com/iot/latest/developerguide/iot-jobs.html

# Create a thing.

```sh
cd certificates
./ca_cli.sh
./client_cli.sh
cd ..
./deploy.sh
```

# Upload a file

Replace `bucket` with your own.

```sh
aws s3 cp test.txt s3://<bucket>/AWSIoT/Jobs/test.txt
```

# Create a AWS IoT Job

1. Replace `region` and `bucket` in `job_document.json` with your own.

`/AWSIoT/Jobs/test.txt` is just an example, so you can change it to anything else.

```json
{
  "operation": "update",
  "version": "2.0.1",
  "file": "${aws:iot:s3-presigned-url-v2:https://s3.<region>.amazonaws.com/<bucket>/AWSIoT/Jobs/test.txt}"
}
```

2. Make sure that you have the file you specified above.

Note, In these step 1 and 2, you used your local environment document file, but you can also use the file in S3 bucket.

3. Create a AWS IoT Job.

```sh
python create.py
```

# Get the created job.

```sh
python device_mqtt.py
or
python device_api.py
```
