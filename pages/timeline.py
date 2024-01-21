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



dash.register_page(__name__, path='/timeline', name="DYNAMIC PLAY TIMELINE")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)


##################
initial_player_name = "Gonzalo Ariel Montiel"
list_of_accepted_actions = ["Pass", 'Dribble', 'Shot', 'Shield']
list_of_required_colums = ['type_name', 'x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']

#filter actions
mask_action = df['type_name'].isin(list_of_accepted_actions)
#select player
mask_player = df.player_name == initial_player_name
#filter time
mask_time_min = df.minute >= -1
mask_time_max = df.minute <= 1000
#combine filters
mask_master = mask_action & mask_player & mask_time_min & mask_time_max
#get filtered dataframe
df_actions = df.loc[mask_master, list_of_required_colums]

#create figure
fig = px.scatter(
    df_actions,
    x='x',
    y='y',
    hover_data=['type_name', 'minute', 'second']
)

arrows = []
for x0,y0,x1,y1 in zip(df_actions["end_x"], df_actions["end_y"], df_actions["x"], df_actions["y"]):
    arrow = go.layout.Annotation(dict(
                    x=x0,
                    y=y0,
                    xref="x", yref="y",
                    showarrow=True,
                    axref="x", ayref='y',
                    ax=x1,
                    ay=y1,
                    arrowhead=2,
                    arrowwidth=2,
                    arrowcolor='rgb(50,50,0)',)
                )
    arrows.append(arrow)

fig.update_layout(hovermode='closest')
fig.update_layout(annotations=arrows)
fig.update_layout(xaxis_range=[3, 120])
fig.update_layout(yaxis_range=[0, 80])

fig.update_xaxes(showticklabels=False, title=None)
fig.update_yaxes(showticklabels=False, title=None)



####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[

        dcc.Dropdown(
            id='timeline-team-dropdown',
            options=[{'label': "all", 'value': "all"}] + [{'label': team, 'value': team} for team in df['team_name'].unique()],
            clearable=False,
            style={"width": "60%"}
        ),
        dcc.Dropdown(
            id='timeline-player-dropdown',
            options=[{'label': "all", 'value': "all"}] + [{'label': player, 'value': player} for player in df['player_name'].unique()],
            # value=initial_player_name,
            clearable=False,
            style={"width": "60%"}
        ),

        dcc.Graph(
            id='pitch-figure-timeline',
            figure=fig,
            # config={ 'modeBarButtonsToRemove': ['zoom', 'pan'], 'staticPlot': True }
        ),

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

# UPDATE PLAYER DROPDOWN
@callback(
    Output('timeline-player-dropdown', 'options'),
    Input('timeline-team-dropdown', 'value')
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

# UPDATE SLIDER MARKS
@callback(
    Output('timeline-min-slider', 'marks'),
    Output('timeline-max-slider', 'marks'),
    Input('timeline-player-dropdown', 'value')
)
def update_slider_range(selected_player):
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

    start_time = int(df.loc[mask_player & mask_action].minute.min())
    end_time = int(df.loc[mask_player & mask_action].minute.max())

    print(start_time)
    print(end_time)

    marks={
        start_time: {'label': 'start'},
        end_time: {'label': 'end'},
    }
    return marks, marks

# UPDATE FIGURE
@callback(
    Output('pitch-figure-timeline', 'figure'),
    Input('timeline-team-dropdown', 'value'),
    Input('timeline-player-dropdown', 'value'),
    Input('timeline-min-slider', 'value'),
    Input('timeline-max-slider', 'value')
)
def update_graph(selected_team, selected_player, min_time, max_time):
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
        hover_data=['type_name', 'minute', 'second']
    )

    arrows = []
    for x0,y0,x1,y1 in zip(df_actions["end_x"], df_actions["end_y"], df_actions["x"], df_actions["y"]):
        arrow = go.layout.Annotation(dict(
            x=x0,
            y=y0,
            xref="x", yref="y",
            showarrow=True,
            axref="x", ayref='y',
            ax=x1,
            ay=y1,
            arrowhead=2,
            arrowwidth=2,
            arrowcolor='rgb(50,50,0)',)
        )
        arrows.append(arrow)
    
    fig.update_layout(hovermode='closest')
    fig.update_layout(annotations=arrows)
    fig.update_layout(xaxis_range=[3, 120])
    fig.update_layout(yaxis_range=[0, 80])

    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(showticklabels=False, title=None)

    return fig