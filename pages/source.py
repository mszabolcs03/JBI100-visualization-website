import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch


dash.register_page(__name__, path='/source', name="GITHUB")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[
        html.A("github.com/mszabolcs03/JBI100-visualization-website", id="github-link", href="https://github.com/mszabolcs03/JBI100-visualization-website")
    ])
])