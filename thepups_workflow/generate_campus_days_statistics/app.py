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


def get_days_on_campus_stats(clean_summary_df: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(clean_summary_df.days_on_campus.describe(percentiles=[.25, .5, .75, .9])).T
    df.fillna(value='NA', inplace=True)
    return df.astype('int32')


def get_days_on_campus_by_age_stats(clean_summary_df: pd.DataFrame) -> pd.DataFrame:
    df = clean_summary_df.groupby('age_group').days_on_campus.describe(percentiles=[.25, .5, .75, .9])
    df.fillna(value='0', inplace=True)
    return df.astype('int32')


def get_days_on_campus_by_weight_stats(clean_summary_df: pd.DataFrame) -> pd.DataFrame:
    df = clean_summary_df.groupby('weight_group').days_on_campus.describe(percentiles=[.25, .5, .75, .9])
    df.fillna(value='0', inplace=True)
    return df.astype('int32')


def get_stats_as_html(data: pd.DataFrame, group_name: str = None, group_title: str = None) -> str:
    if group_name:
        # This extra logic is to move a CategoricalIndex to a column.
        index_df = data.index.to_frame(index=False)
        data = data.reset_index(drop=True)
        data_out = pd.merge(index_df, data, left_index=True, right_index=True)
        data_out.rename(columns={group_name: group_title}, inplace=True)
    else:
        data_out = data.copy()
    data_out.drop(columns=['std'], inplace=True)
    data_out.rename(columns={'count': 'Nbr of Dogs', 'mean': 'Average', 'min': 'Min', 'max': 'Max'}, inplace=True)
    return data_out.to_html(table_id=f'{group_name}_stats_table', index=False, border=0,
                            classes="table table-striped table-hover")


def get_formatted_period(period: tuple) -> str:
    start_date = datetime.strftime(period[0], '%b %d, %Y')
    end_date = datetime.strftime(period[1], '%b %d, %Y')
    return f'{start_date} through {end_date}'


def lambda_handler(event, context):
    summary_df = hdb.dataframe_from_summary()
    period = hdb.get_summary_dates(summary_df)
    clean_summary_df = hdb.remove_zero_values(summary_df)
    clean_summary_df = hdb.group_by_age(clean_summary_df)
    clean_summary_df = hdb.group_by_weight(clean_summary_df)
    doc_stats = get_days_on_campus_stats(clean_summary_df)
    tp.write_to_s3(snippets_bucket, 'days_on_campus/days_on_campus_table.html', get_stats_as_html(doc_stats))

    # Days on Campus by Age
    doc_stats_by_age = get_days_on_campus_by_age_stats(clean_summary_df)
    tp.write_to_s3(snippets_bucket, 'days_on_campus/days_on_campus_by_age_table.html',
                   get_stats_as_html(doc_stats_by_age, 'age_group', 'Age Group'))

    # Days on Campus by Weight
    doc_stats_by_weight = get_days_on_campus_by_weight_stats(clean_summary_df)
    tp.write_to_s3(snippets_bucket, 'days_on_campus/days_on_campus_by_weight_table.html',
                   get_stats_as_html(doc_stats_by_weight, 'weight_group', 'Weight Group'))

    tp.write_to_s3(snippets_bucket, 'days_on_campus/report_period.html', get_formatted_period(period))
    return {
        'statusCode': 200,
        'body': json.dumps('Stats compiled and html pages generated.')
    }
