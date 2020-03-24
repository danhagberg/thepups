import csv
import json
import logging
import os
import re
from datetime import datetime

import boto3
import numpy as np
import pandas as pd
from dateutil import parser
from dateutil.tz import gettz

snippets_bucket = os.environ['SNIPPETS_BUCKET']
output_data_bucket = os.environ['OUTPUT_DATA_BUCKET']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_age_in_months(in_text):
    match = re.search(r'.*/(\d\d)y (\d\d)m', in_text, flags=re.IGNORECASE)
    age = match.groups() if match else ('0', '0')
    age_in_months = int(age[0]) * 12 + int(age[1])
    return age_in_months


def get_name(in_text):
    name = in_text.split(',')[0]
    name = name.split('- Adop')[0]
    name = name.split('*')[0]
    return name.strip()


def get_weight(in_text):
    if len(in_text.strip()) > 0:
        weight_str = in_text.split()[0]
        weight = int(weight_str) if weight_str.isnumeric() else 0
    else:
        weight = 0
    return weight


def get_level(row):
    level = row[4].split()[0].lower() if len(row[4]) > 0 else None
    if level in ['green', 'blue', 'purple', 'red', 'orange']:
        level = level.capitalize()
        if level == 'Red':
            if re.match(r'.*No Handling Level.*', row[5], re.IGNORECASE):
                level = 'Red - Default'
            elif re.match(r'.*Team.*', row[5], re.IGNORECASE):
                level = 'Red - Team'
    else:
        level = None
    return level


def extract_report_time(rpt_title):
    title_parts = rpt_title.split('-')
    timezone_info = {'PT': gettz('US/Pacific')}
    rpt_time_str = title_parts[1].strip() + ' PT'
    rpt_time = parser.parse(rpt_time_str, tzinfos=timezone_info)
    return rpt_time


def get_dogs(csv_contents):
    dogs = {}
    # with open(file_loc, 'r') as dogs_csv:
    current_dog = None
    k_reader = csv.reader(csv_contents.splitlines())
    for row in k_reader:
        row = row[8:]
        if 'Dog Exercise List' in row[0]:
            report_time = extract_report_time(row[0])
        elif row[0] == 'AM':
            name = get_name(row[5])
            weight = get_weight(row[7])
            loc = row[3]
            age = get_age_in_months(row[6])
            id = row[8]
            current_dog = name
            dogs[current_dog] = {
                'id': id,
                'weight': weight,
                'location': loc,
                'age': age,
                'holder': False,
                'kc': False,
                'bite': False,
                'Level': None,
                'level_note': None,
                'stress': False,
                'stress_note': None,
                'team': False,
                'diet': [],
                'notes': []
            }
        elif row[0] == 'DIET':
            dogs[current_dog]['diet'].append(row[5])
        elif len(row) < 2:
            # End of dog notes
            current_dog = None
        elif re.match(r'(.*intake.*|.*incident.*)',
                      row[4],
                      flags=re.IGNORECASE):
            # Intake notes. Skip
            pass
        elif row[0] == 'H':
            dogs[current_dog]['holder'] = True
        elif 'Bite Quarantine' in row[4]:
            dogs[current_dog]['bite'] = True
        elif 'Kennel Stress' in row[4]:
            dogs[current_dog]['stress'] = True
            dogs[current_dog]['stress_note'] = row[5] if len(row[5].strip()) > 0 else None
        elif 'Kennel Cough' in row[4]:
            dogs[current_dog]['kc'] = True
        elif row[0] in ['RDR']:
            # Run dog run.  Skip
            pass
        else:
            level = get_level(row)
            if level:
                dogs[current_dog]['Level'] = level if dogs[current_dog]['bite'] is False else 'Red - BQ'
                dogs[current_dog]['level_note'] = row[5] if len(row[5].strip()) > 0 else None
            elif current_dog and len(row[5]) > 0:
                dogs[current_dog]['notes'].append(row[5])

    dogs = {k: v for k, v in dogs.items() if 'DELETE' not in k}

    return dogs, report_time


def get_dog_counts_dataframe(dogs_df):
    aggFunc = {'Level': np.count_nonzero,
               'holder': sum,
               'kc': sum
               }

    dog_counts = dogs_df.groupby(['Level']).agg(aggFunc)

    dog_counts = dog_counts.rename(columns={'Level': 'All', 'holder': 'Holder', 'kc': 'KC'})
    dog_counts = dog_counts.astype('int32')

    row_total = dog_counts.sum()
    row_total.name = 'Total'
    dog_counts = dog_counts.append(row_total)
    return dog_counts


def get_dog_counts_as_html(dogs_df):
    dog_counts_df = get_dog_counts_dataframe(dogs_df)
    dc_out = dog_counts_df.rename(
        index={'Blue': '3 - Blue', 'Green': '2 - Green', 'Orange': '9 - Orange', 'Purple': '4 - Purple',
               'Red': '8 - Red', 'Red - BQ': '6 - Red - BQ', 'Red - Default': '7 - Red - Default',
               'Red - Team': '5 - Red - Team', 'Total': 'Total'}).sort_index()
    return pd.DataFrame(dc_out.to_records()).to_html(index=False, border=0, classes="table table-striped table-hover")


def write_to_s3(bucket, file_name, content):
    s3 = boto3.resource('s3')
    path = file_name
    encoded_content = content.encode('utf-8')
    s3.Bucket(bucket).put_object(Key=path, Body=encoded_content)


def get_dog_info_as_html(dogs_df):
    dog_info_df = dogs_df[['holder', 'Level', 'location', 'kc', 'id']].rename_axis('name')
    dog_info_df = dog_info_df.rename_axis('Name')
    dog_info_df = dog_info_df.rename(columns={'holder': 'Holder', 'location': 'Location', 'kc': 'KC',
                                              'id': 'ID'}).sort_index()
    dog_info_df = pd.DataFrame(dog_info_df.to_records())
    return dog_info_df.to_html(table_id='dog_info', index=False, border=0, classes="table table-striped table-hover")


def get_dog_dataframe(dogs):
    dogs_df = pd.DataFrame.from_dict(dogs, orient='index')
    dogs_df['dbs'] = dogs_df.Level.apply(lambda l: l in ['Green', 'Blue', 'Purple', 'Red - Team'])
    return dogs_df


def filter_for_dbs(dogs_df):
    return dogs_df[(dogs_df['dbs'] == True)]


def filter_for_non_dbs(dogs_df):
    return dogs_df[(dogs_df['dbs'] == False)]


def get_dogs_as_json(dogs_df: pd.DataFrame, report_date: datetime.date):
    dogs_dict = dogs_df.to_dict()
    dogs_json_str = json.dumps({'report_date': report_date.timestamp(), 'dogs': dogs_dict})
    return dogs_json_str


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    s3 = boto3.resource('s3')
    logger.info(f'Received Event for : Bucket: {bucket}, File: {file}')
    dog_list = s3.Object(bucket, file)
    dog_list_csv = dog_list.get()['Body'].read().decode('utf-8')
    dogs, report_time = get_dogs(dog_list_csv)
    dogs_df = get_dog_dataframe(dogs)
    write_to_s3(snippets_bucket, 'dog_count_timestamp.html',
                datetime.strftime(report_time, '%A, %b %d, %Y at %I:%M %p '))
    write_to_s3(snippets_bucket, 'dbs_dog_counts.html', get_dog_counts_as_html(filter_for_dbs(dogs_df)))
    write_to_s3(snippets_bucket, 'staff_dog_counts.html', get_dog_counts_as_html(filter_for_non_dbs(dogs_df)))
    write_to_s3(snippets_bucket, 'dog_info.html', get_dog_info_as_html(dogs_df))
    write_to_s3(output_data_bucket, 'dog-counts.csv', get_dog_counts_dataframe(dogs_df).to_csv())
    write_to_s3(output_data_bucket, 'dogs-on-campus.json', get_dogs_as_json(dogs_df, report_time))

    return {
        'statusCode': 200,
        'body': json.dumps('HTML snippets created and stored in s3')
    }
