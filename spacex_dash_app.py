# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                             options=launch_sites, placeholder="Select a Launch Site",
                                             value='ALL',
                                             searchable=True,
                                             style={"width": "99%", "fontSize": "20px", "textAlignLast": "center",
                                                    "padding": "3px"}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000,
                                                marks={i:str(i) for i in range(0, 11000, 1000)},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df.groupby(['Launch Site']).sum().reset_index()
        fig = px.pie(filtered_df, values=filtered_df['class'],
                     names=filtered_df['Launch Site'],
                     title='Total Success Launches by Site')
        return fig
    else:
        #filtered_df = spacex_df.groupby(['Launch Site', 'class']).agg(launch_count=pd.NamedAgg(column='class', aggfunc='count')).reset_index()
        filtered_df = spacex_df[['Launch Site', 'class']].value_counts().reset_index(name='counts')
        df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.pie(df, values=df['counts'],
                     names=df['class'],
                     title=f'Success Rate of {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
# Add computation to callback function and return graph
def get_scatter(launch_site, payload_range):
    # Select data
    if launch_site == 'ALL':
        df = spacex_df[(spacex_df['Payload Mass (kg)']<=payload_range[1])&(payload_range[0]<=spacex_df['Payload Mass (kg)'])]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        return fig
    else:
        df = spacex_df[
            (spacex_df['Payload Mass (kg)'] <= payload_range[1]) & (payload_range[0] <= spacex_df['Payload Mass (kg)']) & (spacex_df['Launch Site']==launch_site)]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        return fig
# Run the app
if __name__ == '__main__':
    app.run_server()
