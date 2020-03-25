#!/bin/bash
STAGE=$1
echo Cleaning up s3://${STAGE}-the-pups-output-2020 
aws s3 rb s3://${STAGE}-the-pups-output-2020 --force
echo Cleaning up s3://${STAGE}-the-pups-snippets-2020
aws s3 rb s3://${STAGE}-the-pups-snippets-2020 --force
echo Cleaning up s3://${STAGE}-the-pups-uploads-2020 --force
aws s3 rb s3://${STAGE}-the-pups-uploads-2020 --force
