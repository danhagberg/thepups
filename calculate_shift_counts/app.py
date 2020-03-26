import json
import os
import re
from datetime import date, datetime, timedelta
from io import StringIO
from typing import Tuple, List

import boto3
import numpy as np
import pandas as pd
import pytz

import the_pups as thepups

snippets_bucket = os.environ['SNIPPETS_BUCKET']
output_data_bucket = os.environ['OUTPUT_DATA_BUCKET']

shift_times = {
    1: (((7, 30), (10, 30)), ((13, 0), (16, 0)), ((16, 0), (18, 0))),
    2: (((7, 30), (10, 30)), ((13, 0), (16, 0)), ((16, 0), (18, 0))),
    3: (((7, 30), (10, 30)), ((13, 0), (16, 0)), ((16, 0), (18, 0))),
    4: (((7, 30), (10, 30)), ((13, 0), (16, 0)), ((16, 0), (19, 30))),
    5: (((7, 30), (10, 30)), ((13, 0), (16, 0)), ((16, 0), (19, 30))),
    6: (((8, 0), (11, 0)), ((16, 0), (19, 30))),
    7: (((7, 30), (10, 30)), ((15, 0), (18, 0)))
}


def etl_shift_schedule(shift_csv: str) -> pd.DataFrame:
    shift_csv_io = StringIO(shift_csv)
    schedule_df = pd.read_csv(shift_csv_io, header=[1], quoting=1)
    schedule_df = schedule_df[(schedule_df.Volunteer != 'Volunteer')]  # Remove repeated header rows
    schedule_df = schedule_df.fillna(method='ffill')
    schedule_df = schedule_df[(schedule_df.Volunteer != 'Open')]
    print(schedule_df)
    return schedule_df


def set_level_indicator_vars(schedule_df: pd.DataFrame) -> pd.DataFrame:
    schedule_df['Green'] = schedule_df.LEVEL.apply(lambda l: 'GREEN' in l.upper())
    schedule_df['Blue'] = schedule_df.LEVEL.apply(lambda l: 'BLUE' in l.upper())
    schedule_df['Purple'] = schedule_df.LEVEL.apply(lambda l: 'PURPLE' in l.upper())
    print(schedule_df)
    return schedule_df


def transform_dates(schedule_df: pd.DataFrame) -> pd.DataFrame:
    schedule_df['Begin'] = schedule_df.apply(lambda l: re.sub(' \(.*\)', '', l['Date']) + ' ' + l['From'], axis=1)
    schedule_df['Start_Date'] = pd.to_datetime(schedule_df['Begin'], infer_datetime_format=True)
    schedule_df['End'] = schedule_df.apply(lambda l: re.sub(' \(.*\)', '', l['Date']) + ' ' + l['To'], axis=1)
    schedule_df['End_Date'] = pd.to_datetime(schedule_df['End'], infer_datetime_format=True)
    schedule_df = schedule_df.drop(['Begin', 'From', 'End'], axis=1)
    return schedule_df


def get_dbs_shift_counts(schedule_df: pd.DataFrame) -> pd.DataFrame:
    shifts_minimal = schedule_df[['Start_Date', 'End_Date', 'Green', 'Blue', 'Purple']]
    shift_counts = shifts_minimal.groupby(['Start_Date', 'End_Date']).sum()
    return shift_counts


def get_shift_counts_as_html(shift_counts_df: pd.DataFrame) -> str:
    return shift_counts_df.to_html(table_id='shift_counts_table', index=False, border=0,
                                   classes="table table-striped table-hover table-sm")


def format_shift_counts(assigned: pd.DataFrame) -> pd.DataFrame:
    a_df = pd.DataFrame(assigned.to_records())  # Flatten out multi index
    a_df['Date'] = a_df['shift'].apply(shift_date_str)
    a_df['Time'] = a_df['shift'].apply(shift_time_str)
    # Drop unneeded columns and reorder
    num_cols = ['Green', 'Blue', 'Purple']
    a_df[num_cols] = a_df[num_cols].applymap(np.int64)
    a_out = a_df[['Date', 'Time', 'Green', 'Blue', 'Purple']]
    return a_out


def load_and_summarize_dbs_counts(file_name: str) -> pd.DataFrame:
    shifts_df = etl_shift_schedule(file_name)
    shifts_df = set_level_indicator_vars(shifts_df)
    shifts_df = transform_dates(shifts_df)
    return get_dbs_shift_counts(shifts_df)


def save_shift_counts_as_html(shift_counts_df: pd.DataFrame, output_file: str):
    html_text = get_shift_counts_as_html(shift_counts_df)
    with open(output_file, 'w') as html_out:
        html_out.write(html_text)


def save_shift_counts_as_csv(shift_counts_df: pd.DataFrame, output_file: str):
    a_df = pd.DataFrame(shift_counts_df.to_records())  # Flatten out multi index
    a_df['Start'] = a_df['shift'].apply(lambda s: s[0])
    a_df['End'] = a_df['shift'].apply(lambda s: s[1])
    a_df = a_df[['Start', 'End', 'Green', 'Blue', 'Purple']]
    a_df.to_csv(output_file, index=False)


def get_shift_schedule(for_date: date, start: tuple, end: tuple) -> tuple:
    hour, minute = start
    start_shift = datetime(for_date.year, for_date.month, for_date.day, hour, minute)
    hour, minute = end
    end_shift = datetime(for_date.year, for_date.month, for_date.day, hour, minute)
    return start_shift, end_shift


def generate_schedule(start_date: date, num_of_days=14) -> List[tuple]:
    schedule = list()
    for day in range(num_of_days):
        curr_date = start_date + timedelta(day)
        shifts = shift_times[curr_date.isoweekday()]
        for shift in shifts:
            schedule.append(get_shift_schedule(curr_date, shift[0], shift[1]))
    return schedule


def is_within_timeframe(timeframe: Tuple[datetime, datetime], time: datetime):
    return timeframe[0] <= time <= timeframe[1]


def is_within_or_overlap(timeframe: Tuple[datetime, datetime], shift: Tuple[datetime, datetime]):
    return is_within_timeframe(timeframe, shift[0]) or is_within_timeframe(timeframe, shift[1])


def get_shift_overlap(timeframe: Tuple[datetime, datetime], shift: Tuple[datetime, datetime]) -> float:
    if not is_within_or_overlap(timeframe, shift):
        return 0.0

    shift_start, shift_end = shift
    tf_start, tf_end = timeframe
    in_start = max(shift_start, tf_start)
    in_end = min(shift_end, tf_end)
    tf_duration = tf_end - tf_start
    in_duration = in_end - in_start
    overlap = in_duration / tf_duration
    return overlap


def shift_date_str(shift: Tuple[datetime, datetime]) -> str:
    return shift[0].strftime('%a %-m/%-d')


def shift_time_str(shift: Tuple[datetime, datetime]) -> str:
    return '{} - {}'.format(shift[0].strftime('%-I:%M'), shift[1].strftime('%-I:%M %p'))


def assign_dbs_to_shift(shift_counts_df: pd.DataFrame, schedule: dict):
    # Create datafame for standard shifts
    assigned_counts = shift_counts_df.reset_index()
    assigned_counts['shift'] = assigned_counts.apply(
        lambda row: get_shift((row['Start_Date'], row['End_Date']), schedule), axis=1)
    assigned_counts = assigned_counts.groupby(['shift']).sum()
    return assigned_counts


def get_shift(shift_time: tuple, schedule: list) -> tuple:
    for slot in schedule:
        if get_shift_overlap(shift_time, slot) >= .5:
            return slot
    else:
        return None


def get_schedule(shift_counts: pd.DataFrame) -> List[tuple]:
    start = shift_counts.index[0][0]
    end = shift_counts.index[-1][0]
    num_days = (end - start).days + 1
    return generate_schedule(start, num_days)


def write_as_csv_to_s3(bucket: str, file_name: str, assigned_df: pd.DataFrame):
    all_assigned = pd.DataFrame(assigned_df.to_records())
    # print(all_assigned)
    all_assigned['Start'] = all_assigned['shift'].apply(lambda s: s[0])
    all_assigned['End'] = all_assigned['shift'].apply(lambda s: s[1])
    all_assigned.drop(columns=['shift'], inplace=True, axis=1)
    all_assigned = all_assigned.astype(
        {'Start': 'datetime64[m]', 'End': 'datetime64[m]', 'Green': int, 'Blue': int, 'Purple': int})
    all_assigned = all_assigned[['Start', 'End', 'Green', 'Blue', 'Purple']]
    all_assigned = all_assigned.set_index('Start')
    output = StringIO()
    all_assigned.to_csv(output)
    thepups.write_to_s3(bucket, file_name, output.getvalue())


def zero_out_dbs_levels(shift_counts: pd.DataFrame, levels: list) -> pd.DataFrame:
    shift_counts[levels] = 0
    return shift_counts


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    s3 = boto3.resource('s3')
    print(f'Generating shift counts for: {bucket}:{file}')
    dbs_report = s3.Object(bucket, file)
    dbs_report_csv = dbs_report.get()['Body'].read().decode('utf-8')
    shift_counts_df = load_and_summarize_dbs_counts(dbs_report_csv)
    schedule = get_schedule(shift_counts_df)
    dbs_assigned = assign_dbs_to_shift(shift_counts_df, schedule)
    # Temporary during Covid-19 shutdown
    dbs_assigned = zero_out_dbs_levels(dbs_assigned, ['Green'])
    # End of temp code
    dbs_assigned_fmt = format_shift_counts(dbs_assigned)
    report_time = datetime.now(tz=pytz.timezone('US/Pacific'))

    thepups.write_to_s3(snippets_bucket, 'dbs_shift_counts_timestamp.html',
                        datetime.strftime(report_time, '%A, %b %d, %Y at %I:%M %p '))
    thepups.write_to_s3(snippets_bucket, 'dbs_shift_counts.html', get_shift_counts_as_html(dbs_assigned_fmt))
    write_as_csv_to_s3(output_data_bucket, 'shift_counts/shift-counts.csv', dbs_assigned)
    print(f'Saved formatted html for shift counts in the-pups-info-snippets')

    return {
        'statusCode': 200,
        'body': json.dumps(
            f'HTML snippets created and stored in {snippets_bucket}. Data output to {output_data_bucket}')
    }
