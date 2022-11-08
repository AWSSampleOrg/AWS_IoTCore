#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-0}) && pwd)
echo ${SOURCE_DIR}

IMAGE_NAME="awsiot-cpp:latest"

function blue() {
    echo -e "\033[34m${1}\033[0m"
}

case $1 in
    "build") blue "Build Docker Images"
        docker image build -t ${IMAGE_NAME} ${SOURCE_DIR};;

    "exec") blue "Execute Docker container"
	    docker container exec -it ${CONTAINER_ID} sh;;

	"rmc") blue "Remove All Docker Containers"
	    docker container rm -f ${CONTAINER_ID};;

	"rmi") blue "Remove All Docker Images"
	    docker image rm -f ${IMAGE_NAME};;

	"run") blue "Run Docker container"
	    CONTAINER_ID=$(docker container run -itd -p 80:80 ${IMAGE_NAME});;

    *) blue "Give me docker command parameter";;
esac
