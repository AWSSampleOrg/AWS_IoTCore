#!/usr/bin/env bash
# Based on https://docs.aws.amazon.com/iot/latest/developerguide/thinggroup-index.html

STACK_NAME="${1:-fleet-indexing-test}"

echo "=== Thing Group Indexing Test ==="
echo ""

echo "1. Get Indexing Configuration"
aws iot get-indexing-configuration

echo ""
echo "2. Describe Index"
aws iot describe-index --index-name "AWS_ThingGroups"

echo ""
echo "3. Search Thing Groups"
aws iot search-index --index-name "AWS_ThingGroups" --query-string "thingGroupName:${STACK_NAME}-mythinggroup*"
