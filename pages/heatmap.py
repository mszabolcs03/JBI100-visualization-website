"""
import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch


dash.register_page(__name__, path='/heatmap', name="ACTIVITY HEATMAP")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[

    ])])
"""
import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
from mplsoccer import Sbopen
import plotly.graph_objects as go
from mplsoccer.pitch import Pitch

# Initialize Dash app
app = dash.Dash(__name__)

# Load the StatsBomb data
parser = Sbopen()
competitions = parser.competition()

# Function to get matches between two teams
def get_matches_between_teams(team1, team2):
    # Load matches for a specific competition and season
    match_list = parser.match(competition_id=43, season_id=3)  # Example competition and season IDs

    # Filter for matches between the two teams
    filtered_matches = match_list[((match_list['home_team_name'] == team1) & 
                                  (match_list['away_team_name'] == team2)) |
                                 ((match_list['home_team_name'] == team2) & 
                                  (match_list['away_team_name'] == team1))]

    return filtered_matches

# Function to create a heatmap
def create_heatmap(player_df):
    # Create a heatmap using Plotly
    fig = px.density_heatmap(player_df, x='x', y='y', nbinsx=40, nbinsy=40, color_continuous_scale='Reds')
    return fig

# Layout of the app
app.layout = html.Div([
    html.H1("Soccer Match Analysis"),
    dcc.Input(id='team1-input', type='text', placeholder='Enter first team'),
    dcc.Input(id='team2-input', type='text', placeholder='Enter second team'),
    html.Button('Submit', id='submit-val', n_clicks=0),
    dcc.Dropdown(id='player-dropdown', placeholder='Select a player'),  # Dropdown for selecting player
    dcc.Graph(id='heatmap')
])

# Callback for updating the player dropdown
@app.callback(
    Output('player-dropdown', 'options'),
    [Input('submit-val', 'n_clicks')],
    [State('team1-input', 'value'),
     State('team2-input', 'value')]
)
def update_output(n_clicks, team1, team2):
    if n_clicks > 0:
        matches = get_matches_between_teams(team1, team2)
        if not matches.empty:
            # Select the first match and its events as an example
            match_id = matches['match_id'].iloc[0]
            events = parser.event(match_id)[0]
            player_df = events[events['player_name'] == events['player_name'].dropna().unique()[0]]  # Selecting first player as an example
            fig = create_heatmap(player_df)
            return fig
        else:
            return px.scatter()  # Return an empty plot if no matches found
    else:
        return px.scatter()  # Return an empty plot initially

# Initialize Dash app
app = dash.Dash(__name__)

# Load the StatsBomb data
parser = Sbopen()

# Initialize the pitch
pitch = Pitch(line_color='white', pitch_color='green')

# Function to get matches between two teams
# ... [The rest of the get_matches_between_teams function goes here]

# Function to create a heatmap with a football pitch background
# Function to create a heatmap with a football pitch background
def create_football_pitch_heatmap(player_df):
    # Scale the 'x' and 'y' coordinates to the full pitch dimensions
    player_df['x'] = (player_df['x'] - player_df['x'].min()) / (player_df['x'].max() - player_df['x'].min()) * 120
    player_df['y'] = (player_df['y'] - player_df['y'].min()) / (player_df['y'].max() - player_df['y'].min()) * 80
    # Create figure with pitch layout
    fig = go.Figure()

    # Set up the soccer pitch layout within the figure
    # Draw the outer pitch boundary
    fig.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color="white"), fillcolor='green')
    
    # Draw the center line
    fig.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="white"))
    
    # Draw the center circle
    fig.add_shape(type="circle", xref="x", yref="y", x0=50, y0=30, x1=70, y1=50, line=dict(color="white"))
    
    # Left Penalty Area
    fig.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color="white"))
    
    # Right Penalty Area
    fig.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="white"))
    
    # Left 6-yard Box
    fig.add_shape(type="rect", x0=0, y0=30, x1=6, y1=50, line=dict(color="white"))
    
    # Right 6-yard Box
    fig.add_shape(type="rect", x0=114, y0=30, x1=120, y1=50, line=dict(color="white"))
    
 # Debugging: Print the player_df to make sure it's not empty and the data is valid
    if not player_df.empty and 'x' in player_df.columns and 'y' in player_df.columns:
        # Print the first few rows of the DataFrame
        print(player_df.head())

        # Check the range of the x and y coordinates
        print("X min, max:", player_df['x'].min(), player_df['x'].max())
        print("Y min, max:", player_df['y'].min(), player_df['y'].max())

        # Create the heatmap trace with count aggregation
        heatmap_trace = go.Histogram2d(
            x=player_df['x'],
            y=player_df['y'],
            histfunc='count',
            nbinsx=24,  # Adjust the number of bins for the x-axis
            nbinsy=16,  # Adjust the number of bins for the y-axis
            colorscale='Reds',
            zmin=0,  # Include all bins in the color scale
            colorbar=dict(title='Number of actions'),
            showscale=True
        )
        
        fig.add_trace(heatmap_trace)
    else:
        print("Dataframe is empty or missing 'x' and 'y' columns. No data to create heatmap.")

    # Update the layout to match the pitch and make the background green
    fig.update_layout(
        autosize=False,
        width=900,
        height=600,
        paper_bgcolor="green",
        plot_bgcolor="green",
        margin=dict(t=20, l=20, b=20, r=20),
        title="Player Heatmap on Pitch"
    )

    # Remove axis ticks and labels
    fig.update_xaxes(showticklabels=False, range=[0, 120])
    fig.update_yaxes(showticklabels=False, range=[0, 80])

    return fig


# Layout of the app
app.layout = html.Div([
    html.H1("Soccer Match Analysis"),
    dcc.Input(id='team1-input', type='text', placeholder='Enter first team'),
    dcc.Input(id='team2-input', type='text', placeholder='Enter second team'),
    html.Button('Submit', id='submit-val', n_clicks=0),
    dcc.Dropdown(id='player-dropdown', placeholder='Select a player'),  # Dropdown for selecting player
    dcc.Graph(id='heatmap')
])

# Callback for updating the player dropdown
@app.callback(
    Output('player-dropdown', 'options'),
    [Input('submit-val', 'n_clicks')],
    [State('team1-input', 'value'),
     State('team2-input', 'value')]
)
def update_player_dropdown(n_clicks, team1, team2):
    if n_clicks > 0:
        matches = get_matches_between_teams(team1, team2)
        if not matches.empty:
            match_id = matches['match_id'].iloc[0]
            events = parser.event(match_id)[0]
            players = events['player_name'].dropna().unique()
            return [{'label': player, 'value': player} for player in players]
    return []

# Callback for updating the heatmap
@app.callback(
    Output('heatmap', 'figure'),
    [Input('player-dropdown', 'value')],
    [State('team1-input', 'value'), State('team2-input', 'value')]
)
def update_output(player_name, team1, team2):
    if player_name and team1 and team2:
        matches = get_matches_between_teams(team1, team2)
        if not matches.empty:
            match_id = matches['match_id'].iloc[0]
            events = parser.event(match_id)[0]  # Assuming you only want the first value
            player_df = events[events['player_name'] == player_name]
            fig = create_football_pitch_heatmap(player_df)
            return fig
        else:
            return go.Figure()  # Return an empty figure if no matches or player data
    else:
        return go.Figure()  # Return an empty figure if not all inputs are provided

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
