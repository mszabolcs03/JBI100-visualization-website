import dash
from dash import html, dcc

dash.register_page(__name__, path='/', name="INTRODUCTION")

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
        html.Div(id="content", children=[
            html.Div(children=[
                html.H2("Introduction"),
                
                dcc.Link("DATASET", href="/dataset", className="link"),

                html.Div(className="intro-paragraph", children=[
                    '''
                    For our visualisation of the 2022 FIFA World Cup, we have used a StatsBombs dataset. You can gain more information about the dataset by following this link: https://statsbomb.com/news/statsbomb-release-free-2022-world-cup-data/ 
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    We have four visualisations you can interact with. 
                    '''
                ]),
                
                dcc.Link("PASSING NETWORK", href="/passing", className="link"),
                html.Div(className="intro-paragraph", children=[
                    '''
                    When first loaded, an empty football field should be present on the left side, and on the right side, there should be two selectable drop-downs. By the use of a drop-down, the user can pick out to their liking which matches they would like to view and then pick out one of the teams to show the passing network for it on the right. 
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    Players are represented as nodes. The positions are calculated based on the average position of the player when passing. We have decided to use monochromatic colour and correlate the colour intensity with the number of passes made compared to its teammates. 
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    The edges between nodes represent the passes between two players. The higher the frequency of the number of passes made, the wider the edge is between those two players. 
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    When you hover your mouse over a node, an information box will appear on the passing network. It will provide you with extra information such as the player's full name, the total number of passes made, time played during the game, and the ratio of passes made per minute. 
                    '''
                ]),

                dcc.Link("ACTIVITY HEATMAP", href="/heatmap", className="link"),
                html.Div(className="intro-paragraph", children=[
                    '''
                    The activity heatmap is a crucial tool in football analytics, providing coaches with a comprehensive overview of player movement dynamics throughout the game. Our interactive tool translates locational data into an intuitive visualization that aids coaches in understanding player movement patterns.
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    We are using a color spectrum that ranges from transparent to green, effectively showing the frequency of a given player's presence in different areas. From our data we have obtained the 'x' and 'y' coordinates of each action taken during a game.
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    Our heatmap is interactive, allowing the user to select a specific match from the 2022 FIFA World Cup through the dropdown menu. The first dropdown allows the user to select a match, with the second dropdown a team can be selected from the match, and finally, with the last dropdown, the user can select a specific player from that team.
                    '''
                ]),

                dcc.Link("SHOT ANALYSIS", href="/shot", className="link"),
                html.Div(className="intro-paragraph", children=[
                    '''
                    The shot analysis allows the user to select a player whose shots they would like to visualise, with an option to select the games the user is interested in. There is a corresponding table, showing all the shots of the selected player, letting the user decide which shots will be of interest to be visualised.
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    The visualisation includes two views of the shots, one being an aerial view of the location of the taken shot, and the second the placement of said shots. The two visualisations and table are colour coded, and indexed, with each index identifying a shot, and the colour identifying the outcome of the shot.
                    '''
                ]),

                dcc.Link("DYNAMIC PLAY TIMELINE", href="/shot", className="link"),
                html.Div(className="intro-paragraph", children=[
                    '''
                    The dynamic play timeline visualizes the passes and shots occurring in a game, consisting of 3 main sections: an aerial view of the football pitch, a dropdown menu to select the match, team, and player(s) of which the actions are to be visualized, and sliders to select the timeframe.
                    '''
                ]),
                html.Div(className="intro-paragraph", children=[
                    '''
                    In the selected timeframe, all passes and shots or any other kind of activity are represented by arrows on the football field, color-coded to indicate whether the team playing on the left side (blue) or the team on the right side (orange) possesses the ball. The start position of the arrows indicate the starting position of the action, the length indicates the distance the ball has traveled in the resulting pass or shot, and the angle represents the direction of the action.
                    '''
                ]),



                html.Div(className="intro-paragraph", children=['''‎''']),
                html.Div(className="intro-paragraph", children=['''‎''']),
                html.Div(className="intro-paragraph", children=['''‎''']),
                html.Div(className="intro-paragraph", children=['''‎''']),
                html.Div(className="intro-paragraph", children=['''‎'''])
            ])
        ])
    
])