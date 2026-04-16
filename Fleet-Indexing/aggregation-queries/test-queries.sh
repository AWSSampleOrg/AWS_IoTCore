#!/usr/bin/env bash
# Based on https://docs.aws.amazon.com/iot/latest/developerguide/index-aggregate.html

echo "=== Aggregation Query Examples ==="
echo ""

echo "1. GetStatistics - String Field"
echo "aws iot get-statistics --aggregation-field 'attributes.stringAttribute' --query-string '*'"
echo ""

echo "2. GetStatistics - Numerical Field"
echo "aws iot get-statistics --aggregation-field 'attributes.numericAttribute2' --query-string '*'"
echo ""

echo "3. GetCardinality"
echo "aws iot get-cardinality --query-string 'batterylevel > 50' --aggregation-field 'shadow.reported.batterylevel'"
echo ""

echo "4. GetPercentiles"
echo "aws iot get-percentiles --query-string 'thingName:*' --aggregation-field 'attributes.customField_NUM' --percents 10 20 30 40 50 60 70 80 90 99"
echo ""

echo "5. GetBucketsAggregation"
echo "aws iot get-buckets-aggregation --query-string '*' --aggregation-field 'shadow.reported.batterylevelpercent' --buckets-aggregation-type 'termsAggregation={maxBuckets=5}'"
echo ""

echo "Running examples..."
echo ""

echo "Example 1: Count all things"
aws iot get-statistics --index-name "AWS_Things" --query-string "*"

echo ""
echo "Example 2: Unique thing types"
aws iot get-cardinality --index-name "AWS_Things" --query-string "*" --aggregation-field "registry.thingTypeName"
