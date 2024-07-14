# export AWS IoT endpoint as an environment value

```sh
# The command shown below will help you know the IoT Endpoint with CLI.
export AWS_IOT_CORE_ENDPOINT=$(aws iot describe-endpoint \
  --endpoint-type iot:Data-ATS \
  --query endpointAddress \
  --output text)
```

build & execute

```sh
# build source code using cmake
. build.sh
# execute program
./main
```
