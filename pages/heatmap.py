import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch


#dash.register_page(__name__, path='/heatmap', name="ACTIVITY HEATMAP")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[

    ])
])

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

pitch_green_rgb = (30, 122, 0)  # Example RGB values
pitch_green_hex = '#{:02x}{:02x}{:02x}'.format(*pitch_green_rgb)
custom_color_scale = [(0, pitch_green_hex), (1, 'red')]

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
    # Ensure the 'actions' column exists and contains the count of actions at each (x, y) position.
    if 'actions' not in player_df.columns:
        player_df['actions'] = player_df.groupby(['x', 'y']).size().reset_index(name='actions')['actions']
    
    # Generate the heatmap with the custom color scale range based on the actions.
    fig = px.density_heatmap(player_df, x='x', y='y', z='actions', nbinsx=30, nbinsy=20,
                             color_continuous_scale=custom_color_scale,
                             range_color=[0, player_df['actions'].max()])
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, scaleanchor='y', scaleratio=1, constrain='domain'),
        yaxis=dict(showgrid=False, zeroline=False, autorange='reversed', scaleanchor='x', scaleratio=1),
        coloraxis_colorbar=dict(title='Number of actions'),
        plot_bgcolor='green',  # Set the background color to match the pitch
        margin=dict(l=0, r=0, t=0, b=0),  # Remove margins to make the heatmap fit the plot area
        paper_bgcolor='green',  # Set the paper background color to match the pitch
        height=450, width=800  # Adjust the figure size to fit a standard soccer pitch aspect ratio
    )
    # Update axes ranges to cover the entire pitch area
    fig.update_xaxes(range=[0, 100])  # Update this if your pitch size is different
    fig.update_yaxes(range=[0, 100])   # Update this if your pitch size is different
    
    return fig

def get_team_options():
    match_list = parser.match(competition_id=43, season_id=3)  # Example competition and season IDs
    teams = sorted(set(match_list['home_team_name'].unique()) | set(match_list['away_team_name'].unique()))
    return [{'label': team, 'value': team} for team in teams]


# Layout of the app
app.layout = html.Div([
    html.H1("Soccer Match Analysis"),
    dcc.Dropdown(id='team1-dropdown', options=get_team_options(), placeholder='Select the first team'),
    dcc.Dropdown(id='team2-dropdown', options=get_team_options(), placeholder='Select the second team'),
    html.Button('Submit', id='submit-val', n_clicks=0),
    dcc.Dropdown(id='player-dropdown', placeholder='Select a player'),  # Dropdown for selecting player
    dcc.Graph(id='heatmap')
])

@app.callback(
    Output('player-dropdown', 'options'),
    [Input('submit-val', 'n_clicks')],
    [State('team1-dropdown', 'value'), State('team2-dropdown', 'value')]
)

def update_player_dropdown(n_clicks, team1, team2):
    if n_clicks > 0 and team1 and team2:
        matches = get_matches_between_teams(team1, team2)
        if not matches.empty:
            match_id = matches['match_id'].iloc[0]
            events = parser.event(match_id)[0]
            players = events['player_name'].dropna().unique()
            return [{'label': player, 'value': player} for player in players]
    return []

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

# Function to create a heatmap with a football pitch background
def create_football_pitch_heatmap(player_df):
    # Check if 'player_df' is not empty and contains 'x' and 'y' columns
    if not player_df.empty and 'x' in player_df.columns and 'y' in player_df.columns:
        # Normalize the 'x' and 'y' values to fit the pitch size
        player_df['x'] = player_df['x'] / 120 * 100  # Assuming 'x' is already in the range [0, 120]
        player_df['y'] = player_df['y'] / 80 * 100  # Assuming 'y' is already in the range [0, 80]

        # Create a density heatmap for a smooth heatmap
        fig = px.density_heatmap(player_df, x='x', y='y', nbinsx=30, nbinsy=30, color_continuous_scale=custom_color_scale)

        # Add pitch markings
        fig.update_layout(
            plot_bgcolor=pitch_green_hex,
            paper_bgcolor=pitch_green_hex,
            xaxis=dict(showgrid=False, zeroline=False, scaleanchor='y', scaleratio=5, range=[0, 100]),
            yaxis=dict(showgrid=False, zeroline=False, autorange='reversed', range=[0, 100]),
            margin=dict(l=20, r=20, t=20, b=20)
        )

        # Center circle and halfway line
        fig.add_shape(type="circle",
                      xref="x", yref="y",
                      x0=50 - 9.15, y0=50 - 9.15,
                      x1=50 + 9.15, y1=50 + 9.15,
                      line_color="white")
        fig.add_shape(type="rect",
                      xref="paper", yref="paper",
                      x0=0, y0=0, x1=1, y1=1,
                      line=dict(color="white", width=2)),
    fig.add_shape(type="line",
                      x0=50, y0=0,
                      x1=50, y1=100,
                      line_color="white")

        # Penalty areas, etc. can be added similarly using fig.add_shape

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
"""

# Run the app
#if __name__ == '__main__':
    #app.run_server(debug=True)
