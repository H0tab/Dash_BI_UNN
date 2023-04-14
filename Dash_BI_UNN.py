#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import datetime
import numpy as np
import re


# In[2]:


#from jupyter_dash import JupyterDash  #Если используем внутри Jupyter. На проде - закомитить


# In[3]:


#Для отрисовки дашбордов
import dash
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

import plotly
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


# In[4]:


#Для подключения к серверу
import grpc

from point_data_v1_pb2_grpc import PointDataServiceStub
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.wrappers_pb2 import StringValue
import point_data_v1_pb2


# In[5]:


#Включаем Dask
from distributed import Client

dask_client = Client(processes=False)


# In[6]:


from activity_v1_pb2_grpc import ActivityServiceStub
import activity_v1_pb2


# In[7]:


#Параметры
BLOCKSIZE = 1024e5  #Выбор размера блока памяти в Dask
#css_path = r"D:\Juputer ML\dash-demo\assets\style.css"  #сюда вписать путь до css. Локальный файл/сайт


# In[8]:


#Внешка и логика дашбордов
#Если запускаем на проде - просто юзаем Dash(__name__)
app = Dash(__name__)  #На случай запуска в Jupyter
server = app.server

#app.css.append_css({"external_url": css_path})  #подключение внешнего css

#Фронт
app.layout = html.Div(children=[
    html.H1(children="Дашборд состояний"),
    #Первый раздел. Просмотр готового датасета
    dcc.Tabs([
        #Второй раздел
        dcc.Tab(
            label="Создание собственных графиков",
            children=[
                #Добавление пользователей в запрос gRPC по ID
                html.
                P(children=
                  "Введите номер пользователя для  добавления в меню выгрузки  "
                  ),
                dcc.Input(id='UserIdInput', value=''),
                html.Button('Добавить пользователя', id='UserSubmitButton'),
                html.P(children="Выберите всех желаемых пользователей  "),
                dcc.Dropdown(
                    id='UserSelectorGRPC',
                    options=[
#                        {'label': '12', 'value': 12},
                    ],
                    value='a',
                    multi=True),
                #Даты для запроса gRPC
                html.P(children="Выберите нужный диапазон дат для выгрузки  "),
                dcc.DatePickerRange(id='CalendarSelectorGRPC',
                                    start_date_placeholder_text="Дата начала",
                                    end_date_placeholder_text="Дата конца",
                                    calendar_orientation='vertical'),
                #Выбор переменных для отображения
                html.
                P(children=
                  "Введите название состояния для добавления в меню выгрузки  "
                  ),
                dcc.Input(id='StateInput', value=''),
                html.Button('Добавить состояние', id='StateSubmitButton'),
                html.P(children="Выберите все желаемые состояния"),
                dcc.Dropdown(
                    id='StateSelectorGRPC',
                    options=[
                                     #{'label': 'Stress', 'value': Stress_10_avg},
                    ],
                    value='a',
                    multi=True),
                html.P(children=
                  "Выберите класс выбранных состояний. Может быть только 1 класс на 1 выгрузку"
                  ),
                dcc.RadioItems(['eeg', 'wave', 'mental','skin'], 'mental', inline=True, id="RadioClassInput"),
                #Выбор типа графика
                html.P(children="Выберите тип графика для отображения  "),
                dcc.Dropdown(id='GraphTypeSelectorGRPC',
                             options=[
                                 {'label': 'Линейный график','value': 'line'},
                                 {'label': 'Гистограммы','value': 'hist'},
                                 {'label': 'Коллективная синхронизация','value': 'colsync'},
                             ],
                             value='a',
                             multi=False),
                html.Button('Построить график', id='GraphSubmitButton'),
                html.Button("Скачать CSV", id="CsvDownloadButton"),
                dcc.Download(id="DownloadDataframeCSV"),
                #результирующий график
                dcc.Loading(id="GRPCLoading1",
                            children=dcc.Graph(id='UserCreatedGraphGRPC'),
                            type="circle"),
            ]),
    ])
])

#Логика обращений


#Меню добавления новых пользователей в выгрузку GRPC
@app.callback(
    Output('UserSelectorGRPC', 'options'),
    [Input('UserSubmitButton', 'n_clicks')],
    [State('UserIdInput', 'value'),
     State('UserSelectorGRPC', 'options')],
)
def callback(n_clicks, new_value, current_options):
    print(current_options)
    if not n_clicks:
        return current_options
    check_list = [current_options[i]['value'] for i in range(len(current_options))]
    if new_value not in (check_list):
        current_options.append({'label': str(new_value), 'value': new_value})
        return current_options
    else:
        return current_options


#Меню добавления новых состояний в выгрузку GRPC
@app.callback(
    Output('StateSelectorGRPC', 'options'),
    [Input('StateSubmitButton', 'n_clicks')],
    [State('StateInput', 'value'),
     State('StateSelectorGRPC', 'options'),
    ],
)
def callback(n_clicks, new_value, current_options):
    if not n_clicks:
        return current_options
    check_list = [current_options[i]['value'] for i in range(len(current_options))]
    if new_value not in (check_list):
        current_options.append({'label': str(new_value), 'value': new_value})
        return current_options
    else:
        return current_options


#Выгрузка из GRPC и построение графика
@app.callback(
    Output('UserCreatedGraphGRPC', 'figure'),
    [Input('GraphSubmitButton', 'n_clicks')],
    [
        State('UserSelectorGRPC', 'value'),
        State('StateSelectorGRPC', 'value'),
        State('GraphTypeSelectorGRPC', 'value'),
        State("CalendarSelectorGRPC", 'start_date'),
        State("CalendarSelectorGRPC", 'end_date'),
        State("RadioClassInput", 'value'),
    ],
)
def update_graph(n_clicks, users_list, state_list, graph_type, start_date,
                 end_date, class_type):
    if not n_clicks:
        raise PreventUpdate
    #Открываем подключение
    options = [('grpc.max_receive_message_length', 10*100 * 1024 * 1024)] #Настройка максимального размера запроса.Может потребоваться увеличить для огромных выгрузок
    channel = grpc.insecure_channel('{}:{}'.format('cdb.neurop.org', 5055),
                                    options=options)
    client = PointDataServiceStub(channel)
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()
    #Посылаем запрос
    request = point_data_v1_pb2.PeriodRequest(
        fromDate=Timestamp(seconds=int(start), nanos=0),
        toDate=Timestamp(seconds=int(end), nanos=0),
        group='bio',
        kinds=state_list,
        users=[
            point_data_v1_pb2.PointDataUser(userId=int(i), tenantId=0)
            for i in users_list
        ])
    setattr(request, 'class', str(class_type))
    response = client.GetPoints(request)
    
    #Создаем датафрейм
    df = pd.DataFrame({"user_id":[int(response.data[i].user.userId) for i in range(len(response.data))],
                       "seconds":[response.data[i].time.seconds for i in range(len(response.data))],
                       "nanos":[response.data[i].time.nanos for i in range(len(response.data))],
                       "kind":[response.data[i].kind for i in range(len(response.data))],
                       "value":[float(response.data[i].value) for i in range(len(response.data))]})
 
    df["registered_at"] = pd.to_datetime(
        df['seconds'], unit='s') + pd.to_timedelta(df['nanos'], unit='ns')
    df.drop(columns=["seconds", "nanos"], inplace=True)
    #Делаем "широкий датасет"
    wide_df = pd.DataFrame()
    for user in df["user_id"].unique():
        df_user = df[df["user_id"] == user]
        df_user.drop(columns=["user_id"])
        #группируем по времени, усредняем за секунду
        df_user = df_user.pivot_table(index='registered_at',
                                      columns='kind',
                                      values='value',
                                      aggfunc="mean")
        #Чистим строчки, где есть хотя бы 1 NaN
        df_user = df_user.dropna(axis=0, how="any")
        #Добавляем юзера обратно
        df_user["user_id"] = user
        wide_df = pd.concat([wide_df, df_user], ignore_index=False)
    #Удаляем строчки с нулями
    wide_df = wide_df[~wide_df.eq(0).any(1)]
    
    #Рисуем гистограмму пользователь/состояние
    if graph_type == "hist":
        fig = go.Figure()
        for state in state_list:
            fig.add_trace(
                go.Histogram(histfunc="avg",
                             y=wide_df[state],
                             x=wide_df['user_id'],
                             name=state))
        fig.update_layout(title_text='Пользователи и среднее состояние',
                          xaxis_title_text='Пользователи',
                          yaxis_title_text='Среднее состояние',
                          bargap=0.5,
                          bargroupgap=0.1,
                          template="plotly_dark")
        fig.update_xaxes(type='category')
        return fig

    #Рисуем линейный график пользователь/состояние во времени
    elif graph_type=="line":
        fig = go.Figure()
        for state in state_list:
            for user in users_list:
                fig.add_trace(go.Scatter(x=wide_df.index,
                                         y=wide_df[wide_df.user_id==int(user)][state],
                                         name=f'{user}_{state}',
                                         line_shape='spline'))
        fig.update_layout(title_text='График состояния во времени',
                                xaxis_title_text='Время',
                                yaxis_title_text='Параметр',
                                template ="plotly_dark")
        return fig
    elif graph_type=="colsync":
        roll_corr_graph=pd.DataFrame()
        #Считаем скользящую корреляцию для каждого из показателей по всем пользователям
        for state in state_list: 
            wide_df_state = wide_df[[state,"user_id"]]
            wide_df_state.index=wide_df_state.index.ceil(freq='s')
            wide_df_state = wide_df_state.pivot_table(index=wide_df_state.index,
                                     values=state,
                                     columns="user_id",
                                     aggfunc='mean')
            wide_df_state.dropna(how="any") #Можно заменить на thresh=2 - удалять строчки, где есть данные хотя бы у 2 юзеров
            n = len(wide_df_state.columns)
            #Считаем корреляцию по пользователям
            roll_corr_graph_state =pd.DataFrame(((wide_df_state.rolling(60).corr().unstack(-1).sum(skipna=True,axis=1)- n) / 2) / ((n**2 - n)/2))

            roll_corr_graph_state.columns =[f"Корреляция по {state}"]
            #Делаем датасет со всеми корреляциями показателей
            roll_corr_graph =  pd.concat([roll_corr_graph, roll_corr_graph_state], axis=1)

        #Строим график    
        fig = go.Figure()
        for column in roll_corr_graph.columns:
            fig.add_trace(go.Scatter(x=roll_corr_graph.index,
                                                 y=roll_corr_graph[column],
                                                 name=column,
                                                 line_shape='spline'))
        fig.update_layout(title_text='График коллективной синхронизации',
                                        xaxis_title_text='Время',
                                        yaxis_title_text='Коэффициент корреляции',
                                        template ="plotly_dark")
        return fig
    
#Скачивание CSV 
@app.callback(
    Output("DownloadDataframeCSV", "data"),
    Input("CsvDownloadButton", "n_clicks"),
    [
        State('UserSelectorGRPC', 'value'),
        State('StateSelectorGRPC', 'value'),
        State('GraphTypeSelectorGRPC', 'value'),
        State("CalendarSelectorGRPC", 'start_date'),
        State("CalendarSelectorGRPC", 'end_date'),
        State("RadioClassInput", 'value'),
    ],
    prevent_initial_call=True,
)
def func(n_clicks, users_list, state_list, graph_type, start_date,
                 end_date, class_type):
    if not n_clicks:
        raise PreventUpdate
    else:
        options = [('grpc.max_receive_message_length', 10*100 * 1024 * 1024)] #Настройка максимального размера запроса.Может потребоваться увеличить для огромных выгрузок
        channel = grpc.insecure_channel('{}:{}'.format('cdb.neurop.org', 5055),
                                    options=options)
        client = PointDataServiceStub(channel)
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()
    #Посылаем запрос
        request = point_data_v1_pb2.PeriodRequest(
            fromDate=Timestamp(seconds=int(start), nanos=0),
            toDate=Timestamp(seconds=int(end), nanos=0),
            group='bio',
            kinds=state_list,
            users=[
                point_data_v1_pb2.PointDataUser(userId=int(i), tenantId=0)
                for i in users_list
            ])
        setattr(request, 'class', str(class_type))
        response = client.GetPoints(request)
    
        #Создаем датафрейм
        df = pd.DataFrame({"user_id":[int(response.data[i].user.userId) for i in range(len(response.data))],
                           "seconds":[response.data[i].time.seconds for i in range(len(response.data))],
                           "nanos":[response.data[i].time.nanos for i in range(len(response.data))],
                           "kind":[response.data[i].kind for i in range(len(response.data))],
                           "value":[float(response.data[i].value) for i in range(len(response.data))]})

        df["registered_at"] = pd.to_datetime(
            df['seconds'], unit='s') + pd.to_timedelta(df['nanos'], unit='ns')
        df.drop(columns=["seconds", "nanos"], inplace=True)
        #Делаем "широкий датасет"
        wide_df = pd.DataFrame()
        for user in df["user_id"].unique():
            df_user = df[df["user_id"] == user]
            df_user.drop(columns=["user_id"])
            #группируем по времени, усредняем за секунду
            df_user = df_user.pivot_table(index='registered_at',
                                          columns='kind',
                                          values='value',
                                          aggfunc="mean")
            #Чистим строчки, где есть хотя бы 1 NaN
            df_user = df_user.dropna(axis=0, how="any")
            #Добавляем юзера обратно
            df_user["user_id"] = user
            wide_df = pd.concat([wide_df, df_user], ignore_index=False)
        #Удаляем строчки с нулями
        wide_df = wide_df[~wide_df.eq(0).any(1)]
            
        return dcc.send_data_frame(wide_df.to_csv, f"DF_{class_type}_{start_date}_{end_date}.csv")
        

#В случае запуска не в юпитере - раскомититить:
#if __name__ == "__main__":
#    app.run(debug=False)


# In[9]:


app.run_server(port=8051, debug=True)


# In[ ]:




