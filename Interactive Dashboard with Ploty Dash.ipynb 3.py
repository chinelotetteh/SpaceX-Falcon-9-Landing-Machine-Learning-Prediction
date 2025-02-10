# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites for dropdown
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown for Launch Site Selection
    html.Label("Select Launch Site:"),
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Default selection
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie Chart for Successful Launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Range Slider for Payload Selection
    html.Label("Select Payload Range (kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={0: '0 kg', 2500: '2500 kg', 5000: '5000 kg', 7500: '7500 kg', 10000: '10000 kg'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter Chart for Payload vs. Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# CALLBACK 1: Update Pie Chart Based on Selected Launch Site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Count total successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Success Count']
        
        # Create pie chart with all launch sites
        fig = px.pie(success_counts, 
                     names='Launch Site', 
                     values='Success Count', 
                     title='Total Successful Launches for All Sites')
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        
        # Count success and failure for the selected site
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        
        # Create pie chart with success vs. failure
        fig = px.pie(success_fail_counts, 
                     names='class', 
                     values='count', 
                     title=f'Success vs. Failure for {selected_site}')
    
    return fig

# CALLBACK 2: Update Scatter Chart Based on Selected Launch Site & Payload Range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Further filter based on launch site selection
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df, 
        x="Payload Mass (kg)", 
        y="class", 
        color="Booster Version Category",
        title=f"Payload vs. Success for {selected_site if selected_site != 'ALL' else 'All Sites'}",
        labels={"class": "Launch Outcome"}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
