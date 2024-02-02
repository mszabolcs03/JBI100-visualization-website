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

# choose default match
chosen_match_id = matches[(matches["home_team_country_name"] == match_names[0].split(" ")[0]) & (matches["away_team_country_name"] == match_names[0].split(" ")[2])]["match_id"][0]

#create df of chosen match
df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)



dash.register_page(__name__, path='/passing', name="PASSING NETWORK")

# Page layout
layout = html.Div([
    html.Div(id="content", children=[
        html.H1('Passing Network Visualization'),

        html.Div(id="passing-dropdowns", children=[
            dcc.Dropdown(
                id='passing-match-dropdown',
                options=[
                    {'label': match, 'value': match} for match in match_names
                ],
                clearable=False,
                placeholder="Select match"
            ),
            dcc.Dropdown(
                id='passing-team-dropdown',  # Corrected ID
                options=[{'label': team, 'value': team} for team in df['team_name'].unique()],
                # value='Argentina'  # Default value
            )
        ]),

        dcc.Graph(
            id='passing-network-graph',
            # figure=fig,
            config={ 'modeBarButtonsToRemove': ['zoom', 'pan'] }
        )
    ])
])

# UPDATE TEAM DROPDOWN
@callback(
    Output('passing-team-dropdown', 'options'),
    Input('passing-match-dropdown', 'value')
)
def update_team_dropdown(selected_match_name):
    #print(selected_match_name)

    try:
        chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]
    except:
        chosen_match_id = 3869685 #default
    
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    teams_in_match = [team for team in df["team_name"].dropna().unique()]

    return teams_in_match

# Callback to update graph based on selected team


name_mapping = {
    'Nahuel Molina Lucero': 'N. Molina',
    'Rodrigo Javier De Paul': 'R. De Paul',
    'Cristian Gabriel Romero': 'C. Romero',
    'Nicolás Hernán Otamendi': 'N. Otamendi',
    'Nicolás Alejandro Tagliafico': 'N. Tagliafico',
    'Alexis Mac Allister': 'A. Mac Allister',
    'Damián Emiliano Martínez': 'D. Martínez',
    'Lionel Andrés Messi Cuccittini': 'L. Messi',
    'Ángel Fabián Di María Hernández': 'Á. Di María',
    'Julián Álvarez': 'J. Álvarez',
    'Enzo Fernandez': 'E. Fernandez',
    'Marcos Javier Acuña': 'M. Acuña',
    'Gonzalo Ariel Montiel': 'G. Montiel',
    'Lautaro Javier Martínez': 'L. Martínez',
    'Leandro Daniel Paredes': 'L. Paredes',
    'Paulo Bruno Exequiel Dybala': 'P. Dybala',
    'Germán Alejandro Pezzella': 'G. Pezzella'
}

@callback(
    Output('passing-network-graph', 'figure'),
    Input('passing-match-dropdown', 'value'),
    Input('passing-team-dropdown', 'value')
)
def update_graph(selected_match_name, selected_team):
    try:
        chosen_match_id = matches[(matches["home_team_country_name"] == selected_match_name.split(" ")[0]) & (matches["away_team_country_name"] == selected_match_name.split(" ")[2])]["match_id"].values[0]
    except:
        chosen_match_id = 3869685 #default match
    
    df, df_related, df_freeze, df_tactics = parser.event(chosen_match_id)

    try:
        team_id = df[df['team_name'] == selected_team]['team_id'].iloc[0]
    except:
        team_id = 0 #default team id

    if selected_team == 'Argentina':
        df['player_name'] = df['player_name'].map(name_mapping).fillna(df['player_name'])

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
    annotations = []
    subs = ['M. Acuña','G. Montiel','L. Martínez','L. Paredes', 'P. Dybala', 'G. Pezzella']

    for index, row in average_positions.iterrows():
        player_name = df[df['player_id'] == row['player_id']]['player_name'].iloc[0]
        
        total_passes = player_pass_counts[player_pass_counts['player_id'] == row['player_id']]['total_passes'].iloc[0]
        color_intensity = player_pass_counts[player_pass_counts['player_id'] == row['player_id']]['color_intensity'].iloc[0]

        # Adding player node
        fig.add_trace(go.Scatter(
            x=[row['x']], y=[row['y']],
            mode='markers',
            marker=dict(size=15, color=f'rgba(255, 0, 0, {color_intensity})', showscale=False),
            hoverinfo='text',
            hovertext=f'{player_name}<br>Total Passes: {total_passes}',
        ))

        # Adding annotation for player name
        annotations.append(dict(
            x=row['x'], y=row['y'],
            xref="x", yref="y",
            text=player_name,
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
            textangle=0,
            xanchor='center', yanchor='bottom'  # Adjust the positioning
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
        annotations=annotations,
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