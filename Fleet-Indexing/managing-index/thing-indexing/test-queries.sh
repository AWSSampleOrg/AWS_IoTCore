#!/usr/bin/env bash
# Test queries based on https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html

STACK_NAME="${1:-fleet-indexing-test}"

echo "=== AWS IoT Thing Indexing Test Queries ==="
echo "Based on: https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html"
echo "Stack: $STACK_NAME"
echo ""

# 1. Describe Index (from doc: "Describing a thing index")
echo "1. Describe Index Status"
echo "Command: aws iot describe-index --index-name AWS_Things"
aws iot describe-index --index-name "AWS_Things"

echo ""
echo "---"
echo ""

# 2. Get Indexing Configuration (from doc: "get-indexing-configuration")
echo "2. Get Indexing Configuration"
echo "Command: aws iot get-indexing-configuration"
aws iot get-indexing-configuration

echo ""
echo "---"
echo ""

# 3. Search by thing name (from doc: "Querying a thing index")
echo "3. Search by Thing Name (thingName:mything*)"
echo "Command: aws iot search-index --index-name AWS_Things --query-string \"thingName:${STACK_NAME}-mything*\""
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "thingName:${STACK_NAME}-mything*"

echo ""
echo "---"
echo ""

# 4. Search by attribute (from doc example: attributes.model, attributes.country)
echo "4. Search by Attribute (attributes.country:usa)"
echo "Command: aws iot search-index --index-name AWS_Things --query-string \"attributes.country:usa\""
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "attributes.country:usa AND thingName:${STACK_NAME}-mything*"

echo ""
echo "---"
echo ""

# 5. Search by shadow (from doc example: shadow.reported.stats.battery)
echo "5. Search by Shadow (shadow.reported.stats.battery>70)"
echo "Command: aws iot search-index --index-name AWS_Things --query-string \"shadow.reported.stats.battery>70\""
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "shadow.reported.stats.battery>70 AND thingName:${STACK_NAME}-mything*"

echo ""
echo "---"
echo ""

# 6. Search by connectivity (from doc: connectivity.connected)
echo "6. Search by Connectivity Status (connectivity.connected:true)"
echo "Command: aws iot search-index --index-name AWS_Things --query-string \"connectivity.connected:true\""
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "connectivity.connected:true AND thingName:${STACK_NAME}-mything*"

echo ""
echo "---"
echo ""

# 7. Search by thing type (from doc example: MyThingType)
echo "7. Search by Thing Type"
echo "Command: aws iot search-index --index-name AWS_Things --query-string \"thingTypeName:*MyThingType\""
aws iot search-index \
  --index-name "AWS_Things" \
  --query-string "thingTypeName:${STACK_NAME}-MyThingType"

echo ""
echo "=== Test Complete ==="
