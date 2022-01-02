import dash
import dash_table
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from assets.database import db_session
from assets.models import Data
from datetime import datetime as dt
from datetime import timedelta as td    
from dateutil.parser import parse
import plotly.graph_objects as go

data = db_session.query(Data.Vessel,Data.Carrier,Data.Voyage,Data.Service,Data.Pod,Data.ETA,Data.Berthing,Data.timestamp+td(hours=9)).all()
header=['Vessel','Carrier','Voyage No.','Service','POD', 'ETA','Berthing','UpdateTime']
df = pd.DataFrame(data=data,columns=header)
db_session.close()
for i in range(len(df['Berthing'])): #Berthing列を文字列から日付型へ変更
    try:
        df['Berthing'][i] = parse(df['Berthing'][i])
    except:
        df['Berthing'][i] = np.nan

for i in range(len(df['UpdateTime'])): #UpdateTime列を文字列から日付型へ変更
    try:
        df['UpdateTime'][i] = parse(df['UpdateTime'][i].replace('T',' '))
    except:
        df['UpdateTime'][i] = np.nan

df = df.dropna(axis=0,subset=['UpdateTime']) #UpdatetimeがNaNの行を削除
df = df.sort_values(['Carrier','Service','POD','Voyage No.','Vessel','UpdateTime'],ascending=[True,True,True,True,True,True]).reset_index(drop=True)
df1 = df.drop(columns = ['ETA','UpdateTime'],inplace=False) #日付列を削除して新たなdfを生成
df1.drop_duplicates(subset=['Vessel','Carrier','Voyage No.','Service','POD'],inplace=True,ignore_index=True,keep='first') #上で日付古い順にソートしているので重複を削除すると一番古いBerthingを保持
df1.rename(columns={'Berthing':'Berthing_first'},inplace=True) #'Berthing'の列名を'Berthing_first'へ変更
df2 = df.drop(columns = ['ETA'],inplace=False) #日付列を削除して新たなdfを生成
df2.drop_duplicates(subset=['Vessel','Carrier','Voyage No.','Service','POD'],inplace=True,ignore_index=True,keep='last') #上で日付古い順にソートしているので重複を削除すると一番新しいBerthingとUpdatetimeを保持
df2.rename(columns={'Berthing':'Berthing_last'},inplace=True) #'Berthing'の列名を'Berthing_last'へ変更
df1= pd.merge(df1,df2,on=['Vessel','Carrier','Voyage No.','Service','POD'],how='left')
df1 = df1.dropna(axis=0,subset=['Berthing_first', 'Berthing_last']) #Berthing_firstもしくはBerthing_lastがNaNの行を削除
df1 = df1.reset_index(drop=True)

delta_days=[] #最初のBerthingと最近のBerthingの差を算出
for i in range(len(df1['Berthing_last'])+1):
    try:
        delta= df1['Berthing_last'][i].date() - df1['Berthing_first'][i].date()
        delta_days.append(delta.days)
    except:
        delta_days.append(np.nan)

year_month=[] #最初のBerthingから計上月を産出
for i in range(len(df1['Berthing_first'])+1):
    try:
        berthing_year_month= df1['Berthing_first'][i].strftime('%Y/%m')
        year_month.append(berthing_year_month)
    except:
        year_month.append(np.nan)

df_delta_days=pd.DataFrame(delta_days,columns=['delta_days'])
df_year_month = pd.DataFrame(year_month,columns=['year_month'])
df1= df1.assign(delta_days = df_delta_days,year_month=df_year_month)

pd.set_option('display.max_rows', None)
df_summary = df1.groupby(['Carrier','POD','Service','year_month'])['delta_days'].agg([min,max,np.mean,"count"]).reset_index()
new_row = df_summary['Carrier'].str.cat(df_summary['Service'], sep='_').str.cat(df_summary['POD'], sep='_')
df_summary.insert(3,'Carrier_Service_POD',new_row)

year_month_unique = df_summary['year_month'].unique()
df_date = pd.DataFrame(data=year_month_unique,columns=['year_month_unique']).sort_values('year_month_unique',ascending=True).reset_index(drop=True)
dict_date = df_date.to_dict()
dict_date_swap = {v: k for k, v in dict_date['year_month_unique'].items()}
df_summary_rev = df_summary.replace(dict_date_swap)
year_month_unique_index = df_summary_rev['year_month'].unique()

target1 = df_summary[(df_summary['Carrier'] == 'EVG')&(df_summary['Service'] == 'NSA')]
evg_x1 = target1['year_month'][target1['POD'] == 'OBE']
evg_y1 = target1['mean'][target1['POD'] == 'OBE']
min_err_evg_y1= target1['mean'][target1['POD'] == 'OBE']-target1['min'][target1['POD'] == 'OBE']
max_err_evg_y1= target1['max'][target1['POD'] == 'OBE']-target1['mean'][target1['POD'] == 'OBE']

evg_x2 = target1['year_month'][target1['POD'] == 'TYO']
evg_y2 = target1['mean'][target1['POD'] == 'TYO']
min_err_evg_y2= target1['mean'][target1['POD'] == 'TYO']-target1['min'][target1['POD'] == 'TYO']
max_err_evg_y2= target1['max'][target1['POD'] == 'TYO']-target1['mean'][target1['POD'] == 'TYO']

evg_x3 = target1['year_month'][target1['POD'] == 'OSA']
evg_y3 = target1['mean'][target1['POD'] == 'OSA']
min_err_evg_y3= target1['mean'][target1['POD'] == 'OSA']-target1['min'][target1['POD'] == 'OSA']
max_err_evg_y3= target1['max'][target1['POD'] == 'OSA']-target1['mean'][target1['POD'] == 'OSA']

evg_x4 = target1['year_month'][target1['POD'] == 'YKO']
evg_y4 = target1['mean'][target1['POD'] == 'YKO']
min_err_evg_y4= target1['mean'][target1['POD'] == 'YKO']-target1['min'][target1['POD'] == 'YKO']
max_err_evg_y4= target1['max'][target1['POD'] == 'YKO']-target1['mean'][target1['POD'] == 'YKO']

target2 = df_summary[(df_summary['Carrier'] == 'OOC')&(df_summary['Service'] == 'KTX1')]
ooc_x1 = target2['year_month'][target2['POD'] == 'OBE']
ooc_y1 = target2['mean'][target2['POD'] == 'OBE']
min_err_ooc_y1= target2['mean'][target2['POD'] == 'OBE']-target2['min'][target2['POD'] == 'OBE']
max_err_ooc_y1= target2['max'][target2['POD'] == 'OBE']-target2['mean'][target2['POD'] == 'OBE']

ooc_x2 = target2['year_month'][target2['POD'] == 'TYO']
ooc_y2 = target2['mean'][target2['POD'] == 'TYO']
min_err_ooc_y2= target2['mean'][target2['POD'] == 'TYO']-target2['min'][target2['POD'] == 'TYO']
max_err_ooc_y2= target2['max'][target2['POD'] == 'TYO']-target2['mean'][target2['POD'] == 'TYO']

ooc_x3 = target2['year_month'][target2['POD'] == 'OSA']
ooc_y3 = target2['mean'][target2['POD'] == 'OSA']
min_err_ooc_y3= target2['mean'][target2['POD'] == 'OSA']-target2['min'][target2['POD'] == 'OSA']
max_err_ooc_y3= target2['max'][target2['POD'] == 'OSA']-target2['mean'][target2['POD'] == 'OSA']

ooc_x4 = target2['year_month'][target2['POD'] == 'YKO']
ooc_y4 = target2['mean'][target2['POD'] == 'YKO']
min_err_ooc_y4= target2['mean'][target2['POD'] == 'YKO']-target2['min'][target2['POD'] == 'YKO']
max_err_ooc_y4= target2['max'][target2['POD'] == 'YKO']-target2['mean'][target2['POD'] == 'YKO']

target3 = df_summary[(df_summary['Carrier'] == 'TSL')&(df_summary['Service'] == 'JTK')]
tsl_x1 = target3['year_month'][target3['POD'] == 'OBE']
tsl_y1 = target3['mean'][target3['POD'] == 'OBE']
min_err_tsl_y1= target3['mean'][target3['POD'] == 'OBE']-target3['min'][target3['POD'] == 'OBE']
max_err_tsl_y1= target3['max'][target3['POD'] == 'OBE']-target3['mean'][target3['POD'] == 'OBE']

tsl_x2 = target3['year_month'][target3['POD'] == 'TYO']
tsl_y2 = target3['mean'][target3['POD'] == 'TYO']
min_err_tsl_y2= target3['mean'][target3['POD'] == 'TYO']-target3['min'][target3['POD'] == 'TYO']
max_err_tsl_y2= target3['max'][target3['POD'] == 'TYO']-target3['mean'][target3['POD'] == 'TYO']

tsl_x3 = target3['year_month'][target3['POD'] == 'OSA']
tsl_y3 = target3['mean'][target3['POD'] == 'OSA']
min_err_tsl_y3= target3['mean'][target3['POD'] == 'OSA']-target3['min'][target3['POD'] == 'OSA']
max_err_tsl_y3= target3['max'][target3['POD'] == 'OSA']-target3['mean'][target3['POD'] == 'OSA']

tsl_x4 = target3['year_month'][target3['POD'] == 'YKO']
tsl_y4 = target3['mean'][target3['POD'] == 'YKO']
min_err_tsl_y4= target3['mean'][target3['POD'] == 'YKO']-target3['min'][target3['POD'] == 'YKO']
max_err_tsl_y4= target3['max'][target3['POD'] == 'YKO']-target3['mean'][target3['POD'] == 'YKO']

### グラフの色 ###

#船会社別のマーカーと線の色
evgcolor = '#00AE95'
ooclcolor = '#2905E6'
tslcolor = '#E6D205'

#共通の色
errbarcolor = '#5D5D63' #エラーバー
mkrcolor = '#FFFFFB' #マーカーの中
graphbgcolor = '#E6E7E8' #グラフの背景
bgcolor = '#FFFFFB' #背景の色

fig_evg_nsa_obe = go.Figure(data=go.Scatter(
        x=evg_x1,
        y=evg_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg_y1,
            arrayminus=min_err_evg_y1,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= evgcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= evgcolor),
        line=dict(
            width=5,
            color= evgcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:KOBE',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_evg_nsa_tyo = go.Figure(data=go.Scatter(
        x=evg_x2,
        y=evg_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg_y2,
            arrayminus=min_err_evg_y2,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= evgcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= evgcolor),
        line=dict(
            width=5,
            color= evgcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:TOKYO',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_evg_nsa_osa = go.Figure(data=go.Scatter(
        x=evg_x3,
        y=evg_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg_y3,
            arrayminus=min_err_evg_y3,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= evgcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= evgcolor),
        line=dict(
            width=5,
            color= evgcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:OSAKA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_evg_nsa_yko = go.Figure(data=go.Scatter(
        x=evg_x4,
        y=evg_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg_y4,
            arrayminus=min_err_evg_y4,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= evgcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= evgcolor),
        line=dict(
            width=5,
            color= evgcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:YOKOHAMA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_ooc_ktx1_obe = go.Figure(data=go.Scatter(
        x=ooc_x1,
        y=ooc_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc_y1,
            arrayminus=min_err_ooc_y1,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= ooclcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= ooclcolor),
        line=dict(
            width=5,
            color= ooclcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:KOBE',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_ooc_ktx1_tyo = go.Figure(data=go.Scatter(
        x=ooc_x2,
        y=ooc_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc_y2,
            arrayminus=min_err_ooc_y2,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= ooclcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= ooclcolor),
        line=dict(
            width=5,
            color= ooclcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:TOKYO',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_ooc_ktx1_osa = go.Figure(data=go.Scatter(
        x=ooc_x3,
        y=ooc_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc_y3,
            arrayminus=min_err_ooc_y3,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= ooclcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= ooclcolor),
        line=dict(
            width=5,
            color= ooclcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:OSAKA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_ooc_ktx1_yko = go.Figure(data=go.Scatter(
        x=ooc_x4,
        y=ooc_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc_y4,
            arrayminus=min_err_ooc_y4,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= ooclcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= ooclcolor),
        line=dict(
            width=5,
            color= ooclcolor), 
        ),
        layout=dict( #ダミーレイアウト
            plot_bgcolor= bgcolor,
            paper_bgcolor= bgcolor,
            title='',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month',
                color= bgcolor
                ),
            yaxis=dict(
                title='Average delay days',
                color= bgcolor))
            
    )


fig_tsl_jtk_obe = go.Figure(data=go.Scatter(
        x=tsl_x1,
        y=tsl_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl_y1,
            arrayminus=min_err_tsl_y1,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= tslcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= tslcolor),
        line=dict(
            width=5,
            color= tslcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:KOBE',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_tsl_jtk_tyo = go.Figure(data=go.Scatter(
        x=tsl_x2,
        y=tsl_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl_y2,
            arrayminus=min_err_tsl_y2,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= tslcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= tslcolor),
        line=dict(
            width=5,
            color= tslcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:TOKYO',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_tsl_jtk_osa = go.Figure(data=go.Scatter(
        x=tsl_x3,
        y=tsl_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl_y3,
            arrayminus=min_err_tsl_y3,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= tslcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= tslcolor),
        line=dict(
            width=5,
            color= tslcolor), 
        ),
        layout=dict(
            plot_bgcolor= graphbgcolor,
            paper_bgcolor= bgcolor,
            title='Pod:OSAKA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_tsl_jtk_yko = go.Figure(data=go.Scatter(
        x=tsl_x4,
        y=tsl_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl_y4,
            arrayminus=min_err_tsl_y4,
            width=3,
            color= errbarcolor),
        marker=dict(
            color= mkrcolor,
            size=10,
            line=dict(
                width=5,
                color= tslcolor),
            opacity=1.0),
        mode='markers+lines+text',
        textposition='top right',
        texttemplate='%{y:.1f}',
        textfont=dict(
            size=15,
            color= tslcolor),
        line=dict(
            width=5,
            color= tslcolor), 
        ),
        layout=dict( #ダミーレイアウト
            plot_bgcolor= bgcolor,
            paper_bgcolor= bgcolor,
            title='',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month',
                color= bgcolor
                ),
            yaxis=dict(
                title='Average delay days',
                color= bgcolor))
            
    )

VALID_USERNAME_PASSWORD_PAIRS = {
    'Motoki Murata': '2022'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
tabs_styles = {
    'height': '44px'
}
tab_style1 = {
    'borderTop': '2px solid #FFFFFF',
    'borderBottom': '2px solid #FFFFFF',
    'borderLeft': '2px solid #FFFFFF',
    'borderRight': '2px solid #FFFFFF',
    'color': '#696969',
    'backgroundColor': '#FFFFFF',
    'padding': '6px',
    'fontSize': 28
}

tab_selected_style1 = {
    'borderTop': '2px solid #FFFFFF',
    'borderBottom': '4px solid #7b68ee',
    'borderLeft': '2px solid #FFFFFF',
    'borderRight': '2px solid #FFFFFF',
    'fontWeight': 'bold',
    'color': '#7b68ee',
    'padding': '6px',
    'fontSize': 28
}



tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#F5F5F5',
    'color': '#696969',
    'padding': '6px',
    'fontSize': 20
}

tab_selected_style = {
    'borderTop': '2px solid #696969',
    'fontWeight': 'bold',
    'color': '#696969',
    'padding': '6px',
    'fontSize': 20
}

app.layout =  html.Div([
        html.H1(children='    Vessel Delay Report',
        style={
            'color': '#696969', 
            'fontSize': 40,
            'textAlign': 'left',
            'background-color': '#f5f5f5',
            'fontWeight': 'bold',
            'padding': '0.2em 0.5em 0.2em 0.5em'}
            ),
        html.Div([
        dcc.Tabs(id='tabs-example1', value='tab-a', 
        children=[
        dcc.Tab(
            label='Graph', 
            value='tab-a', 
            style=tab_style1, 
            selected_style=tab_selected_style1
        ),
        dcc.Tab(
            label='Download', 
            value='tab-b', 
            style=tab_style1, 
            selected_style=tab_selected_style1      
        )
            ],
            style={
            'display': 'block',
            'margin': '-1em 0 0 0',
            'padding':'0 75em 4em 0',   
            })
        ]),
        html.Div(id='tabs-example-content-a')
])


@app.callback(
    Output('tabs-example-content-a', 'children'),
    [Input('tabs-example1', 'value')])
def render_content(tab):
    if tab == 'tab-a':
        return html.Div([
        dcc.Tabs(id='tabs-example', value='tab-1', 
        children=[
        dcc.Tab(
            label='EVG', 
            value='tab-1', 
            style=tab_style, 
            selected_style=tab_selected_style
        ),
        dcc.Tab(
            label='OOCL', 
            value='tab-2', 
            style=tab_style, 
            selected_style=tab_selected_style
        ),
        dcc.Tab(
            label='TSL', 
            value='tab-3', 
            style=tab_style, 
            selected_style=tab_selected_style
        ),
        ],
        style={
            'margin': '2em 0 0 0',         
            }
        ),
        html.Div(id='tabs-example-content-1')
        ])

    elif tab == 'tab-b':
        return html.Div(
        children=[
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
                    {'label': 'TSL',
                    'value': 'TSL'}    
                ], 
                style={
                'margin': '2em 0 0 0',         
                },
                value= ['OOC', 'EVG','SAS','TSL','WHL','ONE'],
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
        df_filtered = df[df["Carrier"] == value[cnt]]
        df_out = pd.concat([df_out,df_filtered])
    output_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df_out.to_dict('records'),
        filter_action='native',
        export_format='csv',
    )
    return output_table


@app.callback(
    Output('tabs-example-content-1', 'children'),
    [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
                html.H3(children='Service: NSA',
                style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': evgcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}),
                html.Div([
                dcc.Graph(
                    id='evg_nsa_obe',
                    figure=fig_evg_nsa_obe
                ),

                dcc.Graph(
                    id='evg-nsa-osa',
                    figure=fig_evg_nsa_osa     
                )
            ],
            style={'columnCount':2})
        ])

    elif tab == 'tab-2':
        return html.Div([
            html.H3(children='Service: KTX1',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': ooclcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}),
        html.Div([
        dcc.Graph(
            id='ooc_ktx1_obe',
            figure=fig_ooc_ktx1_obe
        ),

        dcc.Graph(
            id='ooc_ktx1_tyo',
            figure=fig_ooc_ktx1_tyo
        ),

        dcc.Graph(
            id='ooc_ktx1_osa',
            figure=fig_ooc_ktx1_osa
        ),

        dcc.Graph(
            id='ooc_ktx1_yko',
            figure=fig_ooc_ktx1_yko
        )
        ],
        style={'columnCount':2})
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3(children='Service: JTK',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': tslcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}),
        html.Div([
        dcc.Graph(
            id='tsl_jtx_obe',
            figure= fig_tsl_jtk_obe
        ),

        dcc.Graph(
            id='tsl_jtx_tyo',
            figure= fig_tsl_jtk_tyo
        ),

        dcc.Graph(
            id='tsl_jtx_osa',
            figure=fig_tsl_jtk_osa
        ),

        dcc.Graph(
            id='tsl_jtx_yko',
            figure=fig_tsl_jtk_yko
        )
        ],
        style={'columnCount':2})
        ])

if __name__ == '__main__':
    app.run_server(debug=True)