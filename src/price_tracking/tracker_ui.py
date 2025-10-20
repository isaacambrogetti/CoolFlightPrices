"""
Price Tracker UI Tab

Displays tracked flights and their price evolution graphs.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from src.price_tracking.database import PriceTrackingDB


def display_tracker_tab():
    """
Price Tracker UI Tab

Displays tracked flights and their price evolution graphs.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from collections import defaultdict
from src.price_tracking.database import PriceTrackingDB


def group_flights_by_period(flights_data: dict) -> dict:
    """
    Group flights by their departure time period (month-year)
    
    Args:
        flights_data: Dictionary of flight_id -> flight_data
        
    Returns:
        Dictionary of period -> list of (flight_id, flight_data) tuples
    """
    grouped = defaultdict(list)
    
    for flight_id, flight_data in flights_data.items():
        dep_date_str = flight_data.get('departure_date')
        if not dep_date_str:
            grouped['Unknown'].append((flight_id, flight_data))
            continue
        
        try:
            dep_date = datetime.fromisoformat(dep_date_str).date()
            # Group by Month Year (e.g., "March 2026", "August 2026")
            period_key = dep_date.strftime('%B %Y')
            grouped[period_key].append((flight_id, flight_data))
        except:
            grouped['Unknown'].append((flight_id, flight_data))
    
    # Sort periods chronologically
    sorted_periods = {}
    for period, flights in sorted(grouped.items(), key=lambda x: (
        datetime.strptime(x[0], '%B %Y') if x[0] != 'Unknown' else datetime.min
    )):
        sorted_periods[period] = flights
    
    return sorted_periods



def display_tracker_tab():
    """
    Display the price tracking dashboard with all tracked flights
    """
    st.header("📊 Flight Price Tracker")
    st.caption("Monitor your favorite flights and track price changes over time")
    
    # Initialize database
    db = PriceTrackingDB()
    tracked_flights = db.get_tracked_flights()
    
    if not tracked_flights:
        st.info("🔍 No flights tracked yet. Search for flights and click '📊 Track Price' to start monitoring!")
        st.markdown("""
        ### How to use:
        1. Go to **Search Flights** tab
        2. Run a search (single date or flexible dates)
        3. Click the **📊 Track Price** button next to any flight
        4. Return here to see price evolution graphs
        """)
        return
    
    # Add refresh controls at the top
    col_left, col_center, col_right = st.columns([2, 1, 1])
    
    with col_center:
        # Check if any prices need updating
        stale_count = sum(1 for fid in tracked_flights.keys() if db.needs_price_update(fid, hours_threshold=24))
        
        if stale_count > 0:
            st.info(f"🕐 {stale_count} flight(s) need price update (>24h old)")
        else:
            st.success("✅ All prices are fresh (<24h old)")
    
    with col_right:
        manual_refresh = st.button("🔄 Force Refresh All", use_container_width=True, type="secondary",
                                   help="Refresh all flights regardless of when they were last checked")
    
    # Auto-refresh stale prices on page load (once per session)
    if 'auto_refresh_done' not in st.session_state:
        st.session_state.auto_refresh_done = False
    
    # Perform auto-refresh if needed (only for stale prices >24h)
    if not st.session_state.auto_refresh_done and stale_count > 0:
        with st.spinner(f"🔄 Auto-updating {stale_count} stale price(s)..."):
            from src.api.amadeus_client import AmadeusClient
            try:
                client = AmadeusClient()
                results = db.refresh_all_stale_prices(client, hours_threshold=24)
                
                if results['updated'] > 0:
                    st.success(f"✅ Auto-updated {results['updated']} flight price(s)")
                if results['failed'] > 0:
                    st.warning(f"⚠️ Failed to update {results['failed']} flight(s)")
                
                st.session_state.auto_refresh_done = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Auto-refresh error: {str(e)}")
                st.session_state.auto_refresh_done = True
    
    # Manual refresh all prices
    if manual_refresh:
        with st.spinner("🔄 Refreshing all flight prices..."):
            from src.api.amadeus_client import AmadeusClient
            try:
                client = AmadeusClient()
                results = {
                    'total': len(tracked_flights),
                    'updated': 0,
                    'failed': 0,
                    'details': []
                }
                
                for flight_id in tracked_flights.keys():
                    result = db.refresh_flight_price(flight_id, client)
                    if result['success']:
                        results['updated'] += 1
                    else:
                        results['failed'] += 1
                    results['details'].append(result)
                
                st.success(f"✅ Updated {results['updated']}/{results['total']} flights")
                if results['failed'] > 0:
                    st.warning(f"⚠️ {results['failed']} flight(s) failed to update")
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Refresh error: {str(e)}")
    
    # Show statistics
    stats = db.get_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracked", stats['total_tracked'])
    with col2:
        st.metric("Price Drops", stats['with_price_drops'], 
                 delta=None if stats['with_price_drops'] == 0 else "↓",
                 delta_color="normal")
    with col3:
        st.metric("Price Increases", stats['with_price_increases'],
                 delta=None if stats['with_price_increases'] == 0 else "↑",
                 delta_color="inverse")
    with col4:
        avg_change = stats['average_price_change_pct']
        st.metric("Avg Price Change", 
                 f"{avg_change:+.1f}%",
                 delta=f"{abs(avg_change):.1f}%",
                 delta_color="normal" if avg_change <= 0 else "inverse")
    
    st.markdown("---")
    
    # Country Comparison Section
    st.subheader("🌍 Compare Flights by Destination Country")
    st.caption("View price evolution for all flights to the same country")
    
    # Get unique destination countries from tracked flights
    from src.utils.airport_countries import get_country_for_airport
    
    destination_countries = {}
    for flight_id, flight_data in tracked_flights.items():
        country = get_country_for_airport(flight_data['destination'])
        if country != 'Unknown':
            if country not in destination_countries:
                destination_countries[country] = 0
            destination_countries[country] += 1
    
    if destination_countries:
        # Sort by number of flights (descending)
        sorted_countries = sorted(destination_countries.items(), key=lambda x: x[1], reverse=True)
        
        # Create columns for country buttons
        cols_per_row = 4
        rows = [sorted_countries[i:i + cols_per_row] for i in range(0, len(sorted_countries), cols_per_row)]
        
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, (country, count) in enumerate(row):
                with cols[idx]:
                    if st.button(
                        f"🌍 {country} ({count})",
                        key=f"country_{country}",
                        use_container_width=True
                    ):
                        st.session_state.selected_country = country
        
        # Display selected country comparison
        if 'selected_country' in st.session_state and st.session_state.selected_country:
            selected_country = st.session_state.selected_country
            
            st.markdown("---")
            st.subheader(f"📊 {selected_country} - Price Comparison")
            
            # Add view mode toggle
            col_label, col_toggle = st.columns([3, 1])
            with col_label:
                st.caption("Choose how to view your tracked flights:")
            with col_toggle:
                view_mode = st.radio(
                    "View Mode",
                    ["All Together", "Group by Period"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"view_mode_{selected_country}"
                )
            
            # Filter flights for selected country
            country_flights = {
                fid: fdata for fid, fdata in tracked_flights.items()
                if get_country_for_airport(fdata['destination']) == selected_country
            }
            
            if view_mode == "All Together":
                # Show all flights in one graph (original behavior)
                fig = create_country_comparison_graph(country_flights, selected_country)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Group by travel period
                grouped_flights = group_flights_by_period(country_flights)
                
                if len(grouped_flights) == 1:
                    # Only one period, show single graph
                    period = list(grouped_flights.keys())[0]
                    st.info(f"All flights are in the same period: **{period}**")
                    flights_dict = {fid: fdata for fid, fdata in grouped_flights[period]}
                    fig = create_country_comparison_graph(flights_dict, selected_country)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Multiple periods, show separate graphs
                    st.info(f"📅 Showing {len(grouped_flights)} different travel periods")
                    
                    for period, flights_list in grouped_flights.items():
                        st.markdown(f"### 📆 {period}")
                        st.caption(f"{len(flights_list)} flight(s) in this period")
                        
                        # Convert list back to dict for graph function
                        flights_dict = {fid: fdata for fid, fdata in flights_list}
                        fig = create_country_comparison_graph(flights_dict, selected_country)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
            
            # Show list of flights included
            with st.expander(f"✈️ Flights included ({destination_countries.get(selected_country, 0)})"):
                for flight_id, flight_data in tracked_flights.items():
                    if get_country_for_airport(flight_data['destination']) == selected_country:
                        route = f"{flight_data['origin']} → {flight_data['destination']}"
                        dep = flight_data['departure_date']
                        ret = flight_data.get('return_date', 'One-way')
                        price = flight_data['latest_price']
                        currency = flight_data['currency']
                        st.markdown(f"- **{route}** | Dep: {dep} | Latest: {currency} {price:.2f}")
    else:
        st.info("Track flights to different countries to enable country-based comparison!")
    
    st.markdown("---")
    st.markdown("---")
    
    # Display each tracked flight
    for flight_id, flight_data in tracked_flights.items():
        price_change = flight_data['latest_price'] - flight_data['initial_price']
        price_change_pct = (price_change / flight_data['initial_price']) * 100 if flight_data['initial_price'] > 0 else 0
        
        # Color code based on price change
        if price_change < 0:
            price_badge = f"🟢 **{flight_data['currency']} {flight_data['latest_price']:.2f}** (↓ {abs(price_change_pct):.1f}%)"
        elif price_change > 0:
            price_badge = f"🔴 **{flight_data['currency']} {flight_data['latest_price']:.2f}** (↑ {price_change_pct:.1f}%)"
        else:
            price_badge = f"⚪ **{flight_data['currency']} {flight_data['latest_price']:.2f}** (no change)"
        
        # Route title with return flight info
        route_title = f"✈️ {flight_data['origin']} → {flight_data['destination']} ({flight_data['departure_date']})"
        if flight_data['is_roundtrip']:
            route_title += f"\n{flight_data['destination']} → {flight_data['origin']} ({flight_data['return_date']})"
        
        with st.expander(
            f"{route_title} | {price_badge}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Price evolution graph
                fig = create_price_evolution_graph(flight_data)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Flight details
                st.markdown("**Flight Details:**")
                st.markdown(f"- **Route:** {flight_data['origin']} → {flight_data['destination']}")
                st.markdown(f"- **Departure:** {flight_data['departure_date']}")
                
                if flight_data['is_roundtrip']:
                    st.markdown(f"- **Return:** {flight_data['return_date']}")
                else:
                    st.markdown("- **Type:** One-way")
                
                st.markdown(f"- **Airline:** {flight_data['airline']} {flight_data['flight_number']}")
                
                if flight_data.get('return_airline'):
                    st.markdown(f"- **Return Airline:** {flight_data['return_airline']} {flight_data['return_flight_number']}")
                
                st.markdown("---")
                st.markdown("**Price History:**")
                st.markdown(f"- **Initial:** {flight_data['currency']} {flight_data['initial_price']:.2f}")
                st.markdown(f"- **Current:** {flight_data['currency']} {flight_data['latest_price']:.2f}")
                st.markdown(f"- **Change:** {flight_data['currency']} {price_change:+.2f} ({price_change_pct:+.1f}%)")
                
                # Show last checked time
                if flight_data.get('last_checked'):
                    try:
                        last_checked_dt = datetime.fromisoformat(flight_data['last_checked'])
                        hours_ago = (datetime.now() - last_checked_dt).total_seconds() / 3600
                        
                        if hours_ago < 1:
                            time_str = f"{int(hours_ago * 60)} minutes ago"
                        elif hours_ago < 24:
                            time_str = f"{int(hours_ago)} hours ago"
                        else:
                            days_ago = int(hours_ago / 24)
                            time_str = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
                        
                        st.markdown(f"- **Last checked:** {time_str}")
                    except:
                        pass
                
                price_history = flight_data['price_history']
                if len(price_history) > 1:
                    prices = [p['price'] for p in price_history]
                    st.markdown(f"- **Lowest:** {flight_data['currency']} {min(prices):.2f}")
                    st.markdown(f"- **Highest:** {flight_data['currency']} {max(prices):.2f}")
                
                st.markdown(f"- **Tracked since:** {datetime.fromisoformat(flight_data['added_date']).strftime('%b %d, %Y')}")
                st.markdown(f"- **Data points:** {len(price_history)}")
                
                st.markdown("---")
                
                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("🗑️ Remove", key=f"remove_{flight_id}", use_container_width=True):
                        db.remove_tracked_flight(flight_id)
                        st.success("Removed from tracking")
                        st.rerun()
                
                with col_btn2:
                    if st.button("📥 Export", key=f"export_{flight_id}", use_container_width=True):
                        export_price_history(flight_data, flight_id)
    
    # Clear all button at the bottom
    st.markdown("---")
    if st.button("🗑️ Clear All Tracked Flights", type="secondary"):
        if st.session_state.get('confirm_clear', False):
            db.clear_all()
            st.success("All tracked flights removed!")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("⚠️ Click again to confirm clearing all tracked flights")


def create_price_evolution_graph(flight_data: dict) -> go.Figure:
    """
    Create an interactive line graph showing price evolution over time
    
    Args:
        flight_data: Flight data dictionary with price_history
        
    Returns:
        Plotly Figure object
    """
    price_history = flight_data['price_history']
    
    if not price_history:
        fig = go.Figure()
        fig.add_annotation(
            text="No price history available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Extract timestamps and prices
    timestamps = [datetime.fromisoformat(p['timestamp']) for p in price_history]
    prices = [p['price'] for p in price_history]
    currency = flight_data['currency']
    
    fig = go.Figure()
    
    # Main price line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=prices,
        mode='lines+markers',
        name='Price',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>%{x|%b %d, %Y %H:%M}</b><br>' +
                      f'Price: {currency} %{{y:.2f}}<br>' +
                      '<extra></extra>'
    ))
    
    # Add reference line for initial price
    fig.add_hline(
        y=flight_data['initial_price'],
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Initial: {currency} {flight_data['initial_price']:.2f}",
        annotation_position="right"
    )
    
    # Highlight lowest and highest prices if multiple data points
    if len(prices) > 1:
        min_price = min(prices)
        max_price = max(prices)
        min_idx = prices.index(min_price)
        max_idx = prices.index(max_price)
        
        # Lowest price marker
        fig.add_trace(go.Scatter(
            x=[timestamps[min_idx]],
            y=[min_price],
            mode='markers',
            name='Lowest',
            marker=dict(size=15, color='green', symbol='star', line=dict(width=2, color='darkgreen')),
            hovertemplate=f'<b>Lowest Price</b><br>%{{x|%b %d, %Y}}<br>Price: {currency} %{{y:.2f}}<br><extra></extra>'
        ))
        
        # Highest price marker
        fig.add_trace(go.Scatter(
            x=[timestamps[max_idx]],
            y=[max_price],
            mode='markers',
            name='Highest',
            marker=dict(size=15, color='red', symbol='star', line=dict(width=2, color='darkred')),
            hovertemplate=f'<b>Highest Price</b><br>%{{x|%b %d, %Y}}<br>Price: {currency} %{{y:.2f}}<br><extra></extra>'
        ))
    
    # Layout
    title_text = f"Price Evolution:<br>{flight_data['origin']} → {flight_data['destination']} ({flight_data['departure_date']})"
    if flight_data.get('return_date'):
        title_text += f"<br>{flight_data['destination']} → {flight_data['origin']} ({flight_data['return_date']})"
    
    fig.update_layout(
        title=title_text,
        xaxis_title="Date",
        yaxis_title=f"Price ({currency})",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_country_comparison_graph(flights_data: dict, country: str) -> go.Figure:
    """
    Create a comparison graph for all flights to a specific country
    
    Args:
        flights_data: Dictionary of flight_id -> flight_data
        country: Destination country to filter and display
        
    Returns:
        Plotly figure object
    """
    from src.utils.airport_countries import get_country_for_airport
    
    fig = go.Figure()
    
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    flight_count = 0
    
    for flight_id, flight_data in flights_data.items():
        # Check if this flight goes to the specified country
        dest_country = get_country_for_airport(flight_data['destination'])
        
        if dest_country != country:
            continue
        
        # Extract price history
        history = flight_data['price_history']
        if not history:
            continue
        
        timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in history]
        prices = [entry['price'] for entry in history]
        currency = flight_data['currency']
        
        # Create flight label with return info for roundtrips
        route = f"{flight_data['origin']} → {flight_data['destination']}"
        dep_date = flight_data['departure_date']
        ret_date = flight_data.get('return_date')
        
        if ret_date:
            # Roundtrip - include return flight info
            return_route = f"{flight_data['destination']} → {flight_data['origin']}"
            flight_label = f"{route} ({dep_date})<br>{return_route} ({ret_date})"
            # For legend (single line)
            flight_label_short = f"{route} ({dep_date})"
        else:
            # One-way
            flight_label = f"{route} ({dep_date})"
            flight_label_short = flight_label
        
        color = colors[flight_count % len(colors)]
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=prices,
            mode='lines+markers',
            name=flight_label_short,
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color),
            hovertemplate=f'<b>{flight_label}</b><br>%{{x|%b %d, %H:%M}}<br>Price: {currency} %{{y:.2f}}<br><extra></extra>'
        ))
        
        flight_count += 1
    
    # Layout
    fig.update_layout(
        title=f"Price Comparison - Flights to {country}",
        xaxis_title="Date & Time",
        yaxis_title=f"Price ({currency if flight_count > 0 else 'EUR'})",
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    if flight_count == 0:
        # No flights for this country
        fig.add_annotation(
            text=f"No tracked flights to {country}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
    
    return fig


def export_price_history(flight_data: dict, flight_id: str):
    """
    Export price history as CSV download
    
    Args:
        flight_data: Flight data dictionary
        flight_id: Flight identifier
    """
    import pandas as pd
    from io import StringIO
    
    # Prepare data for export
    history = flight_data['price_history']
    
    export_data = []
    for entry in history:
        export_data.append({
            'Timestamp': entry['timestamp'],
            'Date': datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d'),
            'Time': datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S'),
            'Price': entry['price'],
            'Currency': flight_data['currency']
        })
    
    df = pd.DataFrame(export_data)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Filename
    filename = f"price_history_{flight_data['origin']}_{flight_data['destination']}_{flight_data['departure_date']}.csv"
    
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=f"download_{flight_id}"
    )
