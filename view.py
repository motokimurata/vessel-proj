import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from assets.database import db_session
from assets.models import Data



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

data = db_session.query(Data.Vessel,Data.Carrier,Data.Voyage,Data.Service,Data.Pod,Data.ETA,Data.Berthing,Data.timestamp).all()
header=['vessel','carrier','voyage No.','service','POD', 'ETA','Berthing','updatetime']
df = pd.DataFrame(data=data,columns=header)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    children=[
        html.H1("T4 lite dataset"),
        dcc.Dropdown(
            id='carrier-dropdown',
            options=[
                {'label': 'ONE',
                 'value': 'ONE'},
                {'label': 'SAS',
                 'value': 'SAS'},
                {'label': 'OOC',
                 'value': 'OOC'},
                {'label': 'WHL',
                 'value': 'WHL'},
                {'label': 'EVG',
                 'value': 'EVG'},
                {'label': 'CMA',
                 'value': 'CMA'},
                {'label': 'MSK',
                 'value': 'MSK'}
            ], 
            value= ['ONE', 'SAS', 'OOC', 'EVG','MSK','CMA','WHL'],
            multi=True
        ),
        html.Div(id='output-container', style={"margin": "5%"})
    ]
)



@app.callback(
    Output('output-container', 'children'),
    [Input('carrier-dropdown', 'value')])

def input_triggers_spinner(value):
    df_out=pd.DataFrame(columns=header)
    for cnt in range (len(value)):
        df_filtered = df[df["carrier"] == value[cnt]]
        df_out = pd.concat([df_out,df_filtered])
    output_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df_out.to_dict('records'),
        export_format='csv',
    )
    return output_table



if __name__ == '__main__':
    app.run_server(debug=True)
