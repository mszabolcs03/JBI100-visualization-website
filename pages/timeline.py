import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch
from mplsoccer.pitch import Pitch
from plotly.tools import mpl_to_plotly
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback

from getpitch import get_pitch

dash.register_page(__name__, path='/timeline', name="DYNAMIC PLAY TIMELINE")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# select world cup
world_cup = competitions[competitions['competition_name'] == 'FIFA World Cup']
world_cup_id = world_cup['competition_id'].iloc[0]
season_id = world_cup['season_id'].iloc[0]

# get list of matches
matches = parser.match(competition_id=world_cup_id, season_id = season_id)

# get list of match names
match_names = []
for i in range(len(matches)):
    match_names.append(str(matches.loc[i]["home_team_country_name"] + " vs. " + matches.loc[i]["away_team_country_name"]))

# choose match
chosen_match_id = matches[(matches["home_team_country_name"] == match_names[0].split(" ")[0]) & (matches["away_team_country_name"] == match_names[0].split(" ")[2])]["match_id"][0]

#create df of chosen match
df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

##################
list_of_accepted_actions = ["Pass", 'Dribble', 'Shot', 'Shield']
list_of_required_colums = ['type_name', 'x', 'y', 'end_x', 'end_y', "player_name", 'minute', 'second', "team_name"]

mask_player = df.player_name == ""

df_actions = df[list_of_required_colums]

#create base figure
fig = px.scatter(
    df.loc[mask_player, list_of_required_colums],
    x='x',
    y='y'
)

fig.update_layout(hovermode='closest')
fig.update_layout(shapes = get_pitch())
fig.update_layout(xaxis_range=[3, 120])
fig.update_layout(yaxis_range=[0, 80])
fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

fig.update_xaxes(showticklabels=False, title=None)
fig.update_yaxes(showticklabels=False, title=None)



####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[
        html.H1('Dynamic Play Timeline'),

        html.Div(id="timeline-dropdowns", children=[
            dcc.Dropdown(
                id='timeline-match-dropdown',
                options=[
                    {'label': match, 'value': match} for match in match_names
                ],
                clearable=False,
                placeholder="Select match"
            ),
            dcc.Dropdown(
                id='timeline-team-dropdown',
                options=[{'label': "all", 'value': "all"}] + [{'label': team, 'value': team} for team in df['team_name'].unique()],
                clearable=False,
                placeholder="Select team(s)"
            ),
            dcc.Dropdown(
                id='timeline-player-dropdown',
                options=[{'label': "all", 'value': "all"}] + [{'label': player, 'value': player} for player in df['player_name'].unique()],
                clearable=False,
                placeholder="Select player(s)"
            )
        ]),

        dcc.Graph(
            id='pitch-figure-timeline',
            figure=fig,
            config={ 'modeBarButtonsToRemove': ['zoom', 'pan'] }
            # 'layout': go.Layout(
            #     xaxis={'title': 'x-axis','fixedrange':True},
            #     yaxis={'title': 'y-axis','fixedrange':True}
            # )
        ),

        html.Div(id="timeline-sliders", children=[
            dcc.Slider(
                min=0, 
                max=df["minute"].max(),
                id='timeline-min-slider',
                marks={
                    0: {'label': 'start'},
                    int(df["minute"].max()): {'label': 'end'},
                },
                step=1,
                value=df_actions["minute"].min(),
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Slider(
                min=0, 
                max=df["minute"].max(),
                id='timeline-max-slider',
                marks={
                    0: {'label': 'start'},
                    int(df["minute"].max()): {'label': 'end'},
                },
                step=1,            value=df_actions["minute"].max(),
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])
    ])
])

# UPDATE TEAM DROPDOWN
@callback(
    Output('timeline-team-dropdown', 'options'),
    Input('timeline-match-dropdown', 'value')
)
def update_team_dropdown(selected_match_name):
    print(selected_match_name)

    chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]

    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    teams_in_match = [team for team in df["team_name"].dropna().unique()]

    return teams_in_match

# UPDATE PLAYER DROPDOWN
@callback(
    Output('timeline-player-dropdown', 'options'),
    Input('timeline-match-dropdown', 'value'),
    Input('timeline-team-dropdown', 'value')
)
def update_player_dropdown(selected_match_name, selected_team):
    chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    if selected_team == "all":
        mask_team = df.team_name == df.team_name
    else:
        mask_team = df.team_name == selected_team

    players_in_team = [player for player in df.loc[mask_team, 'player_name'].dropna().unique()]

    print(players_in_team)
    print(type(players_in_team))

    return ["all"] + players_in_team

# UPDATE SLIDER MARKS
@callback(
    Output('timeline-min-slider', 'marks'),
    Output('timeline-max-slider', 'marks'),
    Input('timeline-match-dropdown', 'value'),
    Input('timeline-player-dropdown', 'value')
)
def update_slider_range(selected_match_name, selected_player):
    chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    if selected_player == None:
        return {0: {'label': 'start'}, df["minute"].max(): {'label': 'end'}}, {0: {'label': 'start'}, df["minute"].max(): {'label': 'end'}}
    #filter actions
    mask_action = df['type_name'].isin(list_of_accepted_actions)
    #select player
    if selected_player == "all":
        mask_player = df.player_name == df.player_name
    else:
        mask_player = df.player_name == selected_player
    #combine filters
    mask_master = mask_action & mask_player
    #get filtered dataframe

    print(selected_player)

    start_time = int(df.loc[mask_master].minute.min())
    end_time = int(df.loc[mask_master].minute.max())

    print(start_time)
    print(end_time)

    marks={
        start_time: {'label': 'start'},
        end_time: {'label': 'end'}
    }
    return marks, marks

# UPDATE FIGURE
@callback(
    Output('pitch-figure-timeline', 'figure'),
    Input('timeline-match-dropdown', 'value'),
    Input('timeline-team-dropdown', 'value'),
    Input('timeline-player-dropdown', 'value'),
    Input('timeline-min-slider', 'value'),
    Input('timeline-max-slider', 'value')
)
def update_graph(selected_match_name, selected_team, selected_player, min_time, max_time):
    chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    #filter actions
    mask_action = df['type_name'].isin(list_of_accepted_actions)
        #select team
    if selected_team == "all":
        mask_team = df.team_name == df.team_name
    else:
        mask_team = df.team_name == selected_team
    #select player
    if selected_player == "all":
        mask_player = df.player_name == df.player_name
    else:
        mask_player = df.player_name == selected_player
    #filter time
    mask_time_min = df.minute >= min_time
    mask_time_max = df.minute <= max_time
    #combine filters
    mask_master = mask_action & mask_team & mask_player & mask_time_min & mask_time_max
    #get filtered dataframe
    df_actions = df.loc[mask_master, list_of_required_colums]
    
    #create figure
    fig = px.scatter(
        df_actions,
        x='x',
        y='y',
        hover_data=["player_name", "team_name", 'type_name', 'minute', 'second'],
    )
    
    
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    
    fig.update_layout(hovermode='closest')
    fig.update_layout(annotations = get_arrows(df_actions, chosen_match_id))
    fig.update_layout(shapes = get_pitch())
    fig.update_layout(xaxis_range=[3, 120])
    fig.update_layout(yaxis_range=[0, 80])
    fig.update_layout(margin=dict(l=2,r=2,b=0.5,t=2))
    fig.update_layout(plot_bgcolor='rgb(80, 80, 80)')
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)

    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(showticklabels=False, title=None)

    fig.update_traces(marker=dict(color='black'))

    return fig

def get_arrows(df_actions, chosen_match_id):
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    arrows = []

    for i in range(len(df_actions["x"])):
        # df_actions.iloc[i]
        if df_actions.iloc[i]["team_name"] == df["team_name"].dropna().unique()[0]:
            arrow_color = "rgb(8, 129, 197)"
        else:
            arrow_color = "rgb(252, 184, 39)"

        arrow = go.layout.Annotation(dict(
            x=df_actions.iloc[i]["end_x"],
            y=df_actions.iloc[i]["end_y"],
            xref="x",
            yref="y",
            showarrow=True,
            axref="x",
            ayref='y',
            ax=df_actions.iloc[i]["x"],
            ay=df_actions.iloc[i]["y"],
            arrowhead=2,
            arrowwidth=2.5,
            arrowcolor=arrow_color
        ))
        arrows.append(arrow)
    return arrows

def get_pitch():
    pitch = []
    pitch.append({
            'type': 'rect',
            'x0': 0,
            'x1': 25,
            'y0': 13,
            'y1': 66.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 0,
            'x1': 10.5,
            'y0': 27.5,
            'y1': 52,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 2,
            'x1': 3.5,
            'y0': 35,
            'y1': 44.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgb(255,255,255)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 98.5,
            'x1': 121,
            'y0': 13,
            'y1': 66.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 112.5,
            'x1': 121,
            'y0': 27.5,
            'y1': 52,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 119.5,
            'x1': 121,
            'y0': 35,
            'y1': 44.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgb(255,255,255)"
    })
    pitch.append({
            'type': 'rect',
            'x0': 61.5,
            'x1': 61.5,
            'y0': 0,
            'y1': 100,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'circle',
            'x0': 49.5,
            'x1': 73.5,
            'y0': 27.5,
            'y1': 52,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'circle',
            'x0': 0,
            'x1': 5,
            'y0': -2.5,
            'y1': 2.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'circle',
            'x0': 117.5,
            'x1': 122.5,
            'y0': -2.5,
            'y1': 2.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
        'type': 'circle',
        'x0': 0,
        'x1': 5,
        'y0': 77.5,
        'y1': 82.5,
        'xref': 'x',
        'yref': 'y',
        'line': {'color': "rgb(255,255,255)"},
        'fillcolor': "rgba(0,0,0,0)"
    })
    pitch.append({
            'type': 'circle',
            'x0': 117.5,
            'x1': 122.5,
            'y0': 77.5,
            'y1': 82.5,
            'xref': 'x',
            'yref': 'y',
            'line': {'color': "rgb(255,255,255)"},
            'fillcolor': "rgba(0,0,0,0)"
    })

    return pitch