from datetime import datetime as dt

import pandas as pd
import os
import glob
import csv
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sqlite3
import re
from dash.dependencies import Input, Output
import flask
import pandas_datareader as pdr
from dash.dependencies import Input
from dash.dependencies import Output
from flask_login import login_required

from app import create_app
# from bin import graphs

def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


server = create_app()

# =============================
# Dash app
# =============================
dashapp = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')
protect_dashviews(dashapp)

dashapp.layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})


@dashapp.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    df = pdr.get_data_yahoo(selected_dropdown_value, start=dt(2017, 1, 1), end=dt.now())
    return {
        'data': [{
            'x': df.index,
            'y': df.Close
        }],
        'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
    }

# =============================
# Another dash app
# =============================
# ...

dashapp2 = dash.Dash(__name__, server=server, url_base_pathname='/exp_viz/')
protect_dashviews(dashapp2)

database = "../tst_dbs/test_final.db"

# Data Import
    ## fetch plates
def tables_pull(db):
    conn = sqlite3.connect(db)
    conn.text_factory = str # not sure if necc
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    options = []

    for i in tables:
        options.append({'label': i[0], 'value': i[0]}) # not sure if u is necc

    return(options)

orgs = tables_pull(database)

## html/app layout
colors = {
    'background': '#EE7F2D',
    'text': '#111111'
}

dashapp2.layout = html.Div(
    style={'backgroundColor': colors['background'], "border-style": "solid"},
    children=[
        html.H1(
            children='ArkBase 1.0',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(
            children='Experiment Viewer - Perlara PBC', style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

        html.Div(
            children='Platform using Dash for Model Organism Drug Discovery', style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

        html.Div([
            dcc.Dropdown(
                id = 'dropdown_org',
                options=orgs,
                placeholder="Select an orgamism."
                # multi=True
                # value= stlates[0])
            )
            ]
        ),

        html.Div([
            dcc.Dropdown(
                id = 'dropdown_exp',
                placeholder="Select an experiment."
            )
            ]
        ),

        html.Div([
            dcc.Graph(
                id='scatter'
                )
        ], style = {"border-style": "solid", "height": "50vh"}
        ),

        html.Div([
            dcc.Graph(
                id= 'box0'
                )
        ], style = {"border-style": "solid", "height": "50vh"}
        ),

        html.Div([
            dcc.Graph(
                id= 'box1'
                )
        ], style = {"border-style": "solid", "height": "50vh"}
        ),

        html.Div(
            id='org',
            style={'display': 'none'}
            ),

        html.Div(
            id='current_exp_data',
            style={'display': 'none'}
            )
        ]
)

## call backs

@dashapp2.callback(
    Output('dropdown_exp', 'options'),
    [Input('dropdown_org', 'value')])
def exps_pull(value):
    conn = sqlite3.connect(database)
    # v = value.decode('utf8')
    sel = 'select * from {}'
    df = pd.read_sql_query(sel.format(value), conn)
    exps = df['exp'].unique()
    options = []

    for i in exps:
        options.append({'label': i, 'value': i})

    #op = options

    return(tuple(options))

@dashapp2.callback(
    Output('current_exp_data', 'children'),
    [Input('dropdown_exp', 'value'),
    Input('dropdown_org', 'value')])
def update_data(exp, org):
     # some expensive clean data step
     #cleaned_df = your_expensive_clean_or_compute_step(value)

    conn = sqlite3.connect(database)
    sel = 'select * from {}'
    df = pd.read_sql_query(sel.format(org), conn)
    exp_data = df[df['exp'] == exp]

    return exp_data.to_json(date_format='iso', orient='split')

@dashapp2.callback(
    Output('scatter', 'figure'),
    [Input('current_exp_data', 'children'),
    Input('dropdown_org', 'value')])
def update_scatter(data, org):

    df = pd.read_json(data, orient='split')

    if org == 'Worm':
        metric = 'area'
    elif org == 'Yeast':
        metric = 'O.D.'

    return{
        'data' : [
            go.Scatter(
            #customdata=df.to_json(),
            x=df[df['condt'] == i]['zneg'],
            y=df[df['condt'] == i][metric],
            text=df[df['condt'] == i]['well'],
            mode='markers',
            opacity=0.6,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
            ) for i in df.condt.unique()
        ],
        'layout': go.Layout(
            xaxis={'title': 'zneg'},
            yaxis={'title': metric},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


    # figure = create_figure(dff)

@dashapp2.callback(
    Output('box0', 'figure'),
    [Input('current_exp_data', 'children')])
def update_box0(value):

    # more generally, this line would be
    # json.loads(jsonified_cleaned_data)
    df = pd.read_json(value, orient='split')

    return{
        'data' : [
            go.Box(
                # x=df[df['condt'] == i]['zneg'],
                y=df[df['condt'] == i]['zneg'],
                marker=dict(color='#3D9970'),
                name=i,
                boxpoints='all',
                boxmean=True,
                jitter=0.1
            ) for i in df.condt.unique()
        ],
        'layout': go.Layout(
            yaxis=dict(
                title='Z-neg',
                zeroline=True
            ),
            boxmode='overlay'
        )
    }

@dashapp2.callback(
    Output('box1', 'figure'),
    [Input('current_exp_data', 'children'),
    Input('dropdown_org', 'value')])
def update_box1(data, org):

    # more generally, this line would be
    # json.loads(jsonified_cleaned_data)
    df = pd.read_json(data, orient='split')

    if org == 'Worm':
        metric = 'area'
    elif org == 'Yeast':
        metric = 'O.D.'

    return{
        'data' : [
            go.Box(
                # x=df[df['condt'] == i]['zneg'],
                y=df[df['condt'] == i][metric],
                marker=dict(color='#3D9970'),
                name=i,
                boxpoints='all',
                boxmean=True,
                jitter=0.1
            ) for i in df.condt.unique()
        ],
        'layout': go.Layout(
            yaxis=dict(
                title=metric,
                zeroline=False
            ),
            boxmode='overlay'
        )
    }
