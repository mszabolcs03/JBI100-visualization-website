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

#filter actions
mask_action = (df.type_name == "Pass") | (df.type_name == "Shot") | (df.type_name == "Carry")
#select player
mask_player = df.player_name == initial_player_name
#filter time
mask_time_min = df.minute > -1
mask_time_max = df.minute < 1000
#combine filters
mask_master = mask_action & mask_player & mask_time_min & mask_time_max
#get filtered dataframe
df_actions = df.loc[mask_master, ['x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']]

print(df_actions["minute"].min(), df_actions["minute"].max())

fig = px.scatter(x=df_actions['x'], y=df_actions['y'])

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
fig.update_layout(annotations=arrows)



####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Div(id="content", children=[

        dcc.Dropdown(
            id='timeline-player-dropdown',
            options=[{'label': player, 'value': player} for player in df['player_name'].unique()],
            # value=initial_player_name,
            clearable=False,
            style={"width": "60%"}
        ),

        dcc.Graph(
            id='pitch-figure-timeline',
            figure=fig,
            config={ 'modeBarButtonsToRemove': ['zoom', 'pan'], 'staticPlot': True }
        ),

        dcc.Slider(
            min=0, 
            max=df["minute"].max(),
            id='timeline-min-slider',
            marks={
                int(df_actions["minute"].min()): {'label': 'start', 'style': {'color': '#77b0b1'}},
                int(df_actions["minute"].max()): {'label': 'end'},
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
                int(df_actions["minute"].min()): {'label': 'start', 'style': {'color': '#77b0b1'}},
                int(df_actions["minute"].max()): {'label': 'end'},
            },
            step=1,            value=df_actions["minute"].max(),
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ])
])

# UPDATE FIGURE
@callback(
    Output('pitch-figure-timeline', 'figure'),
    Input('timeline-player-dropdown', 'value'),
    Input('timeline-min-slider', 'value'),
    Input('timeline-max-slider', 'value')
)
def update_graph(selected_player, min_time, max_time):
    #filter actions
    mask_action = (df.type_name == "Pass") | (df.type_name == "Shot") | (df.type_name == "Carry")
    #select player
    mask_player = df.player_name == selected_player
    #filter time
    mask_time_min = df.minute > min_time
    mask_time_max = df.minute < max_time
    #combine filters
    mask_master = mask_action & mask_player & mask_time_min & mask_time_max
    #get filtered dataframe
    df_actions = df.loc[mask_master, ['x', 'y', 'end_x', 'end_y', 'pass_height_id', 'minute', 'second']]
    
    print(min_time, max_time)

    # fig = px.scatter(x=df_actions['x'], y=df_actions['y'])
    fig = px.scatter(df_actions, x='x', y='y')

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
    

    fig.update_layout(annotations=arrows)
    fig.update_layout(xaxis_range=[0, 100])
    fig.update_layout(yaxis_range=[0, 100])


    return fig

# UPDATE SLIDER MARKS
# callback(
#     Output('timeline-min-slider', 'marks'),
#     Input('timeline-player-dropdown', 'value')
# )
# def update_slider_range(selected_player):
#     # # Filter DataFrame based on the selected player
#     # player_data = df_actions[df_actions['player_name'] == selected_player]

#     # # Calculate the min and max values for the slider based on the filtered DataFrame
#     # min_value = player_data['minute'].min()
#     # max_value = player_data['minute'].max()

#     # return min_value, max_value
#     print("slider range changed")