import datetime
import json
import logging
import os
from datetime import datetime

import history_db as hdb
import the_pups as tp
import pandas as pd

folder_name = 'dogs_on_campus'
snippets_bucket = os.environ['SNIPPETS_BUCKET']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_dog_count_stats(counts_by_date: pd.DataFrame) -> pd.DataFrame:
    stats_by_level = counts_by_date.describe(percentiles=[.25, .5, .75, .9]).astype('int32')
    stats_by_level.drop('count', inplace=True)
    stats_by_level.drop('std', inplace=True)
    return stats_by_level


def get_dogs_on_campus_stats(stats_df: pd.DataFrame) -> pd.DataFrame:
    return stats_df[['Nbr of Dogs']].copy().T


def get_dogs_on_campus_by_group(stats_df: pd.DataFrame) -> pd.DataFrame:
    return stats_df[['DBS', 'Staff']].copy().T


def get_dogs_on_campus_by_dbs_level(stats_df: pd.DataFrame) -> pd.DataFrame:
    return stats_df[['Green', 'Blue', 'Purple', 'Red - Team']].copy().T


def get_dogs_on_campus_by_staff_level(stats_df: pd.DataFrame) -> pd.DataFrame:
    return stats_df[['Orange', 'Red - Default', 'Red', 'Red - BQ']].copy().T


def get_stats_as_html(data: pd.DataFrame, group_name: str) -> str:
    data_out = data.rename(columns={'count': 'Nbr of Dogs', 'mean': 'Average', 'min': 'Min', 'max': 'Max'})

    return data_out.to_html(table_id=f'{group_name}_stats_table', index=True, border=0,
                            classes="table table-striped table-hover")


def get_formatted_period(period: tuple) -> str:
    start_date = datetime.strftime(period[0], '%b %d, %Y')
    end_date = datetime.strftime(period[1], '%b %d, %Y')
    return f'{start_date} through {end_date}'


def lambda_handler(event, context):
    dog_history_df = hdb.dataframe_from_history()
    period = hdb.get_history_dates(dog_history_df)
    counts_by_date_df = hdb.get_counts_by_date(dog_history_df)
    count_stats_df = get_dog_count_stats(counts_by_date_df)

    dog_stats = get_dogs_on_campus_stats(count_stats_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_all_dogs_table.html',
                   get_stats_as_html(dog_stats, 'all_dogs'))

    dog_stats = get_dogs_on_campus_by_group(count_stats_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_group_table.html',
                   get_stats_as_html(dog_stats, 'group'))

    dog_stats = get_dogs_on_campus_by_dbs_level(count_stats_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_dbs_level_table.html',
                   get_stats_as_html(dog_stats, 'dbs'))

    dog_stats = get_dogs_on_campus_by_staff_level(count_stats_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_staff_level_table.html',
                   get_stats_as_html(dog_stats, 'staff'))

    tp.write_to_s3(snippets_bucket, f'{folder_name}/report_period.html', get_formatted_period(period))
    return {
        'statusCode': 200,
        'body': json.dumps('Stats compiled and html pages generated.')
    }
