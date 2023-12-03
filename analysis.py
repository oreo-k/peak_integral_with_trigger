import dash
from dash import Dash, dash_table, dcc, html, Input, Output, State, callback, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import datetime as dt
import json
import os
import sys
import re
import time



# Load data
# ------------------------------------------------------------------------------
## sample dataの作成
wafer_list = {
    "starttime": ["2023-11-11 11:11:11", "2023-11-12 12:12:12", "2023-11-13 13:13:13"],
    "endtime": ["2023-11-11 11:11:11", "2023-11-12 12:22:12", "2023-11-13 13:33:13"],
    "pjid": [0, 1, 2],
    "slot": [10, 11, 12]
}
# ------------------------------------------------------------------------------
nr_data_list = {
    "starttime": ["2023-11-11 11:21:11", "2023-11-12 12:12:12", "2023-11-13 13:13:13"],
    "endtime": ["2023-11-11 11:21:11", "2023-11-12 12:22:12", "2023-11-13 13:33:13"],
    "filename": ["1st", "2nd", "3rd"]
}
# ------------------------------------------------------------------------------

## wafer listをDataFrameに変換
df_data = pd.DataFrame(wafer_list)
df_data["starttime"]=pd.to_datetime(df_data["starttime"])
df_data["endtime"]=pd.to_datetime(df_data["endtime"])

app = dash.Dash(__name__)

# レイアウトを定義
app.layout = html.Div([
    html.Div("Start Time"), # Start Time
    dcc.DatePickerSingle(
        id='start-date-picker',
        display_format='YYYY-MM-DD',
        date=dt.date.today()
    ),
    dcc.Input(
        id='start-time-input',
        type='text',
        value='00:00',
        placeholder='HH:MM'  # プレースホルダーを設定
    ),
    html.Br(style={'margin-bottom': '10px'}),

    html.Div("End Time"), # End Time
    dcc.DatePickerSingle(
        id='end-date-picker',
        display_format='YYYY-MM-DD',
        date=dt.date.today()
    ),
    dcc.Input(
        id='end-time-input',
        type='text',
        value='23:59',
        placeholder='HH:MM'  # プレースホルダーを設定
    ),

    html.Br(style={'margin-bottom': '10px'}),
    html.Div(id='output-time-range'),

    dash_table.DataTable(
        id='wafer_list_table',
        columns=[
            {'name': 'starttime', 'id': 'starttime'},
            {'name': 'endtime', 'id': 'endtime'},
            {'name': 'pjid', 'id': 'pjid'},
            {'name': 'slot', 'id': 'slot'},
        ],
        data=df_data.to_dict('records'),
        row_selectable='multi',  # 複数行選択を有効にします,
        filter_action="native",
        selected_rows=[],  # 初期選択は空です
    ),

    dcc.Graph(id='selected-wafers-graph')
    ])

# コールバックを定義
## callback for time range
# 開始日時と終了日時を更新します
@app.callback(
    Output('output-time-range', 'children'),
    Input('start-date-picker', 'date'),
    Input('start-time-input', 'value'),
    Input('end-date-picker', 'date'),
    Input('end-time-input', 'value')
)
def update_output(start_date_input, start_time_input, end_date_input, end_time_input):
    try:
        # 日付と時刻を結合してdatetime型に変換します
        start_date = dt.datetime.strptime(start_date_input, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date_input, "%Y-%m-%d").date()

        # 時刻をdatetime型に変換します
        start_time = dt.datetime.strptime(start_time_input, '%H:%M').time()
        end_time = dt.datetime.strptime(end_time_input, '%H:%M').time()

        # 日付と時刻を結合してdatetime型に変換します
        start_datetime = dt.datetime.combine(start_date, start_time)
        end_datetime = dt.datetime.combine(end_date, end_time)
    except ValueError:
        start_datetime = None
        end_datetime = None

    time_range = {"start_datetime": start_datetime, "end_datetime": end_datetime}

    if start_datetime and end_datetime:
        return f"{time_range}"
    else:
        return 'Invalid time format. Please use HH:MM format.'


## callback for time range
# 選択したstarttime とend timeに基づいてwafer listを更新します
@app.callback(
    Output('date-filtered-wafer-list', 'data'),
    Input('output-time-range', 'children')
)
def update_wafer_list(time_range):

    df_date_filtered_data = df_data[(df_data["starttime"] >= time_range["start_datetime"]) & (df_data["endtime"] <= time_range["end_datetime"])]

    if not time_range:
        return df_date_filtered_data.to_dict('records')
        







## callback for wafer list table
# 選択された行に基づいてグラフを更新します
@app.callback(
    Output('selected-wafers-graph', 'figure'),
    Input('wafer_list_table', 'selected_rows')
)
def update_graph(selected_rows):
    if not selected_rows:
        return px.scatter()  # 選択がない場合、空のグラフを返します
    df_selected = df_data.iloc[selected_rows]  # 選択された行を抽出します

    # 選択された行に基づいてグラフを作成します（ここでは散布図を使用）
    fig = px.scatter(df_selected,
        x='starttime',
        y='slot',
        labels={
            'starttime': 'starttime',
            'slot': 'slot'
        }
        )
    return fig

# main function
if __name__ == '__main__':
    app.run_server(debug=True)