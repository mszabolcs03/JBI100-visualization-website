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

from getpitch import get_pitch

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

fig = px.density_heatmap(
    df_actions[["x", "y"]],
    x='x',
    y='y',
    nbinsx=1,
    nbinsy=1,
    range_color=[0, 10],
    color_continuous_scale=["rgb(80, 80, 80)", "rgb(80, 80, 80)"]
)

fig.update(layout_showlegend=False)
fig.update(layout_coloraxis_showscale=False)

fig.update_layout(shapes = get_pitch())
fig.update_layout(xaxis_range=[3, 120])
fig.update_layout(yaxis_range=[0, 80])
fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

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
    fig.update_layout(shapes = get_pitch())
    fig.update_layout(xaxis_range=[3, 120])
    fig.update_layout(yaxis_range=[0, 80])
    fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
    fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(showticklabels=False, title=None)

    return fig