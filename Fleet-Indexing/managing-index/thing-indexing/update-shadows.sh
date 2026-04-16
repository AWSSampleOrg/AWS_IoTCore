#!/usr/bin/env bash
# Update shadows to match AWS documentation examples
# Based on: https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html

STACK_NAME="${1:-fleet-indexing-test}"

echo "=== Updating Thing Shadows ==="
echo "Based on AWS documentation examples"
echo "Stack: $STACK_NAME"
echo ""

# Get thing names from stack
THING1="${STACK_NAME}-mything1"
THING2="${STACK_NAME}-mything2"

# Update mything2 shadow (from doc example)
echo "Updating shadow for ${THING2}..."
SHADOW_DOC='{
  "state": {
    "desired": {
      "location": "new york",
      "myvalues": [3, 4, 5]
    },
    "reported": {
      "location": "new york",
      "myvalues": [1, 2, 3],
      "stats": {
        "battery": 78
      }
    }
  }
}'

aws iot-data update-thing-shadow \
  --thing-name "$THING2" \
  --payload "$(echo "$SHADOW_DOC" | base64)" \
  /dev/stdout

echo "Shadow updated for ${THING2}"
echo ""
echo "Wait 10 seconds for indexing..."
sleep 10
echo ""
echo "Now run: ./test-queries.sh $STACK_NAME"
