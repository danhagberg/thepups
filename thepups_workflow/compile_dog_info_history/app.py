import datetime
import json
import logging
import os
from datetime import datetime

import history_db as hdb
import the_pups as tp
import pandas as pd

snippets_bucket = os.environ['SNIPPETS_BUCKET']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_dog_info_as_html(dogs_df):
    dog_info_df = dogs_df[['name', 'Level', 'animal_id', 'weight', 'age', 'date', 'days_on_campus']]
    dog_info_df = dog_info_df.rename(columns={'weight': 'Weight', 'age': 'Age', 'date': 'Exit Date',
                                              'days_on_campus': 'Total Days On Campus', 'name': 'Name',
                                              'animal_id': 'ID'}).sort_values('Name')
    return dog_info_df.to_html(table_id='dog_info', index=False, border=0, classes="table table-striped table-hover")


def get_formatted_period(period: tuple) -> str:
    start_date = datetime.strftime(period[0], '%b %d, %Y')
    end_date = datetime.strftime(period[1], '%b %d, %Y')
    return f'{start_date} through {end_date}'


def lambda_handler(event, context):
    summary_df = hdb.dataframe_from_summary()
    period = hdb.get_history_dates(summary_df)
    tp.write_to_s3(snippets_bucket, 'all_dog_info.html', get_dog_info_as_html(summary_df))

    tp.write_to_s3(snippets_bucket, 'all_dog_info_report_period.html', get_formatted_period(period))
    return {
        'statusCode': 200,
        'body': json.dumps('Dog history compiled and html pages generated.')
    }
