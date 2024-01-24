import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
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
competitions.head(20)

# Selecting the World Cup Final
df, df_related, df_freeze, df_tactics = parser.event(3869685)
# Players involved in the final
def getUniquePlayers():
    return df['player_name']



# Replacing some full names with famous names
replacements = {
    'Lionel Andrés Messi Cuccittini': 'Lionel Messi',
    'Rodrigo Javier De Paul': 'Rodrigo De Paul'
    # Add more replacements here
}
df['player_name'] = df['player_name'].replace(replacements)
#df2


def deriveShotMapData(playername):
    # Filter for shots by the player
    mask = (df.type_name == 'Shot') & (df.player_name == playername)
    columns = ['player_name', 'period','timestamp','minute','second','x', 'y', 'outcome_name', 'end_x', 'end_y', 'shot_statsbomb_xg', 'end_z', 'technique_id', 'technique_name', 'body_part_name', ]
    df_shots = df.loc[mask, columns]
    df_shots['shot_statsbomb_xg'] = df['shot_statsbomb_xg'].round(2)
    df_shots['Index'] = range(1, len(df_shots) + 1)
    desired_col_order = ['Index', 'player_name', 'period', 'timestamp', 'minute', 'second', 'x', 'y', 'outcome_name', 'end_x', 'end_y', 'shot_statsbomb_xg', 'end_z', 'technique_id', 'technique_name', 'body_part_name']
    df_shots = df_shots[desired_col_order]
    return df_shots  # Returning the filtered DataFrame for further use

def makePitch(PlayerNames):
    img1 = Image.open('C:/Users/20211424/Documents/Y3/Q2/Visualization/New.png')
    img = Image.open('C:/Users/20211424/Documents/Y3/Q2/Visualization/New2.png')
    
    fig = go.Figure()

    for name in PlayerNames:
        data = deriveShotMapData(name)
    
    # Process data
    data['x'] = ((data['x'] - 60) * (2/3))+2
    column_list = data['Index'].tolist()
    string_list = [str(item) for item in column_list]
    
    # Adding data to the plot
    fig.add_trace(
        go.Scatter(
            x=data['x'].values,
            y=data['y'].values,
            mode='markers+text',
            marker=dict(
                size=15,
                color=data['outcome_name'].map(
                    {'Goal': 'green', 'Off T': 'red', 'Saved': 'orange'}
                ),
            ),
            text=string_list,  # Display index numbers on data points
            textposition='middle center',
            name='Salah',
            textfont=dict(size=10),
        ))

    # Update layout for the axes and reduce margins
    fig.update_layout(
        autosize=False,
        width=588,
        height=700,
        xaxis=dict(showline=False, showgrid=False, showticklabels=False, range=[0, 42]),
        yaxis=dict(showline=False, showgrid=False, showticklabels=False, autorange='reversed', range=[0, 80]),
        yaxis_scaleanchor="x",
        yaxis_scaleratio=0.7,
        margin=dict(l=20, r=20, t=20, b=20),  # Adjust margins (left, right, top, bottom)
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

    selectData = data[['Index', 'end_y', 'end_z', 'outcome_name']]
    
    #remove this
    selectData = selectData[np.isfinite(selectData['end_y']) & np.isfinite(selectData['end_z'])]
    
    # Create the figure with the updated background color
    #fig, ax = plt.subplots(figsize=(6, 4))
    fig, ax = plt.subplots(figsize=(9, 6))  # Adjust the dimensions as needed (width, height)

    fig.patch.set_facecolor('#585454')
    ax.set_facecolor('#585454')

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

    data_point_size = 15  # You can adjust this value as needed

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
        plot_bgcolor='#585454',  # Match the background color
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

name = 'Lionel Messi'
shotData = deriveShotMapData(name)
refinedShotData = shotData.drop(columns=["timestamp", "x", "y", "end_x", "end_y", "end_z", "technique_id"])

default_pitch_fig = makePitch(['Lionel Messi'])  # Assuming makePitch returns a Plotly figure
default_shot_map_fig = generateShotMapGoal(deriveShotMapData('Lionel Messi'))


####################### PAGE LAYOUT #############################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = html.Div(children=[
    dbc.Container([
        # Row for the plots
    html.Div([
            # First plot
            html.Div(
                dcc.Graph(id='graph-output', figure=default_pitch_fig),
                style={'display': 'inline-block', 'width': '70%'}
            ),
            # Second plot
            html.Div(
                dcc.Graph(id='shot-map-image', figure=default_shot_map_fig),
                style={'display': 'inline-block', 'width': '50%'}
            )
        ], style={'display': 'flex', 'flex-direction': 'row'}),


        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='player-dropdown',
                options=[
                    {'label': 'Lionel Messi', 'value': 'Lionel Messi'},
                    {'label': 'Cristiano Ronaldo', 'value': 'Cristiano Ronaldo'},
                    # Add more player options as needed
                ],
                value='Lionel Messi'  # Default selected player
            ), width=8),
        ]),

        # Row for DataTable
        dbc.Row([
            dbc.Col(dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in refinedShotData.columns],
                data=shotData.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
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
                     'color': 'white'}
                ],
            ), width=8)
        ])
    ])
])

@app.callback(
    Output('graph-output', 'figure'),
    [Input('player-dropdown', 'value')]
)

def update_graph(selected_player):
    fig = makePitch([selected_player])
    return fig


@app.callback(
    Output('shot-map-image', 'figure'),
    [Input('player-dropdown', 'value')]
)

def update_shot_map(selected_player):
    dat = deriveShotMapData(selected_player)
    print("Data for Shot Map:", dat.head())
    plotly_fig = generateShotMapGoal(dat)
    return plotly_fig
    
@app.callback(
    Output('click-data', 'children'),
    [Input('graph-output', 'clickData')]
)
def display_click_data(clickData):
    if clickData is not None:
        return "Data point clicked!"
    return "Click on a data point to interact"