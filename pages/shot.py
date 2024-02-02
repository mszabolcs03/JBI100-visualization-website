import pandas as pd
import dash
from dash import Dash, dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output, State
from mplsoccer import Pitch, Sbopen, VerticalPitch
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as path_effects
from matplotlib.colors import to_rgba
import matplotlib.patches as mpatches
from PIL import Image
import plotly.graph_objects as go
import plotly.tools as tls
import dash_table
import dash_bootstrap_components as dbc
from matplotlib.widgets import RadioButtons

dash.register_page(__name__, path='/shot', name="SHOT ANALYSIS")

####################### LOAD DATASET #############################
# Load the dataset
parser = Sbopen()
competitions = parser.competition()
#competitions.head(20)

world_cup = competitions[competitions['competition_name'] == 'FIFA World Cup']
world_cup_id = world_cup['competition_id'].iloc[0]
season_id = world_cup['season_id'].iloc[0]

matches = parser.match(competition_id=world_cup_id, season_id = season_id)

argentina_matches = matches[(matches['home_team_country_name'] == 'Argentina') | (matches['away_team_country_name'] == 'Argentina')]
selected_data = argentina_matches[['match_id', 'home_team_country_name', 'away_team_country_name']]

# Convert 'match_id' to numeric
selected_data['match_id'] = pd.to_numeric(selected_data['match_id'])
selected_data = selected_data.sort_values(by='match_id', ascending=False)
selected_data.iloc[0], selected_data.iloc[2] = selected_data.iloc[2].copy(), selected_data.iloc[0].copy()

dataframes = []

index = 0
for index, row in selected_data.iterrows():    
    df, df_related, df_freeze, df_tactics = parser.event(row['match_id'])
    dataframes.append(df)

# Selecting the World Cup Final

#df, df_related, df_freeze, df_tactics = parser.event(3869685)


# Players involved in the final
def getUniquePlayers():
    return df['player_name']

# Replacing some full names with famous names
#replacements = {
#    'Lionel Andrés Messi Cuccittini': 'Lionel Messi',
#    'Rodrigo Javier De Paul': 'Rodrigo De Paul'
#    # Add more replacements here
#}
#df['player_name'] = df['player_name'].replace(replacements)

team_lists = {}
argentina_player_names = df[(df['team_name'] == 'Argentina') & (df['player_name'].notna())]['player_name'].unique().tolist()
team_lists['Argentina_Player_Names'] = argentina_player_names
dropdown_options = [{'label': name, 'value': name} for name in argentina_player_names]

def deriveShotMapData(indices, playername):
    all_shots = []  # List to store shot data from each DataFrame

    for index in reversed(indices):
        # Make sure the index is within the range of 'dataframes' list
        if index < len(dataframes):
            df = dataframes[index]  # Get DataFrame from the list

            other_team_name = df.loc[df['team_name'] != 'Argentina', 'team_name'].drop_duplicates().values[0]

            # Filter for shots by the player
            mask = (df.type_name == 'Shot') & (df.player_name == playername)
            columns = ['player_name', 'period', 'timestamp', 'minute', 'second', 'x', 'y', 'outcome_name', 'end_x', 'end_y', 'shot_statsbomb_xg', 'end_z', 'technique_id', 'technique_name', 'body_part_name']
            df_shots = df.loc[mask, columns]
            df_shots['shot_statsbomb_xg'] = df_shots['shot_statsbomb_xg'].round(2)
            df_shots['Index'] = 10#range(1, len(df_shots) + 1)
            df_shots['Opponent'] = other_team_name
            desired_col_order = ['Index', 'Opponent', 'player_name', 'period', 'timestamp', 'minute', 'second', 'x', 'y', 'outcome_name', 'end_x', 'end_y', 'shot_statsbomb_xg', 'end_z', 'technique_id', 'technique_name', 'body_part_name']
            df_shots = df_shots[desired_col_order]

            all_shots.append(df_shots)

    # Concatenate all the DataFrames in the list
    combined_df = pd.concat(all_shots, ignore_index=True)

    combined_df['Index'] = range(1, len(combined_df) + 1)

    return combined_df

def makePitch(indices, playername):
    img = Image.open('pages/New2.png')
    #img2 = Image.open('pages/Shot-Pitch.png')

    fig = go.Figure()

    data = deriveShotMapData(indices, playername)
    
    # Process data
    data['x'] = ((data['x'] - 60) * (2/3)) + 2
    
    #data['new_x'] = data['y']  # New x-coordinate is the original y-coordinate
    #data['new_y'] = -(((data['x'] - 60) * (2/3)) + 2)  # New y-coordinate is the inverted transformed original x-coordinate
    
    data['hover_text'] = 'Minute: ' + data['minute'].astype(str)  # Create a hover text column
    string_list = [str(item) for item in data['Index'].tolist()]

    # Adding data to the plot
    fig.add_trace(
        go.Scatter(
            x=data['x'].values,
            y=data['y'].values,
            mode='markers+text',
            marker=dict(
                size=25,  # Increase the size of the dots
                color=data['outcome_name'].map(
                    {'Goal': 'green', 'Off T': 'red', 'Saved': 'orange'}
                ),
            ),
            text=string_list,  # Display index numbers on data points
            textposition='middle center',
            name='Argentina',
            textfont=dict(
                size=20,
                color='white'  # Set the text color to white
            ),
            hoverinfo='text',  # Use custom text for hover info
            hovertext=data['hover_text']  # Custom hover text from the DataFrame
        ))

    # Update layout for the axes and reduce margins
    fig.update_layout(
        autosize=False,
        width=588,
        height=700,
        xaxis=dict(
            showline=False, 
            showgrid=False, 
            showticklabels=False, 
            range=[0, 42], 
            visible=False,  # Hide x-axis
            fixedrange=True  # Disable zoom and pan for x-axis
        ),
        yaxis=dict(
            showline=False, 
            showgrid=False, 
            showticklabels=False, 
            autorange='reversed', 
            range=[0, 80], 
            visible=False,  # Hide y-axis
            fixedrange=True  # Disable zoom and pan for y-axis
        ),
        yaxis_scaleanchor="x",
        yaxis_scaleratio=0.7,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='#414042',
        paper_bgcolor='#414042'
    )
    
    # Add background image
    fig.add_layout_image(
        dict(source=img,
             xref='x',
             yref='y',
             x=0,
             y=0,
             sizex=42,
             sizey=80,
             sizing='contain',
             opacity=0.9,
             layer='below')
    )
    return fig

def generateShotMapGoal(data):
    # Coordinates of the goalpost with extended bottom line
    x_bottom = [25, 60]  # Extend the bottom line beyond the posts
    y_bottom = [0, 0]
    x_left = [36, 36]
    y_left = [0, 2.66]
    x_right = [44, 44]
    y_right = [0, 2.66]
    x_top = [36, 44]
    y_top = [2.66, 2.66]

    selectData = data[['Index', 'end_y', 'end_z', 'outcome_name', 'minute']]

    #remove this
    selectData = selectData[np.isfinite(selectData['end_y']) & np.isfinite(selectData['end_z'])]
    
    # Create the figure with the updated background color
    #fig, ax = plt.subplots(figsize=(6, 4))
    fig, ax = plt.subplots(figsize=(9, 6))  # Adjust the dimensions as needed (width, height)

    fig.patch.set_facecolor('#414042')
    ax.set_facecolor('#414042')

    # Plotting the goalpost with thicker white lines
    linewidth_goalpost = 3  # Increase the linewidth for the goalpost
    ax.plot(x_bottom, y_bottom, 'w-', linewidth=linewidth_goalpost)
    ax.plot(x_left, y_left, 'w-', linewidth=linewidth_goalpost)
    ax.plot(x_right, y_right, 'w-', linewidth=linewidth_goalpost)
    ax.plot(x_top, y_top, 'w-', linewidth=linewidth_goalpost)

    ax.set_xlim(33, 47)
    ax.set_ylim(-0.2, 4)
    ax.set_title("Goalpost", color='white')
    ax.set_aspect('equal')

    # Remove the axes, axis labels, and grid
    ax.axis('off')

    data_point_size = 25  # You can adjust this value as needed

    # Enumerate and plot the data points with colored labels
    for index, row in selectData.iterrows():
        if row['outcome_name'] == 'Goal':
            color = 'green'
        elif row['outcome_name'] == 'Off T':
            color = 'red'
        elif row['outcome_name'] == 'Saved':
            color = 'orange'
        else:
            color = 'blue'

        ax.plot(row['end_y'], row['end_z'], 'o', color=color, markersize=data_point_size)  # Adjust marker size here
        ax.text(row['end_y'], row['end_z'], str(int(row['Index'])), ha='center', va='bottom', color='white', fontsize=data_point_size)

    # Convert to a Plotly figure
    plotly_fig = tls.mpl_to_plotly(fig)

    # Update Plotly figure layout for equal axis and to remove axes, ticks, and grid
    plotly_fig.update_layout(
        plot_bgcolor='#414042',  # Match the background color
        xaxis=dict(
            visible=False,  # Hide X-axis
            showgrid=False,  # No grid lines
            showticklabels=False,  # No tick labels
            scaleanchor='y',  # Ensure equal scaling with y-axis
            scaleratio=1,  # 1:1 aspect ratio
        ),
        yaxis=dict(
            visible=False,  # Hide Y-axis
            showgrid=False,  # No grid lines
            showticklabels=False,  # No tick labels
        ),
        margin=dict(l=0, r=0, t=0, b=0),  # Remove margins
    )

    return plotly_fig

def deriveTableData(indices,name):
    table2 = deriveShotMapData(indices, name)
    table2 = table2.drop(columns=["timestamp", "x", "y", "end_x", "end_y", "end_z", "technique_id"])
    return table2

name = 'Julián Álvarez'
shotData = deriveShotMapData([0,1,2,3,4,5,6], name)
refinedShotData = shotData.drop(columns=["timestamp", "x", "y", "end_x", "end_y", "end_z", "technique_id"])

default_pitch_fig = makePitch([0, 1, 2, 3, 4, 5, 6], 'Julián Álvarez')  # Assuming makePitch returns a Plotly figure
default_shot_map_fig = generateShotMapGoal(deriveShotMapData([0,1,2,3,4,5,6],'Julián Álvarez'))

team_data = {'France':'Final',
              'Croatia' : 'Semi-Final',
              'Netherlands' : 'Quarter-Final',
              'Australia' : 'Round of 16',
              'Poland' : 'Group Stage: Game 3',
              'Mexico' : 'Group Stage: Game 2',
              'Saudi Arabia' : 'Group Stage: Game 1'}
table_data = [{'team': team, 'stage': stage} for team, stage in team_data.items()]

####################### PAGE LAYOUT #############################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = html.Div(children=[
    dbc.Container([
        html.H1(id='heading', children=f"Shot Map for: {name}", style={'text-align': 'center'}),

        html.Div([
            html.Div([
                html.H2("Location of taken shots"),
                dcc.Graph(id='graph-output', figure = default_pitch_fig)],
                style={'display': 'inline-block', 'width': '40%', 'height': '30%', 'marginLeft': '10%'}
            ),
            html.Div([
                html.H3("Placement of taken shots"),
                dcc.Graph(id='shot-map-image', figure=default_shot_map_fig)],
                style={'display': 'inline-block', 'width': '40%' ,'height': '30%'}
            )
        ], style={'display': 'flex', 'flex-direction': 'row'}),

        # Row for the existing DataTable
        html.Div([
            dbc.Row([
                dbc.Col(html.Div(
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in refinedShotData.columns],
                        data=shotData.to_dict('records'),
                        fixed_rows={'headers': True},  # Enable fixed header row
                        style_table={
                            'overflowX': 'auto', 
                            'overflowY': 'auto',
                            'maxHeight': '300px'
                        },
                        style_header={
                            'backgroundColor': '#414042',  # Dark grey background color
                            'fontWeight': 'bold',
                            'color': 'white'  # Optional: change text color to white for contrast
                        },
                        style_cell={
                            'textAlign': 'center',
                            'minWidth': '50px',
                            'maxWidth': '100px',
                            'fontSize': '14px'
                        },
                         style_data_conditional=[
                            {'if': {'row_index': 'odd'},
                             'backgroundColor': 'rgb(248, 248, 248)'},
                            {'if': {'column_id': 'Goals'},
                             'fontWeight': 'bold',
                             'backgroundColor': 'rgb(255, 204, 204)'},
                            {'if': {'filter_query': '{outcome_name} eq "Goal"'},
                             'backgroundColor': 'rgba(34, 139, 34, 0.5)',
                             'color': 'white'},
                            {'if': {'filter_query': '{outcome_name} eq "Off T"'},
                             'backgroundColor': 'rgba(255, 0, 0, 0.5)',
                             'color': 'white'},
                            {'if': {'filter_query': '{outcome_name} eq "Saved"'},
                             'backgroundColor': 'rgba(255, 165, 0, 0.5)',
                             'color': 'white'},
                            {'if': {'filter_query': '{outcome_name} eq "Blocked"'},
                             'backgroundColor': 'rgba(0, 0, 0, 0)',
                             'color': 'white'},
                            {'if': {'filter_query': '{outcome_name} eq "Wayward"'},
                             'backgroundColor': 'rgba(0, 0, 0, 0)',
                             'color': 'white'}

                        ],
                    ), style={'display': 'inline-block', 'width': '100%'}), width=12)
            ])
,
            html.Div(
                dbc.Row([
                    dbc.Col(
                        dash_table.DataTable(
                            id='team-table',
                            columns=[
                                {'name': 'Team', 'id': 'team'},
                                {'name': 'Stage', 'id': 'stage'}
                            ],
                            data=table_data,
                            editable=True,
                            row_selectable='multi',
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'center',
                                'color': 'black',  # Text color set to black
                                'backgroundColor': 'white',  # Background color set to white
                                'minWidth': '80px', 'maxWidth': '350px', 'fontSize': '14px'
                            },
                        ),
                        width=6
                    )
                ])  # End of dbc.Row
            ),

            html.Div(id='selected-indices', style={'display': 'none'}),

            html.Div(
                dcc.Dropdown(
                id='simple-dropdown',
                options=dropdown_options,  # Updated options
                value=argentina_player_names[0] if argentina_player_names else None,
                style={'color': 'black', 'width': '300px'}  # Add this style attribute to the dropdown
                )
            ),

            html.Button("Generate graphs", id='my-button'),

            html.Div(id='dropdown-output2'),

        ], style={'display': 'flex', 'flex-direction': 'row'}),

    ]),
])

#Callback for table output selectab
@callback(
    Output('selected-indices', 'children'),
    Input('team-table', 'selected_rows')
)
def update_selected_indices(selected_rows):
    # 'selected_rows' will be a list of selected row indices
    return str(selected_rows)  # Convert the list to a string for display

# Callback for Dropdown
@callback(
    Output('dropdown-output1', 'children'),
    Input('simple-dropdown', 'value')
)
def update_output(value):
    #print(f'Selected value: {value}')
    return f'You have selected {value}'

# Callback for Button to regenerate plots

@callback(
    [Output('graph-output', 'figure'),
     Output('shot-map-image', 'figure')],
    [Input('my-button', 'n_clicks'),
     State('simple-dropdown', 'value')
     ,State('selected-indices', 'children')]
)
def on_button_click(n_clicks, selected_name, selected_indices):
    if n_clicks:
        selected_indices = [int(idx) for idx in selected_indices.strip('[]').split(', ') if idx.isdigit()]
        pitch_fig = makePitch(selected_indices, selected_name)
        shot_map_fig = generateShotMapGoal(deriveShotMapData(selected_indices, selected_name))
        
        return pitch_fig, shot_map_fig
    
@callback(
    Output('table', 'data'),
    Input('my-button', 'n_clicks'),  # Trigger on button click
    State('simple-dropdown', 'value'),
    State('selected-indices', 'children')  # Current value of the dropdown
)
def update_table_on_button_click(n_clicks, selected_name, selected_indices):
    if n_clicks:
        if selected_name is None:
            # Handle the case where no player is selected
            return [refinedShotData]  # Return empty data or some default data

        # Assuming deriveTableData returns the new data for the selected player
        #new_data = deriveTableData(deriveTableData, selected_name)
        new_data = deriveTableData([0,1,2,3,4,5,6], selected_name)

        # Check if new_data is empty
        if new_data.empty:
            # Create a new dataframe or dictionary with a row of zeros
            # Adjust the columns according to your data structure
            columns = ['Column1', 'Column2', 'Column3']  # Replace with actual column names
            zero_data = pd.DataFrame([[0] * len(columns)], columns=columns)
            return zero_data.to_dict('records')

        return new_data.to_dict('records')
    else:
        return dash.no_update  # Keep the table unchanged if the button is not clicked

@callback(
    Output('heading', 'children'),
    Input('my-button', 'n_clicks'),
    State('simple-dropdown', 'value')
)
def update_heading(n_clicks, selected_name):
    if n_clicks:
        return f"Shot Map for: {selected_name}"
    else:
        return dash.no_update