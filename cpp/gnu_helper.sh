#!/usr/bin/env bash

SOURCE_DIR=$(cd $(dirname ${BASH_SOURCE:-$0}) && pwd)

# https://gcc.gnu.org/legacy-ml/gcc-help/2007-09/msg00216.html
echo | g++ -v -x c++ -E - > ${SOURCE_DIR}/g++_config 2>&1
echo | gcc -v -x c++ -E - > ${SOURCE_DIR}/gcc_config 2>&1
