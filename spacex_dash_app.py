import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Create a minimal dummy DataFrame for demonstration
spacex_df = pd.DataFrame({
    'Launch Site': [
        'CCAFS LC-40', 'VAFB SLC-4E', 'CCAFS LC-40',
        'KSC LC-39A', 'CCAFS SLC-40', 'KSC LC-39A'
    ],
    'class': [
        1, 0, 1,
        1, 0, 1
    ],
    'Payload Mass (kg)': [
        500, 3000, 7000,
        9000, 4000, 1000
    ],
    'Booster Version Category': [
        'Falcon 9', 'Falcon Heavy', 'Falcon 9',
        'Falcon 9', 'Falcon Heavy', 'Falcon 9'
    ]
})

# Define min/max payload for the slider
min_payload = 0
max_payload = 10000

# Initialize the app
app = dash.Dash(__name__)

# TASK 1: Add a Launch Site Drop-down Input Component
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # A graph for the pie chart (Task 2)
    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    # TASK 3: Add a RangeSlider to select payload mass range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # A second graph for the scatter chart (Task 4)
    dcc.Graph(id='success-payload-scatter-chart')
])

# TASK 2: Callback to render pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Pie chart of total success launches by site
        fig = px.pie(
            data_frame=spacex_df,
            names='Launch Site',
            values='class',  # 'class' is success/failure in 1/0
            title='Total Success Launches By Site'
        )
        return fig
    else:
        # Filter the dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Compute success/fail counts
        filtered_df = filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')
        fig = px.pie(
            data_frame=filtered_df,
            names='class',
            values='class count',
            title=f'Total Success Launches for site {entered_site}'
        )
        return fig

# TASK 4: Callback to render scatter plot based on selected site & payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    # Extract the lower and upper range from the slider
    low, high = payload_range
    
    # Filter the DataFrame by payload mass
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        title = 'Correlation between Payload and Success for All Sites'
    else:
        # Further filter by the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Correlation between Payload and Success for Site {entered_site}'
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
