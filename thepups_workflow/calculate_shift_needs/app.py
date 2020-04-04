import json
import logging
import math
import os
from collections import namedtuple
from datetime import date, datetime, timedelta, time
from io import StringIO
from typing import Tuple

import pandas as pd
from botocore.exceptions import ClientError

import the_pups as thepups

SESSION_DURATION_SECS = 2100  # 35 minutes per dog
RED_TEAM_DOG_WEIGHT = 2.0
KENNEL_COUGH_WEIGHT = 0.5
GAA_CAPACITY_REDUCTION = 4

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DBS_capacity = namedtuple('DBS_capacity', ['green', 'blue', 'purple'])

snippets_bucket = os.environ['SNIPPETS_BUCKET']
uploads_bucket = os.environ['UPLOADS_BUCKET']
processed_bucket = os.environ['PROCESSED_DATA_BUCKET']


def transform_dog_counts(dog_counts_csv: str, num_days: int = 1) -> pd.DataFrame:
    dog_counts_io = StringIO(dog_counts_csv)
    dog_counts = pd.read_csv(dog_counts_io)
    dog_counts.set_index('Level', inplace=True)

    # Apply weights to dog counts as applicable.
    dog_counts['All'] = dog_counts.apply(lambda row: row['All'] + math.ceil(row['KC'] * KENNEL_COUGH_WEIGHT), axis=1)

    counts = pd.DataFrame(dog_counts.drop(['Holder', 'KC'], axis=1))
    counts = counts.transpose()

    counts.drop('Total', inplace=True, axis=1)

    counts = pd.concat([counts] * num_days)
    dates = [date.today() + timedelta(days=i) for i in range(num_days)]
    counts['Date'] = dates
    dc_df = prepare_dog_counts(counts)

    return dc_df


def prepare_dog_counts(dc_df):
    dc_df.fillna(0, inplace=True)
    if 'Green' not in dc_df.columns:
        dc_df['Green'] = 0
    if 'Blue' not in dc_df.columns:
        dc_df['Blue'] = 0
    if 'Purple' not in dc_df.columns:
        dc_df['Purple'] = 0
    if 'Red - Team' not in dc_df.columns:
        dc_df['Red - Team'] = 0
    dc_df['Total_DBS'] = dc_df['Green'] + dc_df['Blue'] + dc_df['Purple'] + dc_df['Red - Team']
    dc_df = dc_df.astype({'Date': 'datetime64[s]'})
    dc_df = dc_df.set_index('Date')
    dc_df.sort_index(inplace=True)
    return dc_df


def get_dog_counts(bucket, dog_counts_file) -> str:
    dog_counts_csv = thepups.read_from_s3(bucket, dog_counts_file)
    return dog_counts_csv


def get_shift_counts(bucket, shift_counts_file) -> pd.DataFrame:
    shift_counts_csv = thepups.read_from_s3(bucket, shift_counts_file)
    shift_counts_io = StringIO(shift_counts_csv)
    shift_counts_df = pd.read_csv(shift_counts_io, parse_dates=['Start', 'End'])
    return shift_counts_df


def get_shift_exceptions(bucket, shift_exceptions_file) -> dict:
    try:
        shift_exceptions_csv = thepups.read_from_s3(bucket, shift_exceptions_file)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchKey':
            return dict()
        else:
            raise

    shift_exceptions_io = StringIO(shift_exceptions_csv)
    shift_exceptions_df = pd.read_csv(shift_exceptions_io)
    shift_exceptions_df['StartTime'] = shift_exceptions_df.StartTime.apply(time.fromisoformat)
    shift_exceptions_df['EndTime'] = shift_exceptions_df.EndTime.apply(time.fromisoformat)
    shift_exceptions_dict = shift_exceptions_df.set_index(
        [shift_exceptions_df.DayOfWeek, shift_exceptions_df.StartTime, shift_exceptions_df.EndTime])[
        ['Green', 'Blue', 'Purple']].T.to_dict()
    return shift_exceptions_dict


def create_shift_key(row: pd.Series) -> tuple:
    day_of_week = row['Start'].dayofweek
    start_time = row['Start'].time()
    end_time = row['End'].time()
    return day_of_week, start_time, end_time


def apply_exceptions(shift_counts_df: pd.DataFrame, shift_exceptions_dict: dict) -> pd.DataFrame:
    def apply_exceptions_to_row(row: pd.Series):
        shift_key = row['ShiftKey']
        if shift_key in shift_exceptions_dict:
            modifiers = shift_exceptions_dict[shift_key]
            row['Green'] = row['Green'] + modifiers['Green']
            row['Blue'] = row['Blue'] + modifiers['Blue']
            row['Purple'] = row['Purple'] + modifiers['Purple']
        return row

    shift_counts_mod_df = shift_counts_df.copy()
    shift_counts_mod_df['ShiftKey'] = shift_counts_mod_df.apply(create_shift_key, axis=1)
    shift_counts_mod_df = shift_counts_mod_df.apply(apply_exceptions_to_row, axis=1)
    shift_counts_mod_df.drop(columns=['ShiftKey'], inplace=True)
    return shift_counts_mod_df


def combine_dog_and_shift_counts(dog_counts: pd.DataFrame, shift_counts: pd.DataFrame) -> pd.DataFrame:
    sc_flat = pd.DataFrame(shift_counts.to_records())
    dc_flat = pd.DataFrame(dog_counts.to_records())
    sc_flat['Date'] = sc_flat.Start.apply(lambda s: s.date())
    # sc_flat['Date'] = sc_flat.Start.apply(lambda s: date.fromtimestamp(s.timestamp()))
    sc_flat.Date = pd.to_datetime(sc_flat.Date)
    sc_dc = dc_flat.merge(sc_flat, left_on='Date', right_on='Date', suffixes=('_dogs', '_dbs'))
    return sc_dc


def reduce_capacity(capacity: pd.Series, pool: int) -> pd.Series:
    borrow = pool + 1
    while capacity.iloc[pool] < 0 and borrow < capacity.size:
        available = min(capacity.iloc[borrow], abs(capacity.iloc[pool]))
        if available > 0:
            capacity.iloc[pool] += available
            capacity.iloc[borrow] -= available
        borrow += 1
    return capacity


def calc_shift_coverage(row: pd.Series) -> tuple:
    '''
    Calculate the shift coverage for the current shift given the the number of DBS and the number of dogs on campus.
    :param row: Series containing data on number of DBS by type and dogs by type as well as the shift duration.
    :return: tuple of shift needs - (Green DBS, Blue DBS, Purple DBS)
    '''
    sessions = get_number_of_sessions(row['Start'], row['End'])

    common_idx = ['Green', 'Blue', 'Purple']
    dbs_keys = ['Green_dbs', 'Blue_dbs', 'Purple_dbs']
    dbs_c = row.loc[dbs_keys]
    dbs_c.index = common_idx
    dbs_c = dbs_c * sessions

    dog_keys = ['Green_dogs', 'Blue_dogs', 'Purple_dogs']
    dogs = row.loc[dog_keys]
    dogs.index = common_idx
    dogs['Purple'] = dogs['Purple'] + math.ceil(row['Red - Team'] * RED_TEAM_DOG_WEIGHT)

    dbs_n = dbs_c - dogs
    # If not enough blue capacity, subtract from purple capacity, if available
    dbs_n = reduce_capacity(dbs_n, 1)
    # If not enough green capacity, subtract from blue capacity, then purple, if available
    dbs_n = reduce_capacity(dbs_n, 0)

    return math.floor(dbs_n.Green / sessions), math.floor(dbs_n.Blue / sessions), math.floor(dbs_n.Purple / sessions)


# For covid-19
def calc_shift_coverage_during_closure(row: pd.Series) -> tuple:
    '''
    Calculate the shift coverage for the current shift given the the number of DBS and the number of dogs on campus.
    :param row: Series containing data on number of DBS by type and dogs by type as well as the shift duration.
    :return: tuple of shift needs - (Green DBS, Blue DBS, Purple DBS)
    '''
    sessions = get_number_of_sessions(row['Start'], row['End'])

    common_idx = ['Green', 'Blue', 'Purple']
    dbs_keys = ['Green_dbs', 'Blue_dbs', 'Purple_dbs']
    dbs_c = row.loc[dbs_keys]
    dbs_c.index = common_idx
    dbs_c = dbs_c * sessions

    dog_keys = ['Green_dogs', 'Blue_dogs', 'Purple_dogs']
    dogs = row.loc[dog_keys]
    dogs.index = common_idx
    dogs['Purple'] = dogs['Purple'] + math.ceil(row['Red - Team'] * RED_TEAM_DOG_WEIGHT)
    # dogs['Purple'] = dogs.sum()

    dbs_n = dbs_c - dogs
    # If not enough blue capacity, subtract from purple capacity, if available
    dbs_n = reduce_capacity(dbs_n, 1)
    # If not enough green capacity, subtract from blue capacity, then purple, if available
    dbs_n = reduce_capacity(dbs_n, 0)

    return 0, math.floor(dbs_n.Blue / sessions), math.floor(dbs_n.Purple / sessions)


def drop_covered_shifts(shift_needs_df: pd.DataFrame) -> pd.DataFrame:
    return shift_needs_df[
        (shift_needs_df['green_cov'] < 0) | (shift_needs_df['blue_cov'] < 0) | (shift_needs_df['purple_cov'] < 0)]


def get_needs_as_html(shift_needs_df: pd.DataFrame) -> str:
    return shift_needs_df.to_html(table_id='shift_needs_table', index=False, border=0,
                                  classes="table table-striped table-hover table-sm")


def get_all_shifts_covered_html():
    return '<div id="shift_coverage_all">All Shifts Covered</div>'


def shift_date_str(shift: Tuple[datetime, datetime]) -> str:
    return shift[0].strftime('%a %-m/%-d')


def shift_time_str(shift: Tuple[datetime, datetime]) -> str:
    return '{} - {}'.format(shift[0].strftime('%-I:%M'), shift[1].strftime('%-I:%M %p'))


def remove_positive(val: int) -> int:
    if val < 0:
        return val
    else:
        return 0


def format_shift_counts(shift_needs_df: pd.DataFrame) -> pd.DataFrame:
    a_df = pd.DataFrame(shift_needs_df.to_records(index=False))  # Flatten out multi index
    a_df = a_df[['Start', 'End', 'green_cov', 'blue_cov', 'purple_cov']]
    count_cols = ['green_cov', 'blue_cov', 'purple_cov']
    a_df['shift'] = a_df.apply(lambda row: (row['Start'], row['End']), axis=1)
    a_df['Date'] = a_df['shift'].apply(shift_date_str)
    a_df['Time'] = a_df['shift'].apply(shift_time_str)
    a_df['green_cov'] = a_df['green_cov'].apply(remove_positive)
    a_df['blue_cov'] = a_df['blue_cov'].apply(remove_positive)
    a_df['purple_cov'] = a_df['purple_cov'].apply(remove_positive)
    a_df[count_cols] = a_df[count_cols].apply(abs)
    # Drop unneeded columns and reorder
    a_out = a_df[['Date', 'Time', 'green_cov', 'blue_cov', 'purple_cov']]
    a_out.columns = ['Date', 'Time', 'Green', 'Blue', 'Purple']
    return a_out


def get_number_of_sessions(start: datetime, end: datetime) -> int:
    shift_dur = end - start
    sessions = shift_dur.seconds / SESSION_DURATION_SECS
    return sessions


def calc_coverage(sc_dc: pd.DataFrame) -> pd.DataFrame:
    sc_dc[['green_cov', 'blue_cov', 'purple_cov']] = sc_dc.apply(calc_shift_coverage, axis=1).apply(pd.Series)
    return sc_dc


# For covid-19
def calc_coverage_during_closure(sc_dc: pd.DataFrame) -> pd.DataFrame:
    sc_dc[['green_cov', 'blue_cov', 'purple_cov']] = \
        sc_dc.apply(calc_shift_coverage_during_closure, axis=1).apply(pd.Series)
    return sc_dc


def create_needs_output(needs_df):
    if needs_df.empty:
        needs_html = get_all_shifts_covered_html()
    else:
        formatted_needs_df = format_shift_counts(needs_df)
        needs_html = get_needs_as_html(formatted_needs_df)
    thepups.write_to_s3(snippets_bucket, 'dbs_shift_needs.html', needs_html)
    thepups.write_to_s3('the-pups-info-snippets', 'dbs_shift_needs_timestamp.html',
                        datetime.strftime(datetime.now(), '%A, %b %d, %Y at %I:%M %p '))


def calculate_needs(dog_counts_df, shift_counts_df, shift_exceptions_file):
    shift_exceptions = get_shift_exceptions(processed_bucket, shift_exceptions_file)
    shift_counts_df = apply_exceptions(shift_counts_df, shift_exceptions)
    sc_df = combine_dog_and_shift_counts(dog_counts_df, shift_counts_df)
    # For covid-19
    # coverage = calc_coverage(sc_df)
    coverage = calc_coverage_during_closure(sc_df)
    needs_df = drop_covered_shifts(coverage)
    return needs_df


def lambda_handler(event, context):
    dog_counts_file = 'current_dogs/dog-counts.csv'
    shift_counts_file = 'shift_counts/shift-counts.csv'
    shift_exceptions_file = 'dbs_exceptions/shift-exceptions.csv'

    dog_counts_csv = get_dog_counts(processed_bucket, dog_counts_file)
    dog_counts_df = transform_dog_counts(dog_counts_csv, 5)

    shift_counts_df = get_shift_counts(processed_bucket, shift_counts_file)
    dog_counts_range = dog_counts_df.index.min(), dog_counts_df.index.max()
    shift_range = shift_counts_df.Start.min(), shift_counts_df.Start.max()
    if thepups.is_within_or_overlap(shift_range, dog_counts_range):
        needs_df = calculate_needs(dog_counts_df, shift_counts_df, shift_exceptions_file)
        create_needs_output(needs_df)
    else:
        logger.warning(
            f'DBS schedule is not within shift need period. Shifts: {shift_range}, Needs: {dog_counts_range}')

    return {
        'statusCode': 200,
        'body': json.dumps(f'HTML snippets created and stored in {snippets_bucket}.')
    }
