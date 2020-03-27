from datetime import date

import boto3
import pandas as pd

dynamodb_client = boto3.resource('dynamodb')
history_table = dynamodb_client.Table('campus_dog_history')
summary_table = dynamodb_client.Table('campus_dog_summary')


def group_by_age(clean_summary_df: pd.DataFrame) -> pd.DataFrame:
    bins = [0, 6, 12, 60, 120, 1000]
    labels = ['1: Age 0-6m', '2: Age 7-12m', '3: Age 13-60m', '4: Age 61-120m', '5: Age > 120m']
    clean_summary_df.loc[:, 'age_group'] = pd.cut(clean_summary_df.age, bins, labels=labels)
    return clean_summary_df


def group_by_weight(clean_summary_df: pd.DataFrame) -> pd.DataFrame:
    bins = [0, 15, 40, 65, 90, 1000]
    labels = ['1: 0-15lb', '2: 16-40lb', '3: 41-65lb', '4: Age 66-90lb', '5: > 90lb']
    clean_summary_df.loc[:, 'weight_group'] = pd.cut(clean_summary_df.weight, bins, labels=labels)
    return clean_summary_df


def remove_zero_values(summary_df: pd.DataFrame) -> pd.DataFrame:
    return summary_df.loc[~(summary_df == 0).any(axis=1)].copy()


def dataframe_from_history() -> pd.DataFrame:
    history_scan_response = history_table.scan()
    history_scan_items = history_scan_response['Items']
    while 'LastEvaluatedKey' in history_scan_response:
        history_scan_response = history_table.scan(ExclusiveStartKey=history_scan_response['LastEvaluatedKey'])
        history_scan_items.extend(history_scan_response['Items'])
    dog_history_df = pd.DataFrame(history_scan_items)
    return dog_history_df


def dataframe_from_summary() -> pd.DataFrame:
    summary_scan_response = summary_table.scan()
    summary_scan_items = summary_scan_response['Items']
    while 'LastEvaluatedKey' in summary_scan_response:
        summary_scan_response = summary_table.scan(ExclusiveStartKey=summary_scan_response['LastEvaluatedKey'])
        summary_scan_items.extend(summary_scan_response['Items'])
    dog_summary_df = pd.DataFrame(summary_scan_items)
    dog_summary_df['weight'] = dog_summary_df.weight.apply(int)
    dog_summary_df['age'] = dog_summary_df.age.apply(int)
    dog_summary_df['days_on_campus'] = dog_summary_df.days_on_campus.apply(int)
    dog_summary_df['date'] = dog_summary_df.record_date.apply(date.fromtimestamp)
    return dog_summary_df


def get_history_dates(summary_df: pd.DataFrame) -> tuple:
    return summary_df.date.min(), summary_df.date.max()


def write_to_s3(bucket, file_name, content):
    s3 = boto3.resource('s3')
    path = file_name
    encoded_content = content.encode('utf-8')
    s3.Bucket(bucket).put_object(Key=path, Body=encoded_content)


def read_from_s3(bucket, file):
    s3 = boto3.resource('s3')
    csv_object = s3.Object(bucket, file)
    csv_data = csv_object.get()['Body'].read().decode('utf-8')
    return csv_data

