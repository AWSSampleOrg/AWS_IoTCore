#!/usr/bin/env bash

aws cloudformation deploy \
  --template-file template.yml \
  --stack-name ${1:-fleet-stack} \
  --capabilities CAPABILITY_NAMED_IAM
