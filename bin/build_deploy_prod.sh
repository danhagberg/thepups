#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
echo "$SCRIPT_DIR"
pushd "$SCRIPT_DIR"/../thepups_workflow || exit
sam build --use-container
BUILD_STATUS=$?
echo Status of build: $BUILD_STATUS
if [[ $BUILD_STATUS == 0 ]]; then
  echo Status of build was successful. Deploying ...
  sam deploy --stack-name=thepup-info-prod --s3-bucket=aws-sam-cli-managed-default-samclisourcebucket-1h3galvgqsgw0 --s3-prefix=thepup-info-prod --region=us-west-2 --capabilities=CAPABILITY_IAM --parameter-overrides="Env=\"prod\" XRayTracing=\"PassThrough\" ThePupsInfoSnippetsBucketName=\"the-pups-snippets-2020\" ThePupsOutputDataBucketName=\"the-pups-output-2020\" ThePupsUploadsBucketName=\"the-pups-uploads-2020\" ThePupsDogHistoryTableName=\"the-pups-campus-dog-history\" ThePupsDogSummaryTableName=\"the-pups-campus-dog-summary\" ThePupsCampusHistoryUpdatedSnsName=\"the-pups-campus-history-updated\""
else
  echo Build failed
fi
popd || exit
