#!/usr/bin/env bash
set -e

STACK_NAME='jitp-stack'

aws cloudformation deploy \
  --template-file template.yml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_NAMED_IAM
