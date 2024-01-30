import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch
import plotly.graph_objects as go

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

dash.register_page(__name__, path='/heatmap', name="HEATMAP")

# Page layout
layout = html.Div([
    html.Div(id="content", children=[
        html.H1('Player Activity Heatmap'),
    ])
])