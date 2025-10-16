"""
Visualization Module

Create interactive charts and heatmaps for flight price comparisons.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List
from src.api.batch_search import SearchResult


def create_price_heatmap(results: List[SearchResult]) -> go.Figure:
    """
    Create an interactive heatmap showing prices across date combinations.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Plotly Figure object
    """
    # Filter valid results
    valid_results = [r for r in results if r.success and r.cheapest_price is not None]
    
    if not valid_results:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No valid price data to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create DataFrame
    data = []
    for r in valid_results:
        data.append({
            'Departure': r.departure_date.strftime('%b %d'),
            'Return': r.return_date.strftime('%b %d'),
            'Price': r.cheapest_price,
            'Days': r.days_at_destination
        })
    
    df = pd.DataFrame(data)
    
    # Create pivot table for heatmap
    pivot = df.pivot_table(
        values='Price',
        index='Departure',
        columns='Return',
        aggfunc='min'
    )
    
    # Get currency
    currency = valid_results[0].currency
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn_r',  # Red (expensive) to Green (cheap)
        text=pivot.values,
        texttemplate='%{text:.0f}',
        textfont={"size": 11, "color": "black"},
        colorbar=dict(
            title=f"Price ({currency})",
            titleside="right"
        ),
        hovertemplate='Departure: %{y}<br>Return: %{x}<br>Price: ' + currency + ' %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Price Comparison Across Dates",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Return Date",
        yaxis_title="Departure Date",
        height=max(400, len(pivot.index) * 50),  # Scale height with data
        width=max(600, len(pivot.columns) * 80),
        font=dict(size=12)
    )
    
    return fig


def create_price_distribution(results: List[SearchResult]) -> go.Figure:
    """
    Create a histogram showing price distribution.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Plotly Figure object
    """
    valid_results = [r for r in results if r.success and r.cheapest_price is not None]
    
    if not valid_results:
        fig = go.Figure()
        fig.add_annotation(
            text="No price data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    prices = [r.cheapest_price for r in valid_results]
    currency = valid_results[0].currency
    
    fig = go.Figure(data=[go.Histogram(
        x=prices,
        nbinsx=20,
        marker_color='lightblue',
        marker_line_color='darkblue',
        marker_line_width=1
    )])
    
    fig.update_layout(
        title="Price Distribution",
        xaxis_title=f"Price ({currency})",
        yaxis_title="Number of Options",
        showlegend=False,
        height=400
    )
    
    return fig


def create_price_by_duration(results: List[SearchResult]) -> go.Figure:
    """
    Create a scatter plot showing price vs trip duration.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Plotly Figure object
    """
    valid_results = [r for r in results if r.success and r.cheapest_price is not None]
    
    if not valid_results:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    currency = valid_results[0].currency
    
    # Prepare data
    durations = [r.total_duration for r in valid_results]
    prices = [r.cheapest_price for r in valid_results]
    hover_text = [
        f"{r.departure_date.strftime('%b %d')} → {r.return_date.strftime('%b %d')}<br>"
        f"Duration: {r.total_duration} days<br>"
        f"Days at destination: {r.days_at_destination}<br>"
        f"Price: {currency} {r.cheapest_price:.2f}"
        for r in valid_results
    ]
    
    fig = go.Figure(data=go.Scatter(
        x=durations,
        y=prices,
        mode='markers',
        marker=dict(
            size=10,
            color=prices,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title=f"Price ({currency})")
        ),
        text=hover_text,
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Price vs Trip Duration",
        xaxis_title="Total Trip Duration (days)",
        yaxis_title=f"Price ({currency})",
        height=450,
        showlegend=False
    )
    
    return fig


def create_calendar_view(results: List[SearchResult]) -> go.Figure:
    """
    Create a calendar-style view showing best prices per departure date.
    
    Args:
        results: List of SearchResult objects
        
    Returns:
        Plotly Figure object
    """
    valid_results = [r for r in results if r.success and r.cheapest_price is not None]
    
    if not valid_results:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Group by departure date and get min price
    df = pd.DataFrame([
        {
            'date': r.departure_date,
            'price': r.cheapest_price,
            'return': r.return_date,
            'days': r.days_at_destination
        }
        for r in valid_results
    ])
    
    min_prices = df.groupby('date').agg({
        'price': 'min',
        'return': 'first',
        'days': 'first'
    }).reset_index()
    
    currency = valid_results[0].currency
    
    fig = go.Figure(data=go.Bar(
        x=min_prices['date'],
        y=min_prices['price'],
        marker=dict(
            color=min_prices['price'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title=f"Price ({currency})")
        ),
        text=min_prices['price'].apply(lambda x: f"{currency} {x:.0f}"),
        textposition='outside',
        hovertemplate='Date: %{x}<br>Best Price: ' + currency + ' %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Best Price by Departure Date",
        xaxis_title="Departure Date",
        yaxis_title=f"Cheapest Price ({currency})",
        height=400,
        showlegend=False
    )
    
    return fig
