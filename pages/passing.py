import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from dash.dependencies import Input, Output
from mplsoccer import Pitch, Sbopen, VerticalPitch
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


from getpitch import get_pitch

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()

# Select the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)

dash.register_page(__name__, path='/passing', name="PASSING NETWORK")

# Page layout
layout = html.Div([
    html.Div(id="content", children=[
        html.H1('Passing Network Visualization'),

        html.Div(id="passing-dropdowns", children=[
            dcc.Dropdown(
                id='passing-team-dropdown',  # Corrected ID
                options=[{'label': team, 'value': team} for team in df['team_name'].unique()],
                value='Argentina'  # Default value
            )
        ]),

        dcc.Graph(
            id='passing-network-graph',
            # figure=fig,
            config={ 'modeBarButtonsToRemove': ['zoom', 'pan'] }
        )
    ])
])

# Callback to update graph based on selected team
@callback(
    Output('passing-network-graph', 'figure'),
    [Input('passing-team-dropdown', 'value')]
)
def update_graph(selected_team):
    team_id = df[df['team_name'] == selected_team]['team_id'].iloc[0]
    pass_events = df[(df['type_name'] == 'Pass') & (df['team_id'] == team_id)]

    # Calculate the average positions of each player
    average_positions = pass_events.groupby('player_id').agg({'x': 'mean', 'y': 'mean'}).reset_index()

    # Count the passes between each pair of players
    pass_counts = pass_events.groupby(['player_id', 'pass_recipient_id']).size().reset_index(name='pass_count')

    # Count the total number of passes for each player (made and received)
    player_pass_counts = pass_events['player_id'].value_counts().rename_axis('player_id').reset_index(name='passes_made')
    recipient_pass_counts = pass_events['pass_recipient_id'].value_counts().rename_axis('player_id').reset_index(name='passes_received')

    # Merge the counts and fill NaN values with 0
    player_pass_counts = player_pass_counts.merge(recipient_pass_counts, on='player_id', how='outer').fillna(0)
    player_pass_counts['total_passes'] = player_pass_counts['passes_made'] + player_pass_counts['passes_received']

    # Normalize the pass counts for coloring
    max_passes = player_pass_counts['total_passes'].max()
    player_pass_counts['color_intensity'] = player_pass_counts['total_passes'] / max_passes

    # Prepare the graph
    fig = go.Figure()


    # Adding nodes (players) to the graph
    for index, row in average_positions.iterrows():
        player_name = df[df['player_id'] == row['player_id']]['player_name'].iloc[0]
        total_passes = player_pass_counts[player_pass_counts['player_id'] == row['player_id']]['total_passes'].iloc[0]
        color_intensity = player_pass_counts[player_pass_counts['player_id'] == row['player_id']]['color_intensity'].iloc[0]
        fig.add_trace(go.Scatter(
            x=[row['x']], y=[row['y']], mode='markers+text', 
            text=player_name, 
            name=player_name,
            # textfont=dict(color='rgba(255, 255, 255)'),
            marker=dict(size=15, color=f'rgba(255, 0, 0, {color_intensity})', showscale=False),
            hoverinfo='text',
            hovertext=f'{player_name}<br>Total Passes: {total_passes}'
        ))

    # Adding edges (passes) to the graph
    max_pass_count = pass_counts['pass_count'].max()
    for index, row in pass_counts.iterrows():
     # Get the start and end positions of the pass
        start_player = average_positions[average_positions['player_id'] == row['player_id']]
        end_player = average_positions[average_positions['player_id'] == row['pass_recipient_id']]
        if not start_player.empty and not end_player.empty:
            pass_intensity = row['pass_count'] / max_pass_count
            line_width = pass_intensity * 4  # adjust multiplier for desired thickness
            fig.add_trace(go.Scatter(x=[start_player['x'].values[0], end_player['x'].values[0]], 
                                    y=[start_player['y'].values[0], end_player['y'].values[0]], 
                                    mode='lines', 
                                    line=dict(width=line_width, color=f'rgba(255, 255, 255, {pass_intensity})')))

    # Update layout
    fig.update_layout(
        showlegend=False,
        hoverlabel=dict(bgcolor="white", font_size=12),
        hovermode='closest',
        shapes = get_pitch(),
        xaxis_range=[3, 120],
        yaxis_range=[0, 80],
        margin=dict(l=2,r=2,b=0.5,t=2),
        plot_bgcolor='rgb(100, 100, 100)',
        xaxis_showgrid=False, yaxis_showgrid=False
    )
    
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(showticklabels=False, title=None)

    return fig