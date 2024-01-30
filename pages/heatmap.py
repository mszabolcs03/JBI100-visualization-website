import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch
import plotly.graph_objects as go
import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
from mplsoccer import Sbopen
import plotly.graph_objects as go
from mplsoccer.pitch import Pitch
import random

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

dash.register_page(__name__, path='/heatmap', name="HEATMAP")




list_of_accepted_actions = ["Pass", 'Ball Receipt', 'Carry', 'Ball Recovery', 'Block', 'Dribble', 'Shot', 'Goal Keeper', 'Dribbled Past', 'Player Off', 'Player On', 'Substitution', 'Shield']
mask_action = df['type_name'].isin(list_of_accepted_actions)
mask_player = df['player_name'] == "Antoine Griezmann"

mask_master = mask_action & mask_player #& mask_time_min & mask_time_max

df_actions = df.loc[mask_master, ["player_name", "type_name", 'x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']]

df_actions_plus = df_actions[["x", "y"]]

fig = px.density_heatmap(df_actions[["x", "y"]], x='x', y='y', nbinsx=100, nbinsy=400, range_color=[0, 10])

# fig.update(layout_showlegend=False)
# fig.update(layout_coloraxis_showscale=False)

# fig.layout.xaxis.fixedrange = True
# fig.layout.yaxis.fixedrange = True

# fig.update_layout(shapes = get_pitch())
# fig.update_layout(xaxis_range=[0, 120])
# fig.update_layout(yaxis_range=[0, 80])
# fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
# fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
# fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

# Page layout
layout = html.Div([
    html.Div(id="content", children=[
        html.H1('Player Activity Heatmap'),

        html.Div(id="heatmap-dropdowns", children=[
            dcc.Dropdown(
                id='heatmap-team-dropdown',
                options=[{'label': "all", 'value': "all"}] + [{'label': team, 'value': team} for team in df['team_name'].unique()],
                clearable=False,
                placeholder="Select team(s)"
            ),
            dcc.Dropdown(
                id='heatmap-player-dropdown',
                options=[{'label': "all", 'value': "all"}] + [{'label': player, 'value': player} for player in df['player_name'].unique()],
                clearable=False,
                placeholder="Select player(s)"
            )
        ]),

        dcc.Graph(
            id='heatmap-graph',
            figure=fig,
            config={ 'modeBarButtonsToRemove': ['zoom', 'pan'] }
        )
    ])
])

# UPDATE PLAYER DROPDOWN
@callback(
    Output('heatmap-player-dropdown', 'options'),
    Input('heatmap-team-dropdown', 'value')
)
def update_player_dropdown(selected_team):
    if selected_team == "all":
        mask_team = df.team_name == df.team_name
    else:
        mask_team = df.team_name == selected_team

    players_in_team = [player for player in df.loc[mask_team, 'player_name'].dropna().unique()]

    print(players_in_team)
    print(type(players_in_team))

    return ["all"] + players_in_team


# Callback to update graph based on selected team
@callback(
    Output('heatmap-graph', 'figure'),
    Input('heatmap-team-dropdown', 'value'),
    Input('heatmap-player-dropdown', 'value')
)
def update_graph(selected_team, selected_player):
    list_of_accepted_actions = ["Pass", 'Ball Receipt', 'Carry', 'Ball Recovery', 'Block', 'Dribble', 'Shot', 'Goal Keeper', 'Dribbled Past', 'Player Off', 'Player On', 'Substitution', 'Shield']
    mask_action = df['type_name'].isin(list_of_accepted_actions)

    if selected_team == "all":
        mask_team = df["team_name"] == df["team_name"]
    else:
        mask_team = df["team_name"] == selected_team
    #select player
    if selected_player == "all":
        mask_player = df["player_name"] == df["player_name"]
    else:
        mask_player = df["player_name"] == selected_player

    mask_player = df['player_name'] == selected_player

    mask_master = mask_action & mask_team & mask_player

    df_actions = df.loc[mask_master, ["player_name", "type_name", 'x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']]

    length = len(df_actions[["x", "y"]])

    df_actions_plus = df_actions[["x", "y"]]
    for i in range(1000):
        df_actions_plus["x"] = df_actions_plus["x"] + random.gauss(0, 0.6)
        df_actions_plus["y"] = df_actions_plus["y"] + random.gauss(0, 0.6)
        df_actions = pd.concat([df_actions, df_actions_plus], ignore_index=True)

    fig = px.density_heatmap(
        df_actions[["x", "y"]],
        x='x',
        y='y',
        nbinsx=100,
        nbinsy=400,
        range_color=[0, length/2],
        color_continuous_scale=["rgb(80, 80, 80)", "rgb(255, 0, 0)"]
    )

    fig.update(layout_showlegend=False)
    fig.update(layout_coloraxis_showscale=False)

    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    
    fig.update_layout(hovermode='closest')
    # fig.update_layout(shapes = get_pitch())
    fig.update_layout(xaxis_range=[0, 120])
    fig.update_layout(yaxis_range=[0, 80])
    fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
    fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(showticklabels=False, title=None)

    return fig



# # Function to get matches between two teams
# def get_matches_between_teams(team1, team2):
#     # Load matches for a specific competition and season
#     match_list = parser.match(competition_id=43, season_id=3)  # Example competition and season IDs

#     # Filter for matches between the two teams
#     filtered_matches = match_list[((match_list['home_team_name'] == team1) & 
#                                   (match_list['away_team_name'] == team2)) |
#                                  ((match_list['home_team_name'] == team2) & 
#                                   (match_list['away_team_name'] == team1))]

#     return filtered_matches

# # Function to create a heatmap

# def create_heatmap(player_df):
#     # Ensure the 'actions' column exists and contains the count of actions at each (x, y) position.
#     if 'actions' not in player_df.columns:
#         player_df['actions'] = player_df.groupby(['x', 'y']).size().reset_index(name='actions')['actions']
    
#     # Generate the heatmap with the custom color scale range based on the actions.
#     fig = px.density_heatmap(player_df, x='x', y='y', z='actions', nbinsx=30, nbinsy=20,
#                              color_continuous_scale=custom_color_scale,
#                              range_color=[0, player_df['actions'].max()])
#     fig.update_layout(
#         xaxis=dict(showgrid=False, zeroline=False, scaleanchor='y', scaleratio=1, constrain='domain'),
#         yaxis=dict(showgrid=False, zeroline=False, autorange='reversed', scaleanchor='x', scaleratio=1),
#         coloraxis_colorbar=dict(title='Number of actions'),
#         plot_bgcolor='green',  # Set the background color to match the pitch
#         margin=dict(l=0, r=0, t=0, b=0),  # Remove margins to make the heatmap fit the plot area
#         paper_bgcolor='green',  # Set the paper background color to match the pitch
#         height=450, width=800  # Adjust the figure size to fit a standard soccer pitch aspect ratio
#     )
#     # Update axes ranges to cover the entire pitch area
#     fig.update_xaxes(range=[0, 100])  # Update this if your pitch size is different
#     fig.update_yaxes(range=[0, 100])   # Update this if your pitch size is different
    
#     return fig

# def get_team_options():
#     match_list = parser.match(competition_id=43, season_id=3)  # Example competition and season IDs
#     teams = sorted(set(match_list['home_team_name'].unique()) | set(match_list['away_team_name'].unique()))
#     return [{'label': team, 'value': team} for team in teams]


# # Layout of the app
# app.layout = html.Div([
#     html.H1("Soccer Match Analysis"),
#     dcc.Dropdown(id='team1-dropdown', options=get_team_options(), placeholder='Select the first team'),
#     dcc.Dropdown(id='team2-dropdown', options=get_team_options(), placeholder='Select the second team'),
#     html.Button('Submit', id='submit-val', n_clicks=0),
#     dcc.Dropdown(id='player-dropdown', placeholder='Select a player'),  # Dropdown for selecting player
#     dcc.Graph(id='heatmap')
# ])

# @app.callback(
#     Output('player-dropdown', 'options'),
#     [Input('submit-val', 'n_clicks')],
#     [State('team1-dropdown', 'value'), State('team2-dropdown', 'value')]
# )

# def update_player_dropdown(n_clicks, team1, team2):
#     if n_clicks > 0 and team1 and team2:
#         matches = get_matches_between_teams(team1, team2)
#         if not matches.empty:
#             match_id = matches['match_id'].iloc[0]
#             events = parser.event(match_id)[0]
#             players = events['player_name'].dropna().unique()
#             return [{'label': player, 'value': player} for player in players]
#     return []

# # Callback for updating the player dropdown
# @app.callback(
#     Output('player-dropdown', 'options'),
#     [Input('submit-val', 'n_clicks')],
#     [State('team1-input', 'value'),
#      State('team2-input', 'value')]
# )
# def update_output(n_clicks, team1, team2):
#     if n_clicks > 0:
#         matches = get_matches_between_teams(team1, team2)
#         if not matches.empty:
#             # Select the first match and its events as an example
#             match_id = matches['match_id'].iloc[0]
#             events = parser.event(match_id)[0]
#             player_df = events[events['player_name'] == events['player_name'].dropna().unique()[0]]  # Selecting first player as an example
#             fig = create_heatmap(player_df)
#             return fig
#         else:
#             return px.scatter()  # Return an empty plot if no matches found
#     else:
#         return px.scatter()  # Return an empty plot initially

# # Initialize Dash app
# app = dash.Dash(__name__)

# # Load the StatsBomb data
# parser = Sbopen()

# # Initialize the pitch
# pitch = Pitch(line_color='white', pitch_color='green')

# # Function to create a heatmap with a football pitch background
# def create_football_pitch_heatmap(player_df):
#     # Check if 'player_df' is not empty and contains 'x' and 'y' columns
#     if not player_df.empty and 'x' in player_df.columns and 'y' in player_df.columns:
#         # Normalize the 'x' and 'y' values to fit the pitch size
#         player_df['x'] = player_df['x'] / 120 * 100  # Assuming 'x' is already in the range [0, 120]
#         player_df['y'] = player_df['y'] / 80 * 100  # Assuming 'y' is already in the range [0, 80]

#         # Create a density heatmap for a smooth heatmap
#         fig = px.density_heatmap(player_df, x='x', y='y', nbinsx=30, nbinsy=30, color_continuous_scale=custom_color_scale)

#         # Add pitch markings
#         fig.update_layout(
#             plot_bgcolor=pitch_green_hex,
#             paper_bgcolor=pitch_green_hex,
#             xaxis=dict(showgrid=False, zeroline=False, scaleanchor='y', scaleratio=5, range=[0, 100]),
#             yaxis=dict(showgrid=False, zeroline=False, autorange='reversed', range=[0, 100]),
#             margin=dict(l=20, r=20, t=20, b=20)
#         )

#         # Center circle and halfway line
#         fig.add_shape(type="circle",
#                       xref="x", yref="y",
#                       x0=50 - 9.15, y0=50 - 9.15,
#                       x1=50 + 9.15, y1=50 + 9.15,
#                       line_color="white")
#         fig.add_shape(type="rect",
#                       xref="paper", yref="paper",
#                       x0=0, y0=0, x1=1, y1=1,
#                       line=dict(color="white", width=2)),
#     fig.add_shape(type="line",
#                       x0=50, y0=0,
#                       x1=50, y1=100,
#                       line_color="white")

#         # Penalty areas, etc. can be added similarly using fig.add_shape

#     return fig
        
# # Layout of the app
# app.layout = html.Div([
#     html.H1("Soccer Match Analysis"),
#     dcc.Input(id='team1-input', type='text', placeholder='Enter first team'),
#     dcc.Input(id='team2-input', type='text', placeholder='Enter second team'),
#     html.Button('Submit', id='submit-val', n_clicks=0),
#     dcc.Dropdown(id='player-dropdown', placeholder='Select a player'),  # Dropdown for selecting player
#     dcc.Graph(id='heatmap')
# ])

# # Callback for updating the player dropdown
# @app.callback(
#     Output('player-dropdown', 'options'),
#     [Input('submit-val', 'n_clicks')],
#     [State('team1-input', 'value'),
#      State('team2-input', 'value')]
# )
# def update_player_dropdown(n_clicks, team1, team2):
#     if n_clicks > 0:
#         matches = get_matches_between_teams(team1, team2)
#         if not matches.empty:
#             match_id = matches['match_id'].iloc[0]
#             events = parser.event(match_id)[0]
#             players = events['player_name'].dropna().unique()
#             return [{'label': player, 'value': player} for player in players]
#     return []

# # Callback for updating the heatmap
# @app.callback(
#     Output('heatmap', 'figure'),
#     [Input('player-dropdown', 'value')],
#     [State('team1-input', 'value'), State('team2-input', 'value')]
# )
# def update_output(player_name, team1, team2):
#     if player_name and team1 and team2:
#         matches = get_matches_between_teams(team1, team2)
#         if not matches.empty: 
#             match_id = matches['match_id'].iloc[0]
#             events = parser.event(match_id)[0]  # Assuming you only want the first value
#             player_df = events[events['player_name'] == player_name]
#             fig = create_football_pitch_heatmap(player_df)
#             return fig
#         else:
#             return go.Figure()  # Return an empty figure if no matches or player data
#     else:
#         return go.Figure()  # Return an empty figure if not all inputs are provided