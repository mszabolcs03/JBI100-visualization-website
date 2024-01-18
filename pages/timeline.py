import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch
from mplsoccer.pitch import Pitch
from plotly.tools import mpl_to_plotly
import plotly.graph_objects as go



dash.register_page(__name__, path='/timeline', name="DYNAMIC PLAY TIMELINE")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)


##################
mask_action = (df.type_name == "Pass") | (df.type_name == "Shot") | (df.type_name == "Carry")
mask_player = df.player_name == "Gonzalo Ariel Montiel"

mask_master = mask_action & mask_player

df_actions = df.loc[mask_master, ['x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']]

pitch = Pitch(pitch_color='green', line_color='white', stripe=True, corner_arcs=True)

# fig, ax = pitch.draw()

fig = px.scatter(x=df_actions['x'], y=df_actions['y'])

list_of_all_arrows = []
for x0,y0,x1,y1 in zip(df_actions["end_x"], df_actions["end_y"], df_actions["x"], df_actions["y"]):
    arrow = go.layout.Annotation(dict(
                    x=x0,
                    y=y0,
                    xref="x", yref="y",
                    text="",
                    showarrow=True,
                    axref="x", ayref='y',
                    ax=x1,
                    ay=y1,
                    arrowhead=3,
                    arrowwidth=2,
                    arrowcolor='rgb(50,50,0)',)
                )
    list_of_all_arrows.append(arrow)

fig.update_layout(annotations=list_of_all_arrows)

# fig.add_trace(arrows_trace)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[

    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'graph1', 'value': 'graph1'},
            {'label': 'graph2', 'value': 'graph2'},
                ],
        value='graph1',
        style={"width": "60%"}),



        dcc.Graph(
            id='matplotlib-pitch',
            figure=fig,
            # config={ 'modeBarButtonsToRemove': ['zoom', 'pan'], 'staticPlot': True }
        )
    ]
    )
])