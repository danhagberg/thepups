import json
import os
import time
from datetime import date, datetime
from typing import Tuple

import boto3
import pandas as pd
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

history_table_name = os.environ['DOG_HISTORY_TABLE_NAME']
summary_table_name = os.environ['DOG_SUMMARY_TABLE_NAME']


def get_dogs(dog_list_json: dict) -> Tuple[dict, date]:
    json_packet = json.loads(dog_list_json)
    dogs_json = json_packet['dogs']
    count_date = datetime.utcfromtimestamp(json_packet['report_date'])
    # Set UTC time to noon, so the local date portion will be on the same day for US timezones.
    count_date = count_date.replace(hour=12, minute=0, second=0, microsecond=0)

    return dogs_json, count_date


def get_dog_dataframe(dogs_json: dict, count_date: date) -> pd.DataFrame:
    dogs_df = pd.DataFrame(dogs_json)
    dogs_df['record_date'] = count_date
    dogs_df['name'] = dogs_df.index
    dogs_df.set_index(['id', 'record_date'], inplace=True)
    dogs_df.index.set_names(['animal_id', 'record_date'], inplace=True)
    return dogs_df


def write_dogs_to_daily_table(dogs_df: pd.DataFrame) -> pd.DataFrame:
    daily_table = dynamodb.Table(history_table_name)
    dogs_flat = pd.DataFrame(dogs_df.to_records())
    dogs_flat['record_date'] = dogs_flat.record_date.apply(lambda rd: int(rd.timestamp()))
    dogs_dict = dogs_flat.to_dict(orient='index')
    count = 1
    for rec in dogs_dict.values():
        daily_table.put_item(Item=rec)
        if count % 50 == 0:
            time.sleep(1)
        count += 1
    return dogs_flat


def write_dogs_to_summary_table(dogs_df: pd.DataFrame):
    summary_table = dynamodb.Table(summary_table_name)
    dog_summary_df = dogs_df.copy()
    dog_summary_df.sort_values(['animal_id', 'record_date'], inplace=True)
    dog_summary_df.drop(
        ['location', 'holder', 'bite', 'kc', 'level_note', 'stress', 'stress_note', 'team', 'diet', 'dbs', 'notes'],
        axis=1, inplace=True)
    dog_summary_df.drop_duplicates(subset=['animal_id'], keep='last', inplace=True)
    dogs_summary_dict = dog_summary_df.to_dict(orient='index')

    count = 1
    for rec in dogs_summary_dict.values():
        try:
            summary_entry = summary_table.get_item(
                Key={
                    'animal_id': rec['animal_id']
                }
            )
            if summary_entry.get('Item') is None:
                rec['days_on_campus'] = 1
                summary_table.put_item(Item=rec)
            else:
                response = summary_table.update_item(
                    Key={
                        'animal_id': rec['animal_id']
                    },
                    UpdateExpression="SET #level = :dbs_level, \
                                       #name = :animal_name, \
                                       weight = :weight, \
                                       record_date = :rec_date, \
                                       age = :age \
                                       ADD days_on_campus :val",
                    ExpressionAttributeNames={
                        '#level': 'Level',
                        '#name': 'name'
                    },
                    ExpressionAttributeValues={
                        ':dbs_level': rec['Level'],
                        ':val': 1,
                        ':animal_name': rec['name'],
                        ':weight': rec['weight'],
                        ':rec_date': rec['record_date'],
                        ':age': rec['age']
                    },
                    ConditionExpression=":rec_date > record_date",
                    ReturnValues='UPDATED_NEW'
                )
        except ClientError as e:
            print(e)
            break
        if count % 30 == 0:
            time.sleep(1)
        count += 1


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    print(bucket, file)
    dog_list = s3.Object(bucket, file)
    dog_list_json = dog_list.get()['Body'].read().decode('utf-8')
    dogs, report_time = get_dogs(dog_list_json)
    dogs_df = get_dog_dataframe(dogs, report_time)
    dog_history_df = write_dogs_to_daily_table(dogs_df)
    write_dogs_to_summary_table(dog_history_df)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Data loaded to {history_table_name} and {summary_table_name} tables')
    }
