import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.tools as tls
import neuron as nrn
import numpy as np
import pickle
import json
import morph_lib_creator

#path = '../../Neuron/Libraries/'
path = './'
with open('{}map_sec_dist_to_soma.pkl'.format(path), 'rb') as f:
    dist_mapper = pickle.load(f)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    # first row
    html.H1(children='Vizualization of multivariant data'),
    # second row
    html.Div([
        dcc.Graph( id='graph-channelParams')
        ], style={'width': '79%', 'display': 'inline-block', 'padding': '0 20'}),
    # third row
    html.Div([
        dcc.RangeSlider(
            id='slider',
            min=0,
            max=parameters_df.shape[0],
            value=[0,8],
            marks={str(i): str(i) for i in parameters_df.index}
        )
        ], style={'width': '79%', 'display': 'inline-block', 'padding': '0 20'}),
    # forth row
    html.Div([
        html.Div([
            html.H3('Data set'),
            dcc.RadioItems(
                id='data-set',
                options=[
                    {'label': 'Restricted', 'value': 'Restricted'},
                    {'label': 'RestSingle', 'value': 'RestSingle'}
                    ],
                value='Restricted'
                )], style={'display': 'inline-block', 'width':'15%', 'vertical-align':'top'}),
        html.Div([
            html.H3('Pattern size'),
            dcc.RadioItems(
                id='pattern-size',
                options=[
                    {'label': '16', 'value': 16},
                    {'label': '32', 'value': 32},
                    {'label': '64', 'value': 64}
                    ],
                value=16,
                )], style={'display': 'inline-block', 'width':'15%','vertical-align':'top'}),
        html.Div([
            html.H3('DA mod'),
            dcc.RadioItems(
                id='da-mod',
                options=[
                    {'label': 'control', 'value': 0},
                    {'label': '50%',     'value': 50},
                    {'label': '100%',    'value': 100}
                    ],
                value=0
                )], style={'display': 'inline-block', 'width':'15%','vertical-align':'top'}),
        html.Div([
            html.H3('model'),
            dcc.Input(
                id='model_slider',
                placeholder='Enter a value...',
                value=5
                )], style={'display': 'inline-block', 'width':'15%','vertical-align':'top'}),
        html.Div([
            html.H3('pattern number'),
            dcc.Input(
                id='pattern',
                placeholder='Enter a value...',
                value=1
                )], style={'display': 'inline-block', 'width':'15%', 'vertical-align':'top'}),
        html.Div([
            html.H3('sub pattern'),
            dcc.Slider(
                id='sub_slider',
                min=0,
                max=6,
                value=4,
                marks={str(i): str(i) for i in range(7)}
                )], style={'display': 'inline-block', 'width':'15%', 'vertical-align':'top'})
            ], style={  'width': '70%',
                        'margin': '50',
                        'border-style':'solid',
                        'border-radius': '5px',
                        'border-color': 'lightgrey',
                        'background-color':'white',
                        'border-width': '2px'}),
    # fifth row
    html.Div([
        html.Div([
            dcc.Graph(id='graph-morph')
            ], style={'display': 'inline-block', 'hight': '100%'}),
        html.Div([
            html.H3('Section distance'),
            dcc.Graph(id='graph-distanceBar')
            ], style={'display': 'inline-block', 'width': '10%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Vm soma'),
            dcc.Graph(id='voltage-graph')
            ], style={'display': 'inline-block', 'width': '15%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Vm local'),
            dcc.Graph(id='graph-localVm')
            ], style={'display': 'inline-block', 'width': '15%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Morph stat vs spiking'),
            dcc.RadioItems(
                id='stat',
                options=[
                    {'label': 'N',    'value': 'N_endpoints'},
                    {'label': 'Ltot', 'value': 'total_distance'},
                    {'label': 'Lmax', 'value': 'max_len2endpoint'}
                    ],
                value='N_endpoints'
                ),
            dcc.Graph(id='mean-spike-stat')
            ], style={'display': 'inline-block', 'width': '15%', 'vertical-align':'top', 'text-align': 'center'})
        ], style={'width': '100%', 'height':300, 'display': 'inline-block'}),

    # sixth row
    html.Div([
        html.Div([
            html.H3('Mean # spikes vs clustering'),
            dcc.Graph(id='spike-count-graph')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Mean # spikes vs distance'),
            dcc.Graph(id='mean-spike-graph')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            dcc.Graph(id='stem-hover-graph')
            ], style={'display': 'inline-block', 'hight': '100%'}),
        html.Div([
            html.H3('section stat'),
            dcc.Graph(id='graph-sectionHowerData')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'})
        ], style={'width': '100%', 'height':300, 'display': 'inline-block', 'margin': '20'}),

    # seventh row
    html.Div([
        dcc.Markdown('''
# Conclusions
#### - There's a somatic distance dependence of spiking
#### - There are sections deviating from this rule
#### -> these sections have a larger subtree distally
#### - Can be shown by direct manipulation of morphology?
''',
id='blind_spot')
        ]),

    # eigth row
    html.Div([
        html.Div([
            html.H3('Before manipulation'),
            dcc.Graph(id='morph_manip_morph1')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('After manipulation'),
            dcc.Graph(id='morph_manip_morph2')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Spike raster'),
            dcc.Graph(id='morph_manip_scatter')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'}),
        html.Div([
            html.H3('Mean spiking'),
            dcc.Graph(id='morph_manip_bar')
            ], style={'display': 'inline-block', 'width': '20%', 'vertical-align':'top', 'text-align': 'center'})
        ], style={'width': '100%', 'height':300, 'display': 'inline-block', 'margin': '20'}),


    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'})
])

@app.callback(
    dash.dependencies.Output('graph-channelParams', 'figure'),
    [dash.dependencies.Input('slider', 'value')]
    )
def update_parameter_figure(models):
    filtered_frame = parameters_df.iloc[models[0]:models[1]+1,:]
    traces = []
    figure={
            'data': [go.Parcoords(
        dimensions = list([
            dict(range = ranges['naf'][0],
                 label = 'naf0', values = filtered_frame.loc[:,'naf0']),
            dict(range = ranges['naf'][1],
                 label = 'naf1', values = filtered_frame.loc[:,'naf1']),
            dict(range = ranges['naf'][2],
                 label = 'naf2', values = filtered_frame.loc[:,'naf2']),
            dict(range = ranges['naf'][3],
                 label = 'naf3', values = filtered_frame.loc[:,'naf3']),
            dict(range = ranges['kaf'][0],
                 label = 'kaf0', values = filtered_frame.loc[:,'kaf0']),
            dict(range = ranges['kaf'][1],
                 label = 'kaf1', values = filtered_frame.loc[:,'kaf1']),
            dict(range = ranges['kaf'][2],
                 label = 'kaf2', values = filtered_frame.loc[:,'kaf2']),
            dict(range = ranges['kaf'][3],
                 label = 'kaf3', values = filtered_frame.loc[:,'kaf3']),
            dict(range = ranges['kas'][0],
                 label = 'kas0', values = filtered_frame.loc[:,'kas0']),
            dict(range = ranges['kas'][1],
                 label = 'kas2', values = filtered_frame.loc[:,'kas2']),
            dict(range = ranges['kas'][2],
                 label = 'kas3', values = filtered_frame.loc[:,'kas3']),
            dict(range = ranges['Kir'][0],
                 label = 'Kir',  values = filtered_frame.loc[:,'Kir']),
            dict(range = ranges['sk'][0],
                 label = 'sk', values = filtered_frame.loc[:,'sk']),
            dict(range = ranges['can'][0],
                 label = 'can0', values = filtered_frame.loc[:,'can0']),
            dict(range = ranges['can'][1],
                 label = 'can1', values = filtered_frame.loc[:,'can1']),
            dict(range = ranges['can'][2],
                 label = 'can2', values = filtered_frame.loc[:,'can2']),
            dict(range = ranges['can'][3],
                 label = 'can3', values = filtered_frame.loc[:,'can3']),
            dict(range = ranges['c32'][0],
                 label = 'c32-0', values = filtered_frame.loc[:,'c32-0']),
            dict(range = ranges['c32'][1],
                 label = '32-2', values = filtered_frame.loc[:,'32-2']),
            dict(range = ranges['c32'][2],
                 label = '32-3', values = filtered_frame.loc[:,'32-3']),
            dict(range = ranges['c33'][0],
                 label = 'c33-0', values = filtered_frame.loc[:,'c33-0']),
            dict(range = ranges['c33'][1],
                 label = '33-2', values = filtered_frame.loc[:,'33-2']),
            dict(range = ranges['c33'][2],
                 label = '33-3', values = filtered_frame.loc[:,'33-3'])
            ])
            )], 'layout': { 'title': 'Ion channel parameters' }
        }
    return figure


# ---------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)
