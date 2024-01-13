import dash
import plotly.express as px
from dash import Dash, html, dash_table, dcc
import pandas as pd
from mplsoccer import Pitch, Sbopen, VerticalPitch

# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

# Initialize the app
app = Dash(__name__, pages_folder='pages', use_pages=True)

# App layout
app.layout = html.Div([
	html.P("FIFA WORLD CUP ANALYSIS - GROUP 62", id="title"),

    html.Div(id="selection-container", children=[
		html.Div(id="selection-group-1", children=[
			dcc.Link("INTRO", href="/", className="page-option", id="intro"),
	        dcc.Link("DATASET", href="/dataset", className="page-option", id="dataset"),
	        dcc.Link("GITHUB", href="/source", className="page-option", id="source")
        ]),
	    
	    dcc.Link("PASSING NETWORK", href="/passing", className="page-option", id="passing"),
	    dcc.Link("ACTIVITY HEATMAP", href="/heatmap", className="page-option", id="heatmap"),
	    dcc.Link("SHOT ANALYSIS", href="/shot", className="page-option", id="shot"),
	    dcc.Link("DYNAMIC PLAY TIMELINE", href="/timeline", className="page-option", id="timeline")
    ]
	),

	dash.page_container
])


if __name__ == '__main__':
	app.run(debug=False)