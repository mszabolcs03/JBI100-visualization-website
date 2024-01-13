import dash
from dash import html

dash.register_page(__name__, path='/', name="INTRODUCTION")

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
        html.Div(id="content", children=[
            html.Div(children=[
                html.H2("Intro"),
                "Intro",
                "ASDASD"
            ])
        ])
    
])