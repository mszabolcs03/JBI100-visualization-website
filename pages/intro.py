import dash
from dash import html, dcc

dash.register_page(__name__, path='/', name="INTRODUCTION")

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
        html.Div(id="content", children=[
            html.Div(children=[
                html.H2("Introduction"),
                html.Div(
                    id="link",
                    children=[
                        dcc.Link("Dataset", href="/dataset")
                    ]
                ),
                "The dataset page gives us an overview of the data we our visualizations are based on. It is based on the 2022 FIFA World cup,"

            ])
        ])
    
])