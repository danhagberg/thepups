import json
import logging
import os

import history_db as hdb
import the_pups as tp
# import plotly.figure_factory as pff
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as plo

folder_name = 'dogs_on_campus'
snippets_bucket = os.environ['SNIPPETS_BUCKET']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_chart_as_html(fig) -> str:
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def get_count_by_group_chart(counts_by_date: pd.DataFrame) -> str:
    area_by_group = [
        go.Scatter(x=counts_by_date.index, y=counts_by_date['DBS'], mode='lines', name='DBS', stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Staff'], mode='lines', name='Staff', stackgroup='all')
    ]
    group_layout = go.Layout(title=go.layout.Title(text='Dogs on Campus by Group - Stacked'), hovermode='x',
                             yaxis_title="Number of Dogs", xaxis_title="Date")
    fig = go.Figure(data=area_by_group, layout=group_layout)
    return fig


def get_count_by_staff_level_chart(counts_by_date: pd.DataFrame) -> str:
    area_by_level_staff = [
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Red - BQ'], mode='lines', name='Red - BQ',
                   marker_color='rgb(125,0,0)', stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Red'], mode='lines', name='Red',
                   marker_color='rgb(220,0,0)',
                   stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Red - Default'], mode='lines', name='Red - Default',
                   marker_color='plum', stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date.Orange, mode='lines', name='Orange', marker_color='Orange',
                   stackgroup='all'),
    ]
    level_layout_staff = go.Layout(title=go.layout.Title(text="Staff/BPA Dogs on Campus by Level - Stacked"),
                                   hovermode='x', yaxis_title="Number of Dogs", xaxis_title="Date")
    fig = go.Figure(data=area_by_level_staff, layout=level_layout_staff)
    return fig


def get_count_by_dbs_level_chart(counts_by_date: pd.DataFrame) -> str:
    area_by_dbs_level = [
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Red - Team'], mode='lines', name='Red - Team',
                   marker_color='rgb(175,0,0)', stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date.Purple, mode='lines', name='Purple', marker_color='Purple',
                   stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date.Blue, mode='lines', name='Blue', marker_color='Blue',
                   stackgroup='all'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date.Green, mode='lines', name='Green', marker_color='Green',
                   stackgroup='all')
    ]
    level_layout_dbs = go.Layout(title=go.layout.Title(text="DBS Dogs on Campus by Level - Stacked"), hovermode='x',
                                 yaxis_title="Number of Dogs", xaxis_title="Date")
    fig = go.Figure(data=area_by_dbs_level, layout=level_layout_dbs)
    return fig


def get_count_by_kc_chart(counts_by_date: pd.DataFrame) -> str:
    area_by_kc = [
        go.Scatter(x=counts_by_date.index, y=counts_by_date['KC'], mode='lines', name='Dogs with KC',
                   marker_color='Blue',
                   stackgroup='KC'),
        go.Scatter(x=counts_by_date.index, y=counts_by_date['Nbr of Dogs'], mode='lines', name='Dogs on Campus',
                   marker_color='Orange', stackgroup='Dogs')
    ]
    kc_layout = go.Layout(title=go.layout.Title(text='Dogs on Campus with Kennel Cough'), hovermode='x',
                          yaxis_title="Number of Dogs", xaxis_title="Date")
    fig = go.Figure(data=area_by_kc, layout=kc_layout)
    return fig


def lambda_handler(event, context):
    dog_history_df = hdb.dataframe_from_history()
    period = hdb.get_history_dates(dog_history_df)
    counts_by_date_df = hdb.get_counts_by_date(dog_history_df)
    # count_stats_df = get_dog_count_stats(counts_by_date_df)

    chart = get_count_by_group_chart(counts_by_date_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_group_chart.html', get_chart_as_html(chart))

    chart = get_count_by_dbs_level_chart(counts_by_date_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_dbs_level_chart.html', get_chart_as_html(chart))

    chart = get_count_by_staff_level_chart(counts_by_date_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_staff_level_chart.html', get_chart_as_html(chart))

    chart = get_count_by_kc_chart(counts_by_date_df)
    tp.write_to_s3(snippets_bucket, f'{folder_name}/stats_by_kc_chart.html', get_chart_as_html(chart))

    return {
        'statusCode': 200,
        'body': json.dumps('Charts created and html pages generated.')
    }
