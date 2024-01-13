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

    html.Div(id="selection_container", children=[
	    dcc.Link(page['name'], href=page["relative_path"])\
			  for page in dash.page_registry.values()]
	),

	dash.page_container
])


if __name__ == '__main__':
	app.run(debug=False)