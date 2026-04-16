#!/usr/bin/env bash

STACK_NAME="${1:-fleet-indexing-test}"

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file template.yml \
  --stack-name "$STACK_NAME"

echo ""
echo "Configuring fleet indexing..."
python fleet_indexing.py enable
