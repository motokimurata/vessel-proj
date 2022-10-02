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
import dash_auth
from users import USERNAME_PASSWORD_PAIRS

#以下コードを記す。
data = db_session.query(Data.Vessel,Data.Carrier,Data.Voyage,Data.Service,Data.Pod,Data.ETA,Data.Berthing,Data.timestamp+td(hours=9)).all()
#data = pd.read_csv('assets/vessel_schedule.csv')
header=['船名','Carrier','Voyage No.','サービス','POD', 'ETA','Berthing','UpdateTime']
df_origin = pd.DataFrame(data=data,columns=header)
df = pd.DataFrame(data=data,columns=header)
db_session.close()
for i in range(len(df['Berthing'])): #Berthing列を文字列から日付型へ変更
    try:
        df.loc[i,'Berthing'] = parse(df['Berthing'][i])
    except:
        df.loc[i,'Berthing'] = np.nan

for i in range(len(df['UpdateTime'])): #UpdateTime列を文字列から日付型へ変更
    try:
        df.loc[i,'UpdateTime'] = parse(df['UpdateTime'][i].replace('T',' '))
    except:
        df.loc[i,'UpdateTime'] = np.nan

df.dropna(axis=0,subset=['UpdateTime']).copy() #UpdatetimeがNaNの行を削除
df.sort_values(['Carrier','サービス','POD','Voyage No.','船名','UpdateTime'],ascending=[True,True,True,True,True,True]).reset_index(drop=True).copy()
df1 = df.drop(columns = ['ETA','UpdateTime'],inplace=False).copy() #日付列を削除して新たなdfを生成
df1.drop_duplicates(subset=['船名','Carrier','Voyage No.','サービス','POD'],inplace=True,ignore_index=True,keep='first') #上で日付古い順にソートしているので重複を削除すると一番古いBerthingを保持
df1.rename(columns={'Berthing':'Berthing_first'},inplace=True) #'Berthing'の列名を'Berthing_first'へ変更
df2 = df.drop(columns = ['ETA'],inplace=False).copy() #日付列を削除して新たなdfを生成
df2.drop_duplicates(subset=['船名','Carrier','Voyage No.','サービス','POD'],inplace=True,ignore_index=True,keep='last') #上で日付古い順にソートしているので重複を削除すると一番新しいBerthingとUpdatetimeを保持
df2.rename(columns={'Berthing':'Berthing_last'},inplace=True) #'Berthing'の列名を'Berthing_last'へ変更
df1= pd.merge(df1,df2,on=['船名','Carrier','Voyage No.','サービス','POD'],how='left').copy()
df1.dropna(axis=0,subset=['Berthing_first', 'Berthing_last']) #Berthing_firstもしくはBerthing_lastがNaNの行を削除
df1.reset_index(drop=True)

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
df_summary = df1.groupby(['Carrier','POD','サービス','year_month'])['delta_days'].agg([min,max,np.mean,"count"]).reset_index()
new_row = df_summary['Carrier'].str.cat(df_summary['サービス'], sep='_').str.cat(df_summary['POD'], sep='_')
df_summary.insert(3,'Carrier_サービス_POD',new_row)

year_month_unique = df_summary['year_month'].unique()
df_date = pd.DataFrame(data=year_month_unique,columns=['year_month_unique']).sort_values('year_month_unique',ascending=True).reset_index(drop=True)
dict_date = df_date.to_dict()
dict_date_swap = {v: k for k, v in dict_date['year_month_unique'].items()}
df_summary_rev = df_summary.replace(dict_date_swap)
year_month_unique_index = df_summary_rev['year_month'].unique()

target1 = df_summary[(df_summary['Carrier'] == 'EVG')&(df_summary['サービス'] == 'NSA')]
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

evg_x4 = target1['year_month'][target1['POD'] == 'YOK']
evg_y4 = target1['mean'][target1['POD'] == 'YOK']
min_err_evg_y4= target1['mean'][target1['POD'] == 'YOK']-target1['min'][target1['POD'] == 'YOK']
max_err_evg_y4= target1['max'][target1['POD'] == 'YOK']-target1['mean'][target1['POD'] == 'YOK']

target5 = df_summary[(df_summary['Carrier'] == 'EVG')&(df_summary['サービス'] == 'NSC')]
evg2_x1 = target5['year_month'][target5['POD'] == 'OBE']
evg2_y1 = target5['mean'][target5['POD'] == 'OBE']
min_err_evg2_y1= target5['mean'][target5['POD'] == 'OBE']-target5['min'][target5['POD'] == 'OBE']
max_err_evg2_y1= target5['max'][target5['POD'] == 'OBE']-target5['mean'][target5['POD'] == 'OBE']

evg2_x2 = target5['year_month'][target5['POD'] == 'TYO']
evg2_y2 = target5['mean'][target5['POD'] == 'TYO']
min_err_evg2_y2= target5['mean'][target5['POD'] == 'TYO']-target5['min'][target5['POD'] == 'TYO']
max_err_evg2_y2= target5['max'][target5['POD'] == 'TYO']-target5['mean'][target5['POD'] == 'TYO']

evg2_x3 = target5['year_month'][target5['POD'] == 'OSA']
evg2_y3 = target5['mean'][target5['POD'] == 'OSA']
min_err_evg2_y3= target5['mean'][target5['POD'] == 'OSA']-target5['min'][target5['POD'] == 'OSA']
max_err_evg2_y3= target5['max'][target5['POD'] == 'OSA']-target5['mean'][target5['POD'] == 'OSA']

evg2_x4 = target5['year_month'][target5['POD'] == 'YOK']
evg2_y4 = target5['mean'][target5['POD'] == 'YOK']
min_err_evg2_y4= target5['mean'][target5['POD'] == 'YOK']-target5['min'][target5['POD'] == 'YOK']
max_err_evg2_y4= target5['max'][target5['POD'] == 'YOK']-target5['mean'][target5['POD'] == 'YOK']

target6 = df_summary[(df_summary['Carrier'] == 'EVG')&(df_summary['サービス'] == 'NSD')]
evg3_x1 = target6['year_month'][target6['POD'] == 'OBE']
evg3_y1 = target6['mean'][target6['POD'] == 'OBE']
min_err_evg3_y1= target6['mean'][target6['POD'] == 'OBE']-target6['min'][target6['POD'] == 'OBE']
max_err_evg3_y1= target6['max'][target6['POD'] == 'OBE']-target6['mean'][target6['POD'] == 'OBE']

evg3_x2 = target6['year_month'][target6['POD'] == 'TYO']
evg3_y2 = target6['mean'][target6['POD'] == 'TYO']
min_err_evg3_y2= target6['mean'][target6['POD'] == 'TYO']-target6['min'][target6['POD'] == 'TYO']
max_err_evg3_y2= target6['max'][target6['POD'] == 'TYO']-target6['mean'][target6['POD'] == 'TYO']

evg3_x3 = target6['year_month'][target6['POD'] == 'OSA']
evg3_y3 = target6['mean'][target6['POD'] == 'OSA']
min_err_evg3_y3= target6['mean'][target6['POD'] == 'OSA']-target6['min'][target6['POD'] == 'OSA']
max_err_evg3_y3= target6['max'][target6['POD'] == 'OSA']-target6['mean'][target6['POD'] == 'OSA']

evg3_x4 = target6['year_month'][target6['POD'] == 'YOK']
evg3_y4 = target6['mean'][target6['POD'] == 'YOK']
min_err_evg3_y4= target6['mean'][target6['POD'] == 'YOK']-target6['min'][target6['POD'] == 'YOK']
max_err_evg3_y4= target6['max'][target6['POD'] == 'YOK']-target6['mean'][target6['POD'] == 'YOK']

target2 = df_summary[(df_summary['Carrier'] == 'OOC')&(df_summary['サービス'] == 'KTX1')]
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

ooc_x4 = target2['year_month'][target2['POD'] == 'YOK']
ooc_y4 = target2['mean'][target2['POD'] == 'YOK']
min_err_ooc_y4= target2['mean'][target2['POD'] == 'YOK']-target2['min'][target2['POD'] == 'YOK']
max_err_ooc_y4= target2['max'][target2['POD'] == 'YOK']-target2['mean'][target2['POD'] == 'YOK']

target7 = df_summary[(df_summary['Carrier'] == 'OOC')&(df_summary['サービス'] == 'KTX2')]
ooc2_x1 = target7['year_month'][target7['POD'] == 'OBE']
ooc2_y1 = target7['mean'][target7['POD'] == 'OBE']
min_err_ooc2_y1= target7['mean'][target7['POD'] == 'OBE']-target7['min'][target7['POD'] == 'OBE']
max_err_ooc2_y1= target7['max'][target7['POD'] == 'OBE']-target7['mean'][target7['POD'] == 'OBE']

ooc2_x2 = target7['year_month'][target7['POD'] == 'TYO']
ooc2_y2 = target7['mean'][target7['POD'] == 'TYO']
min_err_ooc2_y2= target7['mean'][target7['POD'] == 'TYO']-target7['min'][target7['POD'] == 'TYO']
max_err_ooc2_y2= target7['max'][target7['POD'] == 'TYO']-target7['mean'][target7['POD'] == 'TYO']

ooc2_x3 = target7['year_month'][target7['POD'] == 'OSA']
ooc2_y3 = target7['mean'][target7['POD'] == 'OSA']
min_err_ooc2_y3= target7['mean'][target7['POD'] == 'OSA']-target7['min'][target7['POD'] == 'OSA']
max_err_ooc2_y3= target7['max'][target7['POD'] == 'OSA']-target7['mean'][target7['POD'] == 'OSA']

ooc2_x4 = target7['year_month'][target7['POD'] == 'YOK']
ooc2_y4 = target7['mean'][target7['POD'] == 'YOK']
min_err_ooc2_y4= target7['mean'][target7['POD'] == 'YOK']-target7['min'][target7['POD'] == 'YOK']
max_err_ooc2_y4= target7['max'][target7['POD'] == 'YOK']-target7['mean'][target7['POD'] == 'YOK']

target8 = df_summary[(df_summary['Carrier'] == 'OOC')&(df_summary['サービス'] == 'KTX6')]
ooc3_x1 = target8['year_month'][target8['POD'] == 'OBE']
ooc3_y1 = target8['mean'][target8['POD'] == 'OBE']
min_err_ooc3_y1= target8['mean'][target8['POD'] == 'OBE']-target8['min'][target8['POD'] == 'OBE']
max_err_ooc3_y1= target8['max'][target8['POD'] == 'OBE']-target8['mean'][target8['POD'] == 'OBE']

ooc3_x2 = target8['year_month'][target8['POD'] == 'TYO']
ooc3_y2 = target8['mean'][target8['POD'] == 'TYO']
min_err_ooc3_y2= target8['mean'][target8['POD'] == 'TYO']-target8['min'][target8['POD'] == 'TYO']
max_err_ooc3_y2= target8['max'][target8['POD'] == 'TYO']-target8['mean'][target8['POD'] == 'TYO']

ooc3_x3 = target8['year_month'][target8['POD'] == 'OSA']
ooc3_y3 = target8['mean'][target8['POD'] == 'OSA']
min_err_ooc3_y3= target8['mean'][target8['POD'] == 'OSA']-target8['min'][target8['POD'] == 'OSA']
max_err_ooc3_y3= target8['max'][target8['POD'] == 'OSA']-target8['mean'][target8['POD'] == 'OSA']

ooc3_x4 = target8['year_month'][target8['POD'] == 'YOK']
ooc3_y4 = target8['mean'][target8['POD'] == 'YOK']
min_err_ooc3_y4= target8['mean'][target8['POD'] == 'YOK']-target8['min'][target8['POD'] == 'YOK']
max_err_ooc3_y4= target8['max'][target8['POD'] == 'YOK']-target8['mean'][target8['POD'] == 'YOK']

target9 = df_summary[(df_summary['Carrier'] == 'OOC')&(df_summary['サービス'] == 'KTX3')]
ooc6_x1 = target9['year_month'][target9['POD'] == 'OBE']
ooc6_y1 = target9['mean'][target9['POD'] == 'OBE']
min_err_ooc6_y1= target9['mean'][target9['POD'] == 'OBE']-target9['min'][target9['POD'] == 'OBE']
max_err_ooc6_y1= target9['max'][target9['POD'] == 'OBE']-target9['mean'][target9['POD'] == 'OBE']

ooc6_x2 = target9['year_month'][target9['POD'] == 'TYO']
ooc6_y2 = target9['mean'][target9['POD'] == 'TYO']
min_err_ooc6_y2= target9['mean'][target9['POD'] == 'TYO']-target9['min'][target9['POD'] == 'TYO']
max_err_ooc6_y2= target9['max'][target9['POD'] == 'TYO']-target9['mean'][target9['POD'] == 'TYO']

ooc6_x3 = target9['year_month'][target9['POD'] == 'OSA']
ooc6_y3 = target9['mean'][target9['POD'] == 'OSA']
min_err_ooc6_y3= target9['mean'][target9['POD'] == 'OSA']-target9['min'][target9['POD'] == 'OSA']
max_err_ooc6_y3= target9['max'][target9['POD'] == 'OSA']-target9['mean'][target9['POD'] == 'OSA']

ooc6_x4 = target9['year_month'][target9['POD'] == 'YOK']
ooc6_y4 = target9['mean'][target9['POD'] == 'YOK']
min_err_ooc6_y4= target9['mean'][target9['POD'] == 'YOK']-target9['min'][target9['POD'] == 'YOK']
max_err_ooc6_y4= target9['max'][target9['POD'] == 'YOK']-target9['mean'][target9['POD'] == 'YOK']

target3 = df_summary[(df_summary['Carrier'] == 'TSL')&(df_summary['サービス'] == 'JTK')]
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

tsl_x4 = target3['year_month'][target3['POD'] == 'YOK']
tsl_y4 = target3['mean'][target3['POD'] == 'YOK']
min_err_tsl_y4= target3['mean'][target3['POD'] == 'YOK']-target3['min'][target3['POD'] == 'YOK']
max_err_tsl_y4= target3['max'][target3['POD'] == 'YOK']-target3['mean'][target3['POD'] == 'YOK']

target4 = df_summary[(df_summary['Carrier'] == 'TSL')&(df_summary['サービス'] == 'JTK2')]
tsl2_x1 = target4['year_month'][target4['POD'] == 'OBE']
tsl2_y1 = target4['mean'][target4['POD'] == 'OBE']
min_err_tsl2_y1= target4['mean'][target4['POD'] == 'OBE']-target4['min'][target4['POD'] == 'OBE']
max_err_tsl2_y1= target4['max'][target4['POD'] == 'OBE']-target4['mean'][target4['POD'] == 'OBE']

tsl2_x2 = target4['year_month'][target4['POD'] == 'TYO']
tsl2_y2 = target4['mean'][target4['POD'] == 'TYO']
min_err_tsl2_y2= target4['mean'][target4['POD'] == 'TYO']-target4['min'][target4['POD'] == 'TYO']
max_err_tsl2_y2= target4['max'][target4['POD'] == 'TYO']-target4['mean'][target4['POD'] == 'TYO']

tsl2_x3 = target4['year_month'][target4['POD'] == 'OSA']
tsl2_y3 = target4['mean'][target4['POD'] == 'OSA']
min_err_tsl2_y3= target4['mean'][target4['POD'] == 'OSA']-target4['min'][target4['POD'] == 'OSA']
max_err_tsl2_y3= target4['max'][target4['POD'] == 'OSA']-target4['mean'][target4['POD'] == 'OSA']

tsl2_x4 = target4['year_month'][target4['POD'] == 'YOK']
tsl2_y4 = target4['mean'][target4['POD'] == 'YOK']
min_err_tsl2_y4= target4['mean'][target4['POD'] == 'YOK']-target4['min'][target4['POD'] == 'YOK']
max_err_tsl2_y4= target4['max'][target4['POD'] == 'YOK']-target4['mean'][target4['POD'] == 'YOK']


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

fig_evg_nsa_yok = go.Figure(data=go.Scatter(
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

fig_evg_nsc_obe = go.Figure(data=go.Scatter(
        x=evg2_x1,
        y=evg2_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg2_y1,
            arrayminus=min_err_evg2_y1,
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

fig_evg_nsc_tyo = go.Figure(data=go.Scatter(
        x=evg2_x2,
        y=evg2_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg2_y2,
            arrayminus=min_err_evg2_y2,
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

fig_evg_nsc_osa = go.Figure(data=go.Scatter(
        x=evg2_x3,
        y=evg2_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg2_y3,
            arrayminus=min_err_evg2_y3,
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

fig_evg_nsc_yok = go.Figure(data=go.Scatter(
        x=evg2_x4,
        y=evg2_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg2_y4,
            arrayminus=min_err_evg2_y4,
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

fig_evg_nsd_obe = go.Figure(data=go.Scatter(
        x=evg3_x1,
        y=evg3_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg3_y1,
            arrayminus=min_err_evg3_y1,
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

fig_evg_nsd_tyo = go.Figure(data=go.Scatter(
        x=evg3_x2,
        y=evg3_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg3_y2,
            arrayminus=min_err_evg3_y2,
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

fig_evg_nsd_osa = go.Figure(data=go.Scatter(
        x=evg3_x3,
        y=evg3_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg3_y3,
            arrayminus=min_err_evg3_y3,
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

fig_evg_nsd_yok = go.Figure(data=go.Scatter(
        x=evg3_x4,
        y=evg3_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_evg3_y4,
            arrayminus=min_err_evg3_y4,
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

fig_ooc_ktx1_yok = go.Figure(data=go.Scatter(
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

fig_ooc_ktx2_obe = go.Figure(data=go.Scatter(
        x=ooc2_x1,
        y=ooc2_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc2_y1,
            arrayminus=min_err_ooc2_y1,
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

fig_ooc_ktx2_tyo = go.Figure(data=go.Scatter(
        x=ooc2_x2,
        y=ooc2_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc2_y2,
            arrayminus=min_err_ooc2_y2,
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

fig_ooc_ktx2_osa = go.Figure(data=go.Scatter(
        x=ooc2_x3,
        y=ooc2_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc2_y3,
            arrayminus=min_err_ooc2_y3,
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

fig_ooc_ktx2_yok = go.Figure(data=go.Scatter(
        x=ooc2_x4,
        y=ooc2_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc2_y4,
            arrayminus=min_err_ooc2_y4,
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
            title='Pod:YOKOHAMA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )
fig_ooc_ktx3_obe = go.Figure(data=go.Scatter(
        x=ooc3_x1,
        y=ooc3_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc3_y1,
            arrayminus=min_err_ooc3_y1,
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

fig_ooc_ktx3_tyo = go.Figure(data=go.Scatter(
        x=ooc3_x2,
        y=ooc3_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc3_y2,
            arrayminus=min_err_ooc3_y2,
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

fig_ooc_ktx3_osa = go.Figure(data=go.Scatter(
        x=ooc3_x3,
        y=ooc3_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc3_y3,
            arrayminus=min_err_ooc3_y3,
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

fig_ooc_ktx3_yok = go.Figure(data=go.Scatter(
        x=ooc3_x4,
        y=ooc3_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc3_y4,
            arrayminus=min_err_ooc3_y4,
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
            title='Pod:YOKOHAMA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

fig_ooc_ktx6_obe = go.Figure(data=go.Scatter(
        x=ooc6_x1,
        y=ooc6_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc6_y1,
            arrayminus=min_err_ooc6_y1,
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

fig_ooc_ktx6_tyo = go.Figure(data=go.Scatter(
        x=ooc6_x2,
        y=ooc6_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc6_y2,
            arrayminus=min_err_ooc6_y2,
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

fig_ooc_ktx6_osa = go.Figure(data=go.Scatter(
        x=ooc6_x3,
        y=ooc6_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc6_y3,
            arrayminus=min_err_ooc6_y3,
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

fig_ooc_ktx6_yok = go.Figure(data=go.Scatter(
        x=ooc6_x4,
        y=ooc6_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_ooc6_y4,
            arrayminus=min_err_ooc6_y4,
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
            title='Pod:YOKOHAMA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
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

fig_tsl_jtk_yok = go.Figure(data=go.Scatter(
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
fig_tsl_jtk2_obe = go.Figure(data=go.Scatter(
        x=tsl2_x1,
        y=tsl2_y1,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl2_y1,
            arrayminus=min_err_tsl2_y1,
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

fig_tsl_jtk2_tyo = go.Figure(data=go.Scatter(
        x=tsl2_x2,
        y=tsl2_y2,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl2_y2,
            arrayminus=min_err_tsl2_y2,
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

fig_tsl_jtk2_osa = go.Figure(data=go.Scatter(
        x=tsl2_x3,
        y=tsl2_y3,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl2_y3,
            arrayminus=min_err_tsl2_y3,
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

fig_tsl_jtk2_yok = go.Figure(data=go.Scatter(
        x=tsl2_x4,
        y=tsl2_y4,
        error_y=dict(
            type='data',
            symmetric=False,
            array=max_err_tsl2_y4,
            arrayminus=min_err_tsl2_y4,
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
            title='Pod:YOKOHAMA',
            title_x=.5,
            xaxis=dict(
                showgrid=True,
                title='Original Berthing month'
                ),
            yaxis=dict(
                title='Average delay days'))
            
    )

#VALID_USERNAME_PASSWORD_PAIRS = {
#    'Motoki Murata': '2022'
#}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    USERNAME_PASSWORD_PAIRS
)

server = app.server

tabs_styles = {
    'height': '44px'
}

tab_style2 = {
    'borderTop': '2px solid #FFFEF6',
    'borderBottom': '2px solid #FFFEF6',
    'borderLeft': '2px solid #FFFEF6',
    'borderRight': '2px solid #FFFEF6',
    'color': '#696969',
    'background-color': '#FFFFFF',
    'padding': '0px',
    'fontSize': 16
}

tab_selected_style2 = {
    'borderTop': '2px solid #FFFFFF',
    'borderBottom': '4px solid #7b68ee',
    'borderLeft': '0.05px solid #FFFFFF',
    'borderRight': '0.05px solid #FFFFFF',
    'fontWeight': 'bold',
    'color': '#7b68ee',
    'background-color': '#FFFFFF',
    'padding': '0px',
    'fontSize': 16
}

tab_style1 = {
    'borderTop': '2px solid #FFFEF6',
    'borderBottom': '2px solid #FFFEF6',
    'borderLeft': '2px solid #FFFEF6',
    'borderRight': '2px solid #FFFEF6',
    'color': '#696969',
    'background-color': '#FFFEF6',
    'padding': '0px',
    'fontSize': 16
}

tab_selected_style1 = {
    'borderTop': '2px solid #FFFEF6',
    'borderBottom': '4px solid #7b68ee',
    'borderLeft': '0.05px solid #FFFEF6',
    'borderRight': '0.05px solid #FFFEF6',
    'fontWeight': 'bold',
    'color': '#7b68ee',
    'background-color': '#FFFEF6',
    'padding': '0px',
    'fontSize': 16
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#FFFFFF',
    'color': '#696969',
    'padding': '6px',
    'fontSize': 18
}

tab_selected_style = {
    'borderTop': '2px solid #696969',
    'fontWeight': 'bold',
    'color': '#696969',
    'background-color': '#FFFFFF',
    'padding': '6px',
    'fontSize': 18
}

app.layout =  html.Div([
        html.H1(children='    船名 Delay Report',
        style={
            'color': '#FFFFFF', 
            'borderTop': '1px solid #d6d6d6',
            'fontSize': 32,
            'textAlign': 'center',
            'background-color': '#7b68ee',
            'fontWeight': 'bold',
            'margin': '0 0 -1em 0',
            'padding': '0.2em 0.5em 0.5em 0.5em'}
            ),
        html.Div([
        dcc.Tabs(id='tabs-example1', value='tab-a', 
        children=[
        dcc.Tab(
            label='Graph', 
            value='tab-a', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='Download', 
            value='tab-b', 
            style=tab_style2, 
            selected_style=tab_selected_style2     
        )
            ],
            style={
            'display': 'block',
            'margin': '1em 0 0 0',
            'padding':'0 80% 0.05em 0',   
            'background-color': '#FFFFFF',
            'borderBottom': '1px solid #d6d6d6',
            })
        ]),
        html.Div(id='tabs-example-content-a')
])

div_style = {
    "width" : "50%",
    "display":"inline-block"
}

evg_top_center = html.Div(
    [
        html.H3(children='Service: NSA',
                style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': evgcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'})
        
    ]
)

evg2_top_center = html.Div(
    [
        html.H3(children='Service: NSC',
                style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': evgcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'})
        
    ]
)

evg3_top_center = html.Div(
    [
        html.H3(children='Service: NSD',
                style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': evgcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'})
        
    ]
)


ooc_top_center = html.Div(
    [
        html.H3(children='Service: KTX1',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': ooclcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}) 
    ]
)

ooc2_top_center = html.Div(
    [
        html.H3(children='Service: KTX2',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': ooclcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}) 
    ]
)

ooc3_top_center = html.Div(
    [
        html.H3(children='Service: KTX3',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': ooclcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}) 
    ]
)

ooc6_top_center = html.Div(
    [
        html.H3(children='Service: KTX6',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': ooclcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'}) 
    ]
)

tsl_top_center = html.Div(
    [
        html.H3(children='Service: JTK',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': tslcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'})
    ]
)

tsl2_top_center = html.Div(
    [
        html.H3(children='Service: JTK2',
            style={
                'color': mkrcolor, 
                'display': 'inline-block',
                'fontSize': 24,
                'textAlign': 'center',
                'background-color': tslcolor,
                'fontWeight': 'bold',
                'margin' : '1em 0 0 1em',
                'padding': '0.2em 0.5em 0.2em 0.5em'})
    ]
)
evg_top_left = html.Div(
    [
        dcc.Graph(
                    id='evg_nsa_obe',
                    figure=fig_evg_nsa_obe
                )
    ],
    style=div_style,
)

evg_top_right = html.Div(
    [
        dcc.Graph(
                    id='evg-nsa-osa',
                    figure=fig_evg_nsa_osa 
                )
    ],
    style=div_style,
)

evg2_top_left = html.Div(
    [
        dcc.Graph(
                    id='evg_nsc_obe',
                    figure=fig_evg_nsc_obe
                )
    ],
    style=div_style,
)

evg2_top_right = html.Div(
    [
        dcc.Graph(
                    id='evg-nsc-osa',
                    figure=fig_evg_nsc_osa 
                )
    ],
    style=div_style,
)

evg2_bottom_left = html.Div(
    [
        dcc.Graph(
                    id='evg_nsc_obe',
                    figure=fig_evg_nsc_tyo
                )
    ],
    style=div_style,
)

evg2_bottom_right = html.Div(
    [
        dcc.Graph(
                    id='evg-nsc-osa',
                    figure=fig_evg_nsc_yok 
                )
    ],
    style=div_style,
)

evg3_top_left = html.Div(
    [
        dcc.Graph(
                    id='evg_nsd_obe',
                    figure=fig_evg_nsd_obe
                )
    ],
    style=div_style,
)

evg3_top_right = html.Div(
    [
        dcc.Graph(
                    id='evg-nsd-osa',
                    figure=fig_evg_nsd_osa 
                )
    ],
    style=div_style,
)

evg3_bottom_left = html.Div(
    [
        dcc.Graph(
                    id='evg_nsd_obe',
                    figure=fig_evg_nsd_tyo
                )
    ],
    style=div_style,
)

evg3_bottom_right = html.Div(
    [
        dcc.Graph(
                    id='evg-nsd-osa',
                    figure=fig_evg_nsd_yok 
                )
    ],
    style=div_style,
)

ooc_top_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx1_obe',
            figure=fig_ooc_ktx1_obe
        )
    ],
    style=div_style,
)

ooc_top_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx1_osa',
            figure=fig_ooc_ktx1_osa
        )
    ],
    style=div_style,
)

ooc_bottom_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx1_tyo',
            figure=fig_ooc_ktx1_tyo
        )
    ],
    style=div_style,
)

ooc_bottom_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx1_yok',
            figure=fig_ooc_ktx1_yok
        )
    ],
    style=div_style,
)

ooc2_top_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx2_obe',
            figure=fig_ooc_ktx2_obe
        )
    ],
    style=div_style,
)

ooc2_top_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx2_osa',
            figure=fig_ooc_ktx2_osa
        )
    ],
    style=div_style,
)

ooc2_bottom_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx2_tyo',
            figure=fig_ooc_ktx2_tyo
        )
    ],
    style=div_style,
)

ooc2_bottom_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx2_yok',
            figure=fig_ooc_ktx2_yok
        )
    ],
    style=div_style,
)

ooc3_top_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx3_obe',
            figure=fig_ooc_ktx3_obe
        )
    ],
    style=div_style,
)

ooc3_top_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx3_osa',
            figure=fig_ooc_ktx3_osa
        )
    ],
    style=div_style,
)

ooc3_bottom_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx3_tyo',
            figure=fig_ooc_ktx3_tyo
        )
    ],
    style=div_style,
)

ooc3_bottom_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx3_yok',
            figure=fig_ooc_ktx3_yok
        )
    ],
    style=div_style,
)

ooc6_top_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx6_obe',
            figure=fig_ooc_ktx6_obe
        )
    ],
    style=div_style,
)

ooc6_top_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx6_osa',
            figure=fig_ooc_ktx6_osa
        )
    ],
    style=div_style,
)

ooc6_bottom_left = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx6_tyo',
            figure=fig_ooc_ktx6_tyo
        )
    ],
    style=div_style,
)

ooc6_bottom_right = html.Div(
    [
        dcc.Graph(
            id='ooc_ktx6_yok',
            figure=fig_ooc_ktx6_yok
        )
    ],
    style=div_style,
)


tsl_top_left = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk_obe',
            figure= fig_tsl_jtk_obe
        )
    ],
    style=div_style,
)

tsl_top_right = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk_osa',
            figure=fig_tsl_jtk_osa
        )
    ],
    style=div_style,
)

tsl_bottom_left = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk_tyo',
            figure= fig_tsl_jtk_tyo
        )
    ],
    style=div_style,
)

tsl_bottom_right = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk_yok',
            figure=fig_tsl_jtk_yok
        )
    ],
    style=div_style,
)

tsl2_top_left = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk2_obe',
            figure= fig_tsl_jtk2_obe
        )
    ],
    style=div_style,
)

tsl2_top_right = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk2_osa',
            figure=fig_tsl_jtk2_osa
        )
    ],
    style=div_style,
)

tsl2_bottom_left = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk2_tyo',
            figure= fig_tsl_jtk2_tyo
        )
    ],
    style=div_style,
)

tsl2_bottom_right = html.Div(
    [
        dcc.Graph(
            id='tsl_jtk2_yok',
            figure=fig_tsl_jtk2_yok
        )
    ],
    style=div_style,
)


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
            'background-color' :'#FFFFFF',
            'display': 'block',
            'margin': '1em 0 0 0',
            'padding':'0 70% 0.05em 0',   
            #'borderBottom': '1px solid #d6d6d6',     
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
                'margin': '1em 0 0 0',         
                },
                value= ['OOC', 'EVG','SAS','TSL','WHL','ONE'],
                multi=True
            ),
            html.Div(id='output-container', style={'textAlign': 'center',"margin": "1%"})
        ] 
    )


@app.callback(
    Output('output-container', 'children'),
    [Input('carrier-dropdown', 'value')])
def input_triggers_spinner(value):
    df_out=pd.DataFrame(columns=header)
    for cnt in range (len(value)):
        df_filtered = df_origin[df["Carrier"] == value[cnt]]
        df_out = pd.concat([df_out,df_filtered])
    output_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        # リスト表示にします
        #style_as_list_view=True,
        data=df_out.to_dict('records'),
        # headerを固定してスクロールできるようにします
        fixed_rows={ 'headers': True, 'data': 0 },
        filter_action='native',
        style_filter={'border': '1px solid black' },
                       #, 'textAlign':'left'},
        export_format='xlsx',
        style_header={'textAlign': 'center','border': '1px solid black' ,'color':'white','backgroundColor': '#7b68ee',
        'fontWeight': 'bold'},
        style_cell={'textAlign': 'center','border': '1px solid black' }
    )
    return output_table

@app.callback(
    Output('tabs-example-content-1', 'children'),
    [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        #return html.Div(
            #children=[
                #html.Div(evg_top_center),
                #html.Div([evg_top_left,evg_top_right]),
            #]
        #)
        return html.Div([
        dcc.Tabs(id='tabs-service-example', value='tab-nsa', 
        children=[
        dcc.Tab(
            label='NSA', 
            value='tab-nsa', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='NSC', 
            value='tab-nsc', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='NSD', 
            value='tab-nsd', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        ],
        style={
            'background-color' :'#FFFFFF',
            'display': 'block',
            'margin': '1em 0 0 0',
            'padding':'0 70% 0.05em 0',   
            'borderBottom': '1px solid #d6d6d6',
            }       
        ),
        html.Div(id='tabs-example-content-service')
        ])
        
    elif tab == 'tab-2':
        #return html.Div(
            #children=[
            #    html.Div(ooc_top_center),
            #    html.Div([ooc_top_left,ooc_top_right]),
            #    html.Div([ooc_bottom_left,ooc_bottom_right]),
            #]        
        #)
        return html.Div([
        dcc.Tabs(id='tabs-service-example', value='tab-ktx1', 
        children=[
        dcc.Tab(
            label='KTX1', 
            value='tab-ktx1', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='KTX2', 
            value='tab-ktx2', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='KTX3', 
            value='tab-ktx3', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='KTX6', 
            value='tab-ktx6', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        ],
        style={
            'background-color' :'#FFFFFF',
            'display': 'block',
            'margin': '1em 0 0 0',
            'padding':'0 70% 0.05em 0',   
            'borderBottom': '1px solid #d6d6d6',        
            }
        ),
        html.Div(id='tabs-example-content-service')
        ])
    #elif tab == 'tab-3':
        #return html.Div(
            #children=[
                #html.Div(tsl2_top_center),
                #html.Div([tsl2_top_left,tsl2_top_right]),
                #html.Div([tsl2_bottom_left,tsl2_bottom_right]),
            #]        
        #)
    elif tab == 'tab-3':
        return html.Div([
        dcc.Tabs(id='tabs-service-example', value='tab-jtk', 
        children=[
        dcc.Tab(
            label='JTK', 
            value='tab-jtk', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        dcc.Tab(
            label='JTK2', 
            value='tab-jtk2', 
            style=tab_style2, 
            selected_style=tab_selected_style2
        ),
        ],
        style={
            'background-color' :'#FFFFFF',
            'display': 'block',
            'margin': '1em 0 0 0',
            'padding':'0 70% 0.05em 0',   
            'borderBottom': '1px solid #d6d6d6',       
            }
        ),
        html.Div(id='tabs-example-content-service')
        ])
        
@app.callback(
    Output('tabs-example-content-service', 'children'),
    [Input('tabs-service-example', 'value')])
def render_content(value):
    if value == 'tab-jtk':
        return html.Div(
            children=[
                #html.Div(tsl_top_center),
                html.Div([tsl_top_left,tsl_top_right]),
                html.Div([tsl_bottom_left,tsl_bottom_right]),
            ]        
        )
    elif value == 'tab-jtk2':
        return html.Div(
            children=[
                #html.Div(tsl2_top_center),
                html.Div([tsl2_top_left,tsl2_top_right]),
                html.Div([tsl2_bottom_left,tsl2_bottom_right]),
            ]        
        )
        
    elif value == 'tab-nsa':
        return html.Div(
            children=[
                #html.Div(evg_top_center),
                html.Div([evg_top_left,evg_top_right]),
                #html.Div([evg_bottom_left,evg_bottom_right]),
            ]        
        )    
    elif value == 'tab-nsc':
        return html.Div(
            children=[
                #html.Div(evg2_top_center),
                #html.Div([evg2_top_left,evg2_top_right]),
                html.Div([evg2_bottom_left,evg2_bottom_right]),
            ]        
        )
    elif value == 'tab-nsd':
        return html.Div(
            children=[
                #html.Div(evg3_top_center),
                #html.Div([evg3_top_left,evg3_top_right]),
                html.Div([evg3_bottom_left,evg3_bottom_right]),
            ]        
        )    
        
    elif value == 'tab-ktx1':
        return html.Div(
            children=[
                #html.Div(ooc_top_center),
                html.Div([ooc_top_left,ooc_top_right]),
                html.Div([ooc_bottom_left,ooc_bottom_right]),
            ]        
        ) 
        
    elif value == 'tab-ktx2':
        return html.Div(
            children=[
                #html.Div(ooc2_top_center),
                html.Div([ooc2_top_left,ooc2_top_right]),
                html.Div([ooc2_bottom_left,ooc2_bottom_right]),
            ]        
        )  
    elif value == 'tab-ktx3':
        return html.Div(
            children=[
                #html.Div(ooc3_top_center),
                html.Div([ooc3_top_left,ooc3_top_right]),
                html.Div([ooc3_bottom_left,ooc3_bottom_right]),
            ]        
        )   
    elif value == 'tab-ktx6':
        return html.Div(
            children=[
                #html.Div(ooc6_top_center),
                html.Div([ooc6_top_left,ooc6_bottom_left]),
            ]        
        ) 
if __name__ == '__main__':
    app.run_server(debug=True)