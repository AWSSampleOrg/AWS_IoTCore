FROM ubuntu:22.04

RUN apt update -y && apt install build-essential -y
# Other useful libraries
RUN apt install -y \
    clang \
    clang-tidy \
    clang-format \
    cmake \
    gcc \
    g++ \
    jq \
    llvm \
    wget \
    git \
    openssl \
    libcurl4-openssl-dev \
    liblog4cxx-dev \
    libssl-dev \
    sudo \
    pkg-config

# install AWS IoT SDK for C++2
ENV SOURCE_DIR /opt/work
WORKDIR ${SOURCE_DIR}
RUN git clone --recursive https://github.com/aws/aws-iot-device-sdk-cpp-v2.git
# Ensure all submodules are properly updated
RUN cd ${SOURCE_DIR}/aws-iot-device-sdk-cpp-v2 && git submodule update --init --recursive
# Make a build directory for the SDK. Can use any name.
# If working with multiple SDKs, using a SDK-specific name is helpful.
WORKDIR ${SOURCE_DIR}/build
RUN cmake -DCMAKE_INSTALL_PREFIX=${SOURCE_DIR} -DBUILD_DEPS=ON -DCMAKE_BUILD_TYPE="Release" ../aws-iot-device-sdk-cpp-v2
RUN cmake --build . --target install --config "Release"
