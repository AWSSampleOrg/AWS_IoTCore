FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# build-essential
RUN apt update -y && apt install build-essential -y
RUN apt install -y openssl cmake mosquitto git libssl-dev

RUN mkdir -p /IoT
COPY . /IoT
WORKDIR /IoT

# install AWS IoT SDK for C++2
RUN git clone --recursive https://github.com/aws/aws-iot-device-sdk-cpp-v2.git
RUN source setup.sh
WORKDIR /IoT/src
