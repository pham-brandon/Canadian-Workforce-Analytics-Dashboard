import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# Data loading and preprocessing
df = pd.read_csv("dataset.csv")
df = df[df['Province'] != 'Canada'].copy()
df['NOC'] = df['Occupation'].str.extract(r'^(\d)')
df['NOC Label'] = df['Occupation'].where(df['NOC'].notna(), None)
provinces = sorted(df['Province'].unique())

# Initialize the app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Canadian Workforce Analytics Dashboard"}
    ]
)
app.title = "Canadian Workforce Analytics Dashboard"
load_figure_template("flatly")

server = app.server
app.layout = dbc.Container([
    # Page header
    dbc.Row([
        dbc.Col([
            html.H1("Canadian Workforce Analytics Dashboard", className="text-center my-4"),
            html.P("Exploring employment trends and workforce distribution across Canadian provinces and territories.", 
                  className="text-center text-muted mb-5")
        ], width=12)
    ]),
    
    # Essential Services Section
    dbc.Card([
        dbc.CardHeader(html.H3("Essential Services Distribution", className="mb-0")),
        dbc.CardBody([
            dcc.RadioItems(
                id='service-dropdown',
                options=[
                    {'label': ' Nurses', 'value': 'nurse'},
                    {'label': ' Police Officers', 'value': 'police'},
                    {'label': ' Firefighters', 'value': 'firefighter'}
                ],
                value='nurse',
                inline=True,
                className="mb-3",
                inputClassName="me-2",
                labelClassName="mx-3"
            ),
            dcc.Loading(
                id="loading-essential",
                type="circle",
                children=[dcc.Graph(id='essential-service-graph')]
            )
        ])
    ], className="mb-4"),
    
    # Gender and NOC Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Gender Distribution by Occupation", className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Province:", className="form-label"),
                            dcc.Dropdown(
                                id='province-dropdown',
                                options=[{'label': prov, 'value': prov} for prov in provinces],
                                value='Ontario',
                                clearable=False,
                                className="mb-3"
                            )
                        ], md=6)
                    ]),
                    dcc.Loading(
                        id="loading-gender",
                        type="circle",
                        children=[dcc.Graph(id='gender-noc-graph')]
                    )
                ])
            ], className="mb-4")
        ], md=6),
        
        # Engineering Workforce Section
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H3("Engineering Workforce Availability", className="mb-0")),
                dbc.CardBody([
                    html.Label("Select Engineer Types:", className="form-label"),
                    dbc.Checklist(
                        id='engineer-checklist',
                        options=[
                            {'label': ' Computer Engineers', 'value': '21311'},
                            {'label': ' Electrical Engineers', 'value': '21310'},
                            {'label': ' Mechanical Engineers', 'value': '21301'},
                            {'label': ' Total Engineers', 'value': 'total'}
                        ],
                        value=['21311', '21310', '21301', 'total'],
                        inline=False,
                        switch=True,
                        className="mb-3"
                    ),
                    dcc.Loading(
                        id="loading-engineering",
                        type="circle",
                        children=[dcc.Graph(id='engineering-graph')]
                    )
                ])
            ])
        ], md=6)
    ], className="mb-4"),
    
    # Popular Occupations Section
    dbc.Card([
        dbc.CardHeader([
            html.H3("Most Popular Occupations by Province/Territory", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Province:", className="form-label"),
                    html.Div([
                        dcc.Tabs(
                            id='province-tabs',
                            value='Ontario',
                            children=[dcc.Tab(
                                label=prov,
                                value=prov,
                                className="px-2 py-1 mx-1",
                                selected_className="fw-bold border-bottom border-primary",
                                style={
                                    'whiteSpace': 'nowrap',
                                    'display': 'inline-block',
                                    'minWidth': 'max-content',
                                    'padding': '0.5rem 0.75rem'
                                }
                            ) for prov in provinces],
                            className="mb-3",
                            style={
                                'display': 'flex',
                                'flexWrap': 'wrap',
                                'borderBottom': 'none',
                                'gap': '0.25rem',
                                'rowGap': '0.5rem',
                                'alignItems': 'center',
                                'justifyContent': 'flex-start'
                            }
                        )
                    ], style={'width': '100%'})
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-occupations",
                        type="circle",
                        children=[dcc.Graph(id='occupations-graph')]
                    )
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Data Source: ",
                html.A("Statistics Canada", href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810040401", target="_blank")
            ], className="text-center text-muted")
        ])
    ])
], fluid=True, className="p-4")


# Service name mapping
SERVICE_NAMES = {
    'nurse': 'Nurses',
    'police': 'Police Officers',
    'firefighter': 'Firefighters'
}

@app.callback(
    Output('essential-service-graph', 'figure'),
    Input('service-dropdown', 'value')
)
def update_essential_services(selected_service):
    # Process data
    filtered_df = df[
        df['Occupation'].str.contains(selected_service, case=False) & 
        (df['Gender'] == 'Total')
    ]
    grouped = filtered_df.groupby('Province', as_index=False, observed=True)['Employment'].sum()
    
    # Create and return figure
    fig = px.bar(
        grouped,
        x='Province',
        y='Employment',
        title=f"Distribution of {SERVICE_NAMES[selected_service]} by Province",
        labels={'Employment': 'Number of Workers'},
        color='Employment',
        color_continuous_scale='Blues',
        text_auto=True,
        height=500
    )
    
    # Update layout and traces
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        title_x=0.5,
        title_font=dict(size=18),
        xaxis=dict(title='', tickangle=45, showgrid=False),
        yaxis=dict(title='Number of Workers', showgrid=True, gridcolor='#f0f0f0'),
        coloraxis_showscale=False
    ).update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.8
    )
    
    return fig


@app.callback(
    Output('gender-noc-graph', 'figure'),
    Input('province-dropdown', 'value')
)
def update_gender_noc(province):
    # Process data
    df_noc = df[
        (df['Gender'].isin(['Men', 'Women'])) &
        (df['NOC'].notna()) &
        (df['Province'] == province)
    ]
    
    # Create a mapping of NOC codes to their labels (concise version)
    noc_mapping = {
        '0': 'Management',
        '1': 'Business & Finance',
        '2': 'Natural & Applied Sciences',
        '3': 'Healthcare',
        '4': 'Education & Government',
        '5': 'Arts & Culture',
        '6': 'Sales & Service',
        '7': 'Trades & Transport',
        '8': 'Natural Resources',
        '9': 'Manufacturing'
    }
    
    # Add NOC label column
    df_noc['NOC_Label'] = df_noc['NOC'].astype(str).str[0].map(noc_mapping)
    
    # Group by NOC label and gender
    grouped = df_noc.groupby(['NOC_Label', 'Gender'], as_index=False)['Employment'].sum()
    
    # Create figure
    figure2 = px.bar(
        grouped,
        x='NOC_Label',
        y='Employment',
        color='Gender',
        barmode='group',
        title=f"Gender Distribution by NOC in {province}",
        labels={
            'Employment': 'Number of Workers', 
            'NOC_Label': 'NOC Major Group',
            'Gender': 'Gender'
        },
        color_discrete_map={"Men": "#3498db", "Women": "#e74c3c"},
        height=600
    )
    
    # Update layout with more vertical spacing
    figure2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=80, b=100),
        title=dict(
            text=f"Gender Distribution by NOC in {province}",
            x=0.5,
            font=dict(size=18),
            y=0.95,  # Position title lower
            yanchor='top',
            pad=dict(b=20)  # Add padding below title
        ),
        xaxis=dict(
            title='NOC Major Group',
            showgrid=False,
            tickangle=45,
            tickfont=dict(size=11),  # Slightly larger font
            automargin=True  # Prevents label cutoff
        ),
        yaxis=dict(
            title='Number of Workers',
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.45,  # Move legend below x-axis labels
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#ddd',
            borderwidth=1
        )
    )
    
    # Update y-axis to show properly formatted numbers
    figure2.update_yaxes(
        tickformat=',.0f',  # Add thousand separators
        title='Number of Workers',
        showgrid=True,
        gridcolor='#f0f0f0',
        gridwidth=0.5
    )
    
    # Update traces to use Plotly's built-in short number formatting
    figure2.update_traces(
        texttemplate='%{y:.3s}',  # Built-in short number formatting (K, M, etc.)
        textposition='outside',
        marker_line_color='rgba(0,0,0,0.1)',
        marker_line_width=1,
        opacity=0.9,
        textfont_size=10,
        hovertemplate='<b>%{x}</b><br>%{data.name}: %{y:,.0f}<extra></extra>',
        textfont=dict(family='Arial', size=10, color='#333')
    )
    
    return figure2


@app.callback(
    Output('engineering-graph', 'figure'),
    Input('engineer-checklist', 'value')
)
def update_engineer_graph(selected_nocs):
    # Process data
    show_total = 'total' in selected_nocs
    # Filter out 'total' from the patterns since it's not an occupation code
    patterns = [code for code in selected_nocs if code != 'total']
    
    if not patterns and not show_total:
        # If nothing is selected, return an empty figure
        return px.density_heatmap(
            pd.DataFrame(columns=['Province', 'Engineer Type', 'Employment']),
            x='Province',
            y='Engineer Type',
            z='Employment',
            color_continuous_scale='Teal',
            title="Engineering Workforce Availability by Province"
        )
    
    # Filter data based on selected engineer types
    if patterns:
        pattern = '|'.join(patterns)
        df_engineer = df.loc[df['Occupation'].str.contains(pattern) & (df['Gender'] == 'Total')].copy()
    else:
        df_engineer = df[df['Gender'] == 'Total'].copy()
    
    def engineer_type(occupation):
        if occupation == '21311 Computer engineers (except software engineers and designers)':
            return 'Computer Engineers'
        elif occupation == '21301 Mechanical engineers':
            return 'Mechanical Engineers'
        elif occupation == '21310 Electrical and electronics engineers':
            return 'Electrical Engineers'
        return None  # Exclude non-engineering occupations
    
    # Add engineer type and filter out non-engineering occupations
    df_engineer.loc[:, 'Engineer Type'] = df_engineer['Occupation'].apply(engineer_type)
    df_engineer = df_engineer.dropna(subset=['Engineer Type'])  # Remove non-engineering occupations
    
    # Create grouped data by province and engineer type
    grouped = df_engineer.groupby(['Province', 'Engineer Type'], as_index=False)['Employment'].sum()
    
    # Prepare data for visualization
    if show_total:
        # Calculate totals for each province if total is selected
        totals = df_engineer.groupby('Province', as_index=False)['Employment'].sum()
        totals['Engineer Type'] = 'Total Engineers'
        
        if patterns:
            # If specific types are selected, show both individual and total
            combined = pd.concat([grouped, totals])
        else:
            # If only total is selected, show only total
            combined = totals
    else:
        # If total is not selected, show only selected types
        combined = grouped
    
    # Create figure
    figure3 = px.density_heatmap(
        combined,
        x='Province',
        y='Engineer Type',
        z='Employment',
        color_continuous_scale='Teal',
        title="Engineering Workforce Availability by Province",
        labels={'Employment': 'Number of Engineers'},
        text_auto=True,
        height=500
    )
    
    # Update layout with adjusted margins for colorbar
    figure3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=150, t=40, b=20),  # Increased right margin for colorbar
        title_x=0.5,
        title_font=dict(size=18),
        xaxis=dict(
            title='',
            side="bottom"
        ),
        yaxis=dict(
            title='',
            autorange="reversed"
        ),
        coloraxis_colorbar=dict(
            title='Number of Engineers',
            thicknessmode="pixels", 
            thickness=20,
            lenmode="pixels", 
            len=300,
            yanchor="top", 
            y=0.95,  # Slightly lower than top
            xanchor="left",  # Changed from right to left
            x=1.02,  # Position just outside the plot
            outlinewidth=1,
            outlinecolor='#ddd'
        )
    )
    
    # Update traces with custom hover template
    figure3.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y} Engineers: %{z:,.0f}<extra></extra>',
        texttemplate='%{z:.2s}',
        textfont={"size": 12, "color": "black"}
    )
    
    # Update colorbar to show short form numbers
    figure3.update_coloraxes(colorbar_tickformat='.2s')
    
    return figure3


@app.callback(
    Output('occupations-graph', 'figure'),
    Input('province-tabs', 'value')
)
def update_occupations(province):
    print(f"\nProcessing data for province: {province}")
    
    # Process data
    df_t4 = df[
        (df['Province'] == province) &
        (df['Gender'] == 'Total')
    ]
    print(f"Found {len(df_t4)} rows for {province}")
    
    # Check if we have data for the selected province
    if df_t4.empty:
        print(f"No data found for province: {province}")
        # Return an empty figure with a message
        return {
            'data': [],
            'layout': {
                'title': f'No data available for {province}',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'No data available',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }
    
    # Group and sort the data
    occupations = df_t4.groupby('Occupation', as_index=False)['Employment'].sum()
    print(f"Found {len(occupations)} unique occupations")
    
    # Check if we have any data after grouping
    if occupations.empty:
        print("No data available after grouping")
        return {
            'data': [],
            'layout': {
                'title': f'No occupation data available for {province}',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'No occupation data available',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }
    
    # Sort and get top 15 occupations
    occupations = occupations.sort_values(by='Employment', ascending=False).head(15)
    print(f"Top occupation: {occupations.iloc[0]['Occupation']} with {occupations.iloc[0]['Employment']} workers")
    
    # Extract NOC code (first digit of the occupation code)
    occupations['NOC'] = occupations['Occupation'].str.extract(r'^([0-9])')
    print(f"NOC codes found: {occupations['NOC'].unique().tolist()}")
    
    # Create display labels (without NOC code and truncated to 3 words)
    def create_display_label(occupation):
        # Remove NOC code if present
        if ' ' in occupation:
            occupation = ' '.join(occupation.split(' ')[1:])
        
        # Clean up common patterns
        occupation = occupation.replace('Occupations in ', '')
        occupation = occupation.replace('Occupations related to ', '')
        occupation = occupation.replace(' in manufacturing and utilities', '')
        occupation = occupation.replace(' and other services', '')
        occupation = occupation.replace(' and related support services', '')
        
        # Replace comma-space with ' and ' for better readability
        occupation = occupation.replace(', ', ' and ')
        
        # Take first 3 words max
        words = occupation.split()[:3]
        
        # Remove trailing 'and' or comma from the last word
        if words:
            last_word = words[-1].rstrip(',')
            if last_word.lower() == 'and':
                words = words[:-1]  # Remove the 'and' word
            elif last_word.endswith(','):
                words[-1] = last_word.rstrip(',')
            else:
                words[-1] = last_word
        
        # Special cases for specific labels
        if len(words) == 2 and words[0].lower() == 'education':
            return 'Education'
            
        # Special case for Legislative and Senior -> Legislative and Senior Management
        if 'Legislative and Senior'.lower() in ' '.join(words).lower():
            return 'Legislative and Senior Management'
            
        # Special case for Health Occupations -> Health
        if 'Health Occupations'.lower() in ' '.join(words).lower():
            return 'Health'
        
        # Join words and capitalize all words except 'and'
        result = ' '.join(word.capitalize() if word.lower() != 'and' else 'and' for word in ' '.join(words).split())
        
        # Special case for parentheses
        if '(' in result and ')' in result:
            # Find text in parentheses and capitalize it
            start = result.find('(') + 1
            end = result.find(')')
            if start < end:
                parenthesized = result[start:end]
                result = result[:start] + parenthesized.capitalize() + result[end:]
                
        return result
    
    # Add display labels to the dataframe
    occupations['Display_Label'] = occupations['Occupation'].apply(create_display_label)
    
    # Define NOC labels for better visualization
    noc_labels = {
        '0': 'Management',
        '1': 'Business, finance and administration',
        '2': 'Natural and applied sciences',
        '3': 'Health',
        '4': 'Education, law and social services',
        '5': 'Art, culture and recreation',
        '6': 'Sales and service',
        '7': 'Trades, transport and equipment',
        '8': 'Natural resources and agriculture',
        '9': 'Manufacturing and utilities'
    }
    
    # Create a simplified treemap without NOC grouping first
    try:
        print("Creating treemap...")
        # First, try with just Occupation to see if that works
        # Create treemap with display labels but use original names for hover
        figure4 = px.treemap(
            occupations,
            path=[px.Constant('All Occupations'), 'Display_Label'],
            values='Employment',
            title=f"Top 15 Occupations in {province} by Employment",
            color='NOC',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=600,
            custom_data=['Occupation']  # Include original names for hover
        )
        
        # Simplify the treemap display to show labels
        figure4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=80, b=10),
            title_x=0.5,
            title_y=0.95,
            title_font=dict(size=18)
        )
        
        # Update traces to show display labels but keep original names in hover
        figure4.update_traces(
            textinfo='label',
            textposition='middle center',
            marker=dict(line=dict(width=0.5, color='#7f7f7f')),
            pathbar=dict(visible=True),
            hovertemplate='<b>%{customdata[0]}</b><br>Workers: %{value:,.0f}<br>%{percentParent:.1%} of total<extra></extra>',
            textfont=dict(size=12)
        )
        
        # Add custom NOC labels to the legend
        for i, trace in enumerate(figure4.data):
            if trace.name in noc_labels:
                trace.name = f"NOC {trace.name} - {noc_labels[trace.name]}"
        
        print("Treemap created successfully")
        return figure4
        
    except Exception as e:
        print(f"Error creating treemap: {str(e)}")
        # Fallback to a simple bar chart if treemap fails
        print("Falling back to bar chart...")
        fig = px.bar(
            occupations,
            x='Employment',
            y='Occupation',
            orientation='h',
            title=f"Top 15 Occupations in {province} by Employment",
            labels={'Employment': 'Number of Workers', 'Occupation': ''},
            color='NOC',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=60, b=10),
            title_x=0.5,
            title_font=dict(size=18),
            yaxis=dict(autorange="reversed"),
            legend_title_text='NOC Category'
        )
        return fig

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    app.run_server(host='0.0.0.0', port=8050, debug=False)