
#!/bin/bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-0}) && pwd)
echo ${SOURCE_DIR}

readonly image_name="awsiot-cpp:latest" 2> /dev/null

function blue()
{
    echo -e "\033[34m${1}\033[0m"
}

case $1 in
    "build") blue "Build Docker Images"
        docker image build -t ${image_name} ${SOURCE_DIR};;

    "exec") blue "Execute Docker container"
	    docker container exec -it ${CONTAINER_ID} sh;;

	"rmc") blue "Remove All Docker Containers"
	    docker container rm -f ${CONTAINER_ID};;

	"rmi") blue "Remove All Docker Images"
	    docker image rm -f ${image_name};;

	"run") blue "Run Docker container"
	    CONTAINER_ID=$(docker container run -itd -p 80:80 ${image_name});;

    *) blue "Give me docker command parameter";;
esac
