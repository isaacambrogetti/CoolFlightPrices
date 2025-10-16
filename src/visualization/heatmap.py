"""
Visualization Module

Create interactive charts and heatmaps for flight price comparisons.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List
from src.api.batch_search import SearchResult

def create_airport_price_comparison(results: List[SearchResult]) -> List[go.Figure]:
    """
    Create bar charts comparing average prices per departure and arrival airport.
    Only shown when there are multiple airports for departure or arrival.
    Returns a list of Plotly Figure objects (one for departure, one for arrival).
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
        return [fig]

    # Collect airport info
    dep_prices = {}
    arr_prices = {}
    for r in valid_results:
        origin = getattr(r, 'origin', None)
        destination = getattr(r, 'destination', None)
        price = float(r.cheapest_price)
        if origin:
            dep_prices.setdefault(origin, []).append(price)
        if destination:
            arr_prices.setdefault(destination, []).append(price)

    # Only show if there are multiple airports
    figs = []
    currency = valid_results[0].currency
    if len(dep_prices) > 1:
        dep_df = pd.DataFrame({
            'Airport': list(dep_prices.keys()),
            'Avg Price': [sum(prices)/len(prices) for prices in dep_prices.values()],
            'Min Price': [min(prices) for prices in dep_prices.values()],
            'Median Price': [pd.Series(prices).median() for prices in dep_prices.values()]
        })
        fig_dep = go.Figure()
        fig_dep.add_trace(go.Bar(
            x=dep_df['Airport'],
            y=dep_df['Avg Price'],
            marker=dict(color=dep_df['Avg Price'], colorscale='RdYlGn_r', showscale=True, colorbar=dict(title=f"Avg Price ({currency})")),
            text=dep_df['Avg Price'].apply(lambda x: f"{currency} {x:.0f}"),
            textposition='outside',
            name='Average Price',
            hovertemplate='Airport: %{x}<br>Avg Price: ' + currency + ' %{y:.2f}<br>Min: %{customdata[0]:.2f}<br>Median: %{customdata[1]:.2f}<extra></extra>',
            customdata=dep_df[['Min Price', 'Median Price']].values
        ))
        fig_dep.update_layout(
            title="Average Price by Departure Airport",
            xaxis_title="Departure Airport",
            yaxis_title=f"Avg Price ({currency})",
            height=400,
            showlegend=False
        )
        figs.append(fig_dep)

    if len(arr_prices) > 1:
        arr_df = pd.DataFrame({
            'Airport': list(arr_prices.keys()),
            'Avg Price': [sum(prices)/len(prices) for prices in arr_prices.values()],
            'Min Price': [min(prices) for prices in arr_prices.values()],
            'Median Price': [pd.Series(prices).median() for prices in arr_prices.values()]
        })
        fig_arr = go.Figure()
        fig_arr.add_trace(go.Bar(
            x=arr_df['Airport'],
            y=arr_df['Avg Price'],
            marker=dict(color=arr_df['Avg Price'], colorscale='RdYlGn_r', showscale=True, colorbar=dict(title=f"Avg Price ({currency})")),
            text=arr_df['Avg Price'].apply(lambda x: f"{currency} {x:.0f}"),
            textposition='outside',
            name='Average Price',
            hovertemplate='Airport: %{x}<br>Avg Price: ' + currency + ' %{y:.2f}<br>Min: %{customdata[0]:.2f}<br>Median: %{customdata[1]:.2f}<extra></extra>',
            customdata=arr_df[['Min Price', 'Median Price']].values
        ))
        fig_arr.update_layout(
            title="Average Price by Arrival Airport",
            xaxis_title="Arrival Airport",
            yaxis_title=f"Avg Price ({currency})",
            height=400,
            showlegend=False
        )
        figs.append(fig_arr)

    if not figs:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough airport variety for comparison",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18)
        )
        return [fig]
    return figs
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
        try:
            data.append({
                'Departure': r.departure_date,  # Keep as date object
                'Return': r.return_date,  # Keep as date object
                'Departure_Label': r.departure_date.strftime('%b %d'),
                'Return_Label': r.return_date.strftime('%b %d'),
                'Price': float(r.cheapest_price),
                'Days': r.days_at_destination
            })
        except Exception as e:
            # Skip results with invalid data
            print(f"Skipping result due to error: {e}")
            continue
    
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No valid data for heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    df = pd.DataFrame(data)
    
    # Sort by actual dates
    df = df.sort_values(['Departure', 'Return'])
    
    # Create pivot table for heatmap using date objects
    try:
        pivot = df.pivot_table(
            values='Price',
            index='Departure_Label',  # Use labels for display
            columns='Return_Label',
            aggfunc='min'
        )
        
        # Get the order based on actual dates
        dep_order = df.sort_values('Departure')['Departure_Label'].unique()
        ret_order = df.sort_values('Return')['Return_Label'].unique()
        
        # Reindex to ensure chronological order
        pivot = pivot.reindex(index=dep_order, columns=ret_order)
        
        # Check if we have enough data
        if pivot.size == 0 or pivot.isna().all().all():
            fig = go.Figure()
            fig.add_annotation(
                text="No valid date combinations to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
    except Exception as e:
        # Handle edge cases (e.g., single data point)
        fig = go.Figure()
        fig.add_annotation(
            text=f"Not enough data to create heatmap<br>({len(df)} result(s) found)<br>{str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Get currency
    currency = valid_results[0].currency
    
    # Handle NaN values in the heatmap (for sparse data)
    # Replace NaN with a sentinel value for better visualization
    z_values = pivot.values.copy()
    
    # Create custom text that shows prices or '-' for missing data
    text_values = []
    for row in pivot.values:
        text_row = []
        for val in row:
            if pd.isna(val):
                text_row.append('-')
            else:
                text_row.append(f'{val:.0f}')
        text_values.append(text_row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale='RdYlGn_r',  # Red (expensive) to Green (cheap)
        text=text_values,
        texttemplate='%{text}',
        textfont={"size": 10, "color": "black"},
        colorbar=dict(
            title=dict(
                text=f"Price ({currency})",
                side="right"
            )
        ),
        hovertemplate='Departure: %{y}<br>Return: %{x}<br>Price: ' + currency + ' %{z:.2f}<extra></extra>',
        zmin=pivot.min().min(),  # Set color scale based on actual data
        zmax=pivot.max().max()
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
    
    try:
        prices = [float(r.cheapest_price) for r in valid_results]
        currency = valid_results[0].currency
    except (ValueError, TypeError, AttributeError) as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error processing price data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
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
    
    try:
        currency = valid_results[0].currency
        
        # Prepare data with validation
        durations = []
        prices = []
        hover_text = []
        
        for r in valid_results:
            try:
                durations.append(int(r.total_duration))
                prices.append(float(r.cheapest_price))
                hover_text.append(
                    f"{r.departure_date.strftime('%b %d')} → {r.return_date.strftime('%b %d')}<br>"
                    f"Duration: {r.total_duration} days<br>"
                    f"Days at destination: {r.days_at_destination}<br>"
                    f"Price: {currency} {r.cheapest_price:.2f}"
                )
            except (ValueError, TypeError, AttributeError):
                # Skip invalid entries
                continue
        
        if not durations or not prices:
            fig = go.Figure()
            fig.add_annotation(
                text="No valid data points",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig
            
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error processing data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
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
    
    try:
        # Group by departure date and get min price
        df = pd.DataFrame([
            {
                'date': r.departure_date,
                'price': float(r.cheapest_price),
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
        
    except Exception as e:
        # Handle grouping errors or data issues
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating calendar view: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
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
