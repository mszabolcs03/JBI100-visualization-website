import pandas as pd
import dash
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dash_table, dcc
from mplsoccer import Pitch, Sbopen, VerticalPitch

dash.register_page(__name__, path='/dataset', name="DATASET")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Br(),
    dash_table.DataTable(
        id="data-table",

        data=df.to_dict('records'),
        page_size=20,
        style_cell={"background-color": "lightgrey", "outline": "solid 0.5px var(--darkbg)", "color": "black", "font-size": "11px", "text-align": "left", "padding": "8px"},
        style_header={"background-color": "#212131", "font-weight": "500", "color": "white", "padding": "8px", "font-size": "15px"},
    )
])