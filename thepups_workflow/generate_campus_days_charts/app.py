import json
import logging
import os

import history_db as hdb
import the_pups as tp
# import plotly.figure_factory as pff
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as plo

snippets_bucket = os.environ['SNIPPETS_BUCKET']
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_chart_as_html(fig) -> str:
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def get_days_on_campus_age_weight_heatmap(clean_summary_df: pd.DataFrame, period: tuple) -> str:
    data = go.Heatmap(x=clean_summary_df.age_group, y=clean_summary_df.weight_group, z=clean_summary_df.days_on_campus)
    layout = go.Layout(title='Days on Campus')
    fig = go.Figure(data=data, layout=layout)
    return plo.plot(fig, output_type='div')


def get_days_on_campus_chart(clean_summary_df: pd.DataFrame, group: str, x: str, period: tuple,
                             chart_title: str) -> str:
    cats = clean_summary_df[group].unique().sort_values().to_list()
    traces = []
    for cat in cats:
        sub = clean_summary_df.loc[clean_summary_df[group] == cat]
        traces.append(go.Scatter(x=sub[x],
                                 y=sub['days_on_campus'],
                                 mode='markers',
                                 hovertext=sub['name'],
                                 hoverinfo='x+y+text',
                                 name=cat,
                                 text=['name']))  # hover text goes here

    layout = go.Layout(title_text=f'Total Days on Campus by {chart_title} from {period[0]} to {period[1]}', bargap=0.2,
                       yaxis_title='Cumulative Days on Campus', xaxis_title=chart_title)
    fig = go.Figure(data=traces, layout=layout)
    return plo.plot(fig, output_type='div')


def lambda_handler(event, context):
    summary_df = hdb.dataframe_from_summary()
    period = hdb.get_history_dates(summary_df)
    clean_summary_df = hdb.remove_zero_values(summary_df)
    clean_summary_df = hdb.group_by_age(clean_summary_df)
    clean_summary_df = hdb.group_by_weight(clean_summary_df)

    # Days on Campus by Age
    doc_chart_by_age = get_days_on_campus_chart(clean_summary_df, 'age_group', 'age', period, 'Age')
    tp.write_to_s3(snippets_bucket, 'days_on_campus/days_on_campus_by_age_chart.html', doc_chart_by_age)

    # Days on Campus by Weight
    doc_chart_by_weight = get_days_on_campus_chart(clean_summary_df, 'weight_group', 'weight', period, 'Weight')
    tp.write_to_s3(snippets_bucket, 'days_on_campus/days_on_campus_by_weight_chart.html', doc_chart_by_weight)

    return {
        'statusCode': 200,
        'body': json.dumps('Charts created and html pages generated.')
    }
