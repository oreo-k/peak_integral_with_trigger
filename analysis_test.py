import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import datetime as dt


import pandas as pd

app = dash.Dash(__name__)

# Load data
# ------------------------------------------------------------------------------
## sample dataの作成
wafer_list = {
    "datetime": ["2023-11-11 11:11:11", "2023-11-12 12:12:12", "2023-11-13 13:13:13"],
    "pjid": [0, 1, 2],
    "slot": [10, 11, 12]
}
# ------------------------------------------------------------------------------
nr_data_list = {
    "datetime": ["2023-11-11 11:11:11", "2023-11-12 12:12:12", "2023-11-13 13:13:13"],
    "filename": ["1st", "2nd", "3rd"]
}
# ------------------------------------------------------------------------------


df_data = pd.DataFrame(wafer_list)
df_data["datetime"]=pd.to_datetime(df_data["datetime"])




app.layout = html.Div([
    dcc.DatePickerSingle(
        id='date-picker',
        display_format='YYYY-MM-DD',
        date=dt.date.today()
    ),
    dcc.Slider(
        id='hour-slider',
        min=0,
        max=23,
        step=1,
        value=12,
        marks={i: str(i) for i in range(24)}
    ),
    dcc.Input(
        id='manual-time-input',
        type='text',
        value='12:00'
    ),
    html.Div(id='output-date-time'),
    dash_table.DataTable(
        id='wafer_list_table',
        columns=[
            {'name': 'datetime', 'id': 'datetime'},
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
@app.callback(
    Output('output-date-time', 'children'),
    Input('date-picker', 'date'),
    Input('hour-slider', 'value'),
    Input('manual-time-input', 'value')
)
def update_output(date, hour_slider, manual_time_input):
    try:
        time_parts = manual_time_input.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
    except ValueError:
        hour = 0
        minute = 0

    selected_datetime = dt.datetime.strptime(date, '%Y-%m-%d').replace(hour=hour, minute=minute)
    return f'Selected Date and Time: {selected_datetime}'

@app.callback(
    Output('selected-wafers-graph', 'figure'),
    Input('wafer_list_table', 'selected_rows')
)
def update_graph(selected_rows):
    if not selected_rows:
        return px.scatter()  # 選択がない場合、空のグラフを返します

    df_selected = df_data.iloc[selected_rows]  # 選択された行を抽出します

    # 選択された行に基づいてグラフを作成します（ここでは散布図を使用）
    fig = px.scatter(df_selected, x='datetime', y='slot', labels={'Name': 'Name', 'Salary': 'Salary'})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host="127.0.0.1", port=8051)

