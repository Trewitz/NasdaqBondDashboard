from turtle import filling
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from scraper import Bond

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Nasdaq Danish Bond Dashboard'),

    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='XCSE35NYK01EDA53', type='text')
    ]),

    dcc.Graph(
        id='my-output'
    )
])

@app.callback(
    Output(component_id='my-output', component_property='figure'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    bonds_df = pd.DataFrame(columns=['Date', 'Close', 'AvgCPH', 'Id'])
    for id in input_value.split(","):
        bond = Bond(id.strip())
        bond.get_bond_data()

        bond.df['Id'] = bond.id
        bonds_df = pd.concat([bonds_df, bond.df], axis=0)

    fig = px.line(bonds_df, x="Date", y="Close", color='Id')
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

