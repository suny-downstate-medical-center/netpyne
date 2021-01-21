import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.tools as tls
import numpy as np
import pickle
import json

data = pickle.load(open('test.pkl'))
print (data)
#
# app = dash.Dash(__name__)
#
# app.layout = html.Div(children=[
#     # first row
#     html.H1(children='Visualisation of netpyne sim results'),
#     # second row
#     html.Div([
#         dcc.Graph( id='graph-channelParams')
#         ], style={'width': '79%', 'display': 'inline-block', 'padding': '0 20'}),
#     # third row
#     html.Div([
#         dcc.RangeSlider(
#             id='slider',
#             min=0,
#             max=parameters_df.shape[0],
#             value=[0,8],
#             marks={str(i): str(i) for i in parameters_df.index}
#         )
#         ], style={'width': '79%', 'display': 'inline-block', 'padding': '0 20'}),
#     # fifth row
#     html.Div([
#         html.Div([
#             html.H3('Section distance'),
#             dcc.Graph(id='graph-distanceBar')
#             ], style={'display': 'inline-block', 'width': '10%', 'vertical-align':'top', 'text-align': 'center'}),
#         ], style={'width': '100%', 'height':300, 'display': 'inline-block'}),
#
#     # Hidden div inside the app that stores the intermediate value
#     html.Div(id='intermediate-value', style={'display': 'none'})
# ])
#
# @app.callback(
#     dash.dependencies.Output('graph-channelParams', 'figure'),
#     [dash.dependencies.Input('slider', 'value')]
#     )
# def update_parameter_figure(models):
#     filtered_frame = parameters_df.iloc[models[0]:models[1]+1,:]
#     traces = []
#     figure={
#             'data': [go.Parcoords(
#         dimensions = list([
#             dict(range = ranges['naf'][0],
#                  label = 'naf0', values = filtered_frame.loc[:,'naf0']),
#             ])
#             )], 'layout': { 'title': 'Ion channel parameters' }
#         }
#     return figure

# ---------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
