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
            st.info(f"🕐 {stale_count} flight(s) need price update")
    
    with col_right:
        manual_refresh = st.button("🔄 Refresh All Prices", use_container_width=True, type="primary")
    
    # Auto-refresh stale prices on page load (once per session)
    if 'auto_refresh_done' not in st.session_state:
        st.session_state.auto_refresh_done = False
    
    # Perform auto-refresh if needed
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
        
        # Route title
        route_title = f"✈️ {flight_data['origin']} → {flight_data['destination']}"
        date_info = f"{flight_data['departure_date']}"
        if flight_data['is_roundtrip']:
            date_info += f" → {flight_data['return_date']}"
        
        with st.expander(
            f"{route_title} | {date_info} | {price_badge}",
            expanded=True
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
    fig.update_layout(
        title=f"Price Evolution: {flight_data['origin']} → {flight_data['destination']}",
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
