import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any

def create_utilization_chart(results: Dict[str, Any], truck_spec: Dict[str, float], trucks_needed: int) -> go.Figure:
    """
    Create a utilization chart showing volume and weight usage
    
    Args:
        results: Calculation results
        truck_spec: Truck specifications
        trucks_needed: Number of trucks needed
        
    Returns:
        Plotly figure object
    """
    # Calculate capacities
    total_volume_capacity = truck_spec['volume'] * trucks_needed
    total_weight_capacity = truck_spec['weight'] * trucks_needed
    
    # Data for the chart
    categories = ['Volume (m³)', 'Weight (kg)']
    used_values = [results['total_volume'], results['total_weight']]
    capacity_values = [total_volume_capacity, total_weight_capacity]
    utilization_percentages = [
        results['volume_utilization'],
        results['weight_utilization']
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Add capacity bars (background)
    fig.add_trace(go.Bar(
        name='Total Capacity',
        x=categories,
        y=capacity_values,
        marker_color='lightgray',
        opacity=0.7
    ))
    
    # Add used capacity bars
    colors = ['#2E86AB' if util >= 70 else '#F24236' for util in utilization_percentages]
    fig.add_trace(go.Bar(
        name='Used Capacity',
        x=categories,
        y=used_values,
        marker_color=colors,
        opacity=0.8
    ))
    
    # Update layout
    fig.update_layout(
        title='Truck Capacity Utilization',
        barmode='overlay',
        yaxis_title='Capacity',
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    # Add utilization percentage annotations
    for i, (category, percentage) in enumerate(zip(categories, utilization_percentages)):
        fig.add_annotation(
            x=category,
            y=used_values[i],
            text=f'{percentage:.1f}%',
            showarrow=False,
            yshift=10,
            font=dict(color='white', size=12, family='Arial Black')
        )
    
    return fig

def create_sku_breakdown_chart(skus: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a pie chart showing SKU breakdown by volume or weight
    
    Args:
        skus: List of SKU dictionaries
        
    Returns:
        Plotly figure object
    """
    if not skus:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No SKUs to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Extract data
    sku_names = [sku['name'] for sku in skus]
    volumes = [sku['total_volume'] for sku in skus]
    weights = [sku['total_weight'] for sku in skus]
    
    # Create subplot with two pie charts
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=('Volume Distribution', 'Weight Distribution')
    )
    
    # Volume pie chart
    fig.add_trace(go.Pie(
        labels=sku_names,
        values=volumes,
        name="Volume",
        hole=.3,
        marker_colors=px.colors.qualitative.Set3
    ), row=1, col=1)
    
    # Weight pie chart
    fig.add_trace(go.Pie(
        labels=sku_names,
        values=weights,
        name="Weight",
        hole=.3,
        marker_colors=px.colors.qualitative.Pastel
    ), row=1, col=2)
    
    # Update layout
    fig.update_layout(
        title_text="SKU Distribution Analysis",
        showlegend=True,
        height=400,
        font=dict(size=11)
    )
    
    return fig

def create_truck_comparison_chart(optimization_results: Dict[str, Dict[str, Any]]) -> go.Figure:
    """
    Create a comparison chart for different truck types
    
    Args:
        optimization_results: Results from truck type optimization
        
    Returns:
        Plotly figure object
    """
    truck_types = list(optimization_results.keys())
    trucks_needed = [optimization_results[truck]['trucks_needed'] for truck in truck_types]
    utilizations = [optimization_results[truck]['utilization'] for truck in truck_types]
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add bars for trucks needed
    fig.add_trace(go.Bar(
        name='Trucks Needed',
        x=truck_types,
        y=trucks_needed,
        yaxis='y',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    # Add line for utilization
    fig.add_trace(go.Scatter(
        name='Utilization %',
        x=truck_types,
        y=utilizations,
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))
    
    # Update layout
    fig.update_layout(
        title='Truck Type Comparison',
        xaxis_title='Truck Type',
        yaxis=dict(
            title='Number of Trucks',
            side='left'
        ),
        yaxis2=dict(
            title='Utilization %',
            side='right',
            overlaying='y'
        ),
        showlegend=True,
        height=400
    )
    
    return fig

def create_efficiency_gauge(utilization_percentage: float) -> go.Figure:
    """
    Create a gauge chart showing efficiency
    
    Args:
        utilization_percentage: Current utilization percentage
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = utilization_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Utilization Efficiency"},
        delta = {'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig
