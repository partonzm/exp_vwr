#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Version Comment: This is the sexy, stable, early version

# """And with these words of prayer they threw the barley-grains..."""

## __Import__
import pandas as pd
# import matplotlib.pyplot as plt
import os
import glob
import csv
import numpy as np
import json
# import scipy as sp
# import shutil
# import datetime
# from pylab import figure, axes, pie, title, show, savefig
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sqlite3
import re
from dash.dependencies import Input, Output
import flask
from textwrap import dedent as de
import plotly.figure_factory as ff
from plotly import tools
#custom imports
from bin import imgs

## for debug to cut through the crap
# import logging
#
# logging.getLogger('werkzeug').setLevel(logging.ERROR)

## Initital hooha
external_stylesheets = ['https://www.perlara.com/wp-content/plugins/divi_extended_column_layouts/style.css?ver=4.9.8']
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
## callback suppression for testing
#app.config['suppress_callback_exceptions']=True

# Global
database = "../../tst_dbs/test_final.db"
# list
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

## test for image display
# img_file = '../../tst_dbs/L12.jpg'
# enc_img = imgs.byt_out(img_file)

## html/app layout
colors = {
    'background': '#EE7F2D',
    'text': '#111111'
}

app.layout = html.Div(
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
            children='Experiment Viewer - Perlara PBC',
            style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

        html.Div(
            children='Platform using Dash for Model Organism Drug Discovery',
            style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),

        html.Div([
            dcc.Tabs(id="tabs", value='tab-1', children=[
                dcc.Tab(label='Tab one', value='tab-1'),
                dcc.Tab(label='Tab two', value='tab-2'),
            ])
        ], # style = {"border-style": "solid"}
        ),

        html.Div([
            dcc.Dropdown(
                id = 'dropdown_org',
                options=orgs,
                placeholder="Select an orgamism.",
                multi=True
                # value= stlates[0])
            ),

            dcc.Dropdown(
                id = 'dropdown_exp',
                placeholder="Select an experiment.",
                multi=True
                # value= stlates[0])
            )
            ], style = {"border-style": "solid"}
        ),

        ## control sep
        html.Div([
            dcc.Graph(
                id= 'box0'
                )
        ], style = {"border-style": "solid", "autosize" : "True"}
        ),

        ## img preview
        html.Div([
            html.Img(
                id= 'egami',
                width= "18%"
            )
            ], style = {"float": "center", "display": "inline-block"}
        ),
        html.Div([
            dcc.Markdown(de("""
                    **Hover Data**

                    Mouse over values in the graph.
                """),
                id='click-data'
            )
        ], style = {"float": "center", "display": "inline-block"}
        ),


        ## main scatter
        html.Div([
            dcc.Graph(
                id='scatter',
                style={
                      "height": 8000
                }
                )
        ], style = {"border-style": "solid"}
        ),

        # html.Div([
        #     dcc.Graph(
        #         id= 'box1'
        #         )
        # ], style = {"border-style": "solid", "height": "50vh"}
        # ),

        ## below are hiden html vars that store cache data

        html.Div(
            id='org',
            style={'display': 'none'}
            ),

        html.Div(
            id='current_exp_data',
            style={'display': 'none'}
        ),
        html.Div(
            id='metric',
            style={'display': 'none'}
            )
        ]
)

## call backs

@app.callback(
    Output('dropdown_exp', 'options'),
    [Input('dropdown_org', 'value')])
def exps_pull(value):
    # value = tuple(value)
    options = []
    conn = sqlite3.connect(database)
    conn.text_factory = str
    # vals = []
    # for v in value:
    #      vals.append(v.encode(unicode))
    sel = 'select * from {}'
    for i in value:
        df = pd.read_sql_query(sel.format(i), conn)
        exps = df['exp'].unique()
        for i in exps:
            options.append({'label': i, 'value': i})

    #op = options

    return(tuple(options))

@app.callback(
    Output('metric', 'children'),
    [Input('dropdown_org', 'value')])
def metric(org):

    if org == 'Cell':
        metric = 'Puncta_Area'
    elif org == 'Worm':
        metric = 'area'
    elif org == 'Yeast':
        metric = 'O.D.'

    return(metric)

@app.callback(
    Output('current_exp_data', 'children'),
    [Input('dropdown_exp', 'value'),
    Input('dropdown_org', 'value')])
def update_data(exp, org):
     # some expensive clean data step
     #cleaned_df = your_expensive_clean_or_compute_step(value)

    conn = sqlite3.connect(database)
    sel = 'select * from {} where exp=\'{}\''
    int_data = []
    for i in org:
        for e in exp:
            df = pd.read_sql_query(sel.format(i, str(e)), conn)
            # df.index.to_series()
            # interm = df.where('exp' == exp)
            # interm = df[df['exp'] == exp]
            if df.empty:
                pass
            else:
                df['org'] = str(i)
                int_data.append(df)

    exp_data = pd.concat(int_data)
    e_d = exp_data.reset_index()

    return exp_data.to_json(date_format='iso', orient='split')

## for dynamically updating size of scatter box
@app.callback(
    Output('scatter', 'style'),
    [Input('current_exp_data', 'children')])
def upd_sct_sz(data):

    df = pd.read_json(data, orient='split')

    tits = df['plt_nm'].unique()
    ln = len(tits)
    ht = 1000 * ln

    return {"height" : ht}

# faceted scatter plots
@app.callback(
    Output('scatter', 'figure'),
    [Input('current_exp_data', 'children'),
    Input('dropdown_org', 'value'),
    Input('metric', 'children')])
def update_scatter(data, org, metric):

    df = pd.read_json(data, orient='split')

    if len(df.loc[df['condt'] == 'exp'].index) > 0:
        df = df.loc[df['condt'] == 'exp']
    tits = df['plt_nm'].unique()
    ln = len(tits)
    itr = iter(range(ln))


    fig = tools.make_subplots(rows=ln, cols=1, shared_xaxes=True, print_grid=False, subplot_titles=tits)

    d = 0

    for i in df.plt_nm.unique():
#        i = str(i)
            # for i in df.plt_nm.unique():
        g = go.Scatter(
    #customdata=df.to_json(),
        x=df[df['plt_nm'] == i]['well'],
        y=df[df['plt_nm'] == i]['zneg'],
        text=str(df[df['plt_nm'] == i]['org']),
# + str(df[df['condt'] == i]['plt_nm']) ],
        mode='markers',
        opacity=0.6,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': 'black'}
        }, name=i
        )
        d += 1
    #    g['layout']
        fig.append_trace(g, d, 1)


    #fig['layout'].update(height=600, width=600, title='Stacked Subplots with Shared X-Axes')

    return{
        'data' : fig,
        'layout': go.Layout(
            xaxis={'title': 'well'},
            yaxis={'title': 'zneg'},
            height=1000,
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


# def update_corr_scatter(data, org, metric):
#
#     df = pd.read_json(data, orient='split')
#
#     return{
#         'data' : [
#             go.Scatter(
#             #customdata=df.to_json(),
#             x=df[df['condt'] == i][metric],
#             y=df[df['condt'] == i]['zneg'],
#             text=df[df['condt'] == i]['well'],
#             mode='markers',
#             opacity=0.6,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'white'}
#             },
#             name=i
#             ) for i in df.condt.unique()
#         ],
#         'layout': go.Layout(
#             xaxis={'title': metric},
#             yaxis={'title': 'zneg'},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }

    # figure = create_figure(dff)

@app.callback(
    Output('box0', 'figure'),
    [Input('current_exp_data', 'children')])
def update_box0(value):

    # more generally, this line would be
    # json.loads(jsonified_cleaned_data)

    df = pd.read_json(value, orient='split')

    if len(df['exp'].unique()) >1 :
        return{'data': []}

    else:
        plot1 = ff.create_facet_grid(
            df,
            x='condt',
            y='zneg',
            marker=dict(color='#3D9970'),
            facet_col='plt_nm',
        #                cols=df['plt_nm'].count(),
        #                facet_col='condt',
            boxpoints='all',
            ggplot2=True,
            trace_type='box'
            # boxmean=True,
            # jitter=0.1
            )

            # boxmode='overlay

        plot1['layout'].update(
            title='control seperation',
            # titlefont=dict(
            #     family='Arial, sans-serif',
            #     size=18,
            #     color='black'
            # ),
            autosize=True,
            width=2000
            )

        return(plot1)

## img return callback
@app.callback(
    Output('egami', 'src'),
    [Input('dropdown_exp', 'value')])
def upd_img(value):
    if len(value) >=1 :
        img_file = '../../tst_dbs/L12.jpg'
        enc_img = imgs.byt_out(img_file)
        src = 'data:image/png;base64,{}'.format(enc_img.decode())
        return(src)
    else:
        return{}
    # }

## change text on click
@app.callback(
    Output('click-data', 'children'),
    [Input('scatter', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

# @app.callback(
#     Output('box1', 'figure'),
#     [Input('current_exp_data', 'children'),
#     Input('dropdown_org', 'value'),
#     Input('metric', 'children')])
# def update_box1(data, org, metric):
#
#     # more generally, this line would be
#     # json.loads(jsonified_cleaned_data)
#     df = pd.read_json(data, orient='split')
#
#     return{
#         'data' : [
#             go.Box(
#                 # x=df[df['condt'] == i]['zneg'],
#                 y=df[df['condt'] == i][metric],
#                 marker=dict(color='#3D9970'),
#                 name=i,
#                 boxpoints='all',
#                 boxmean=True,
#                 jitter=0.1
#             ) for i in df.condt.unique()
#         ],
#         'layout': go.Layout(
#             yaxis=dict(
#                 title=metric,
#                 zeroline=False
#             ),
#             boxmode='overlay'
#         )
#     }


## main loop
if __name__ == '__main__':
    app.run_server(debug=True,port=8050,host='0.0.0.0')
