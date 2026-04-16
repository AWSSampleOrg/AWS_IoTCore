#!/usr/bin/env bash
# Based on https://docs.aws.amazon.com/iot/latest/developerguide/query-syntax.html

echo "=== Query Syntax Examples ==="
echo ""
echo "1. Prefix Search: thingName:sensor*"
echo "2. Range: attributes.temperature:[20 TO 30]"
echo "3. Boolean AND: thingName:sensor* AND attributes.location:zone-1"
echo "4. Boolean OR: attributes.location:zone-1 OR attributes.location:zone-2"
echo "5. Boolean NOT: thingName:tv* AND NOT thingName:*plasma"
echo "6. Comparison: shadow.reported.battery>80"
echo "7. Connectivity: connectivity.connected:true"
echo "8. Grouping: (attributes.location:zone-1 OR attributes.location:zone-2) AND shadow.reported.battery>50"
echo ""
echo "Notes:"
echo "- Default operator is AND"
echo "- Field names are case sensitive"
echo "- Maximum 12 terms per query"
