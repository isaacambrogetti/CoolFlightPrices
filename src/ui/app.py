def get_airline_logo_html(iata_code: str) -> str:
    """Return HTML for airline logo with fallback to code if missing."""
    if not iata_code or len(iata_code) != 2:
        return f"<span>{iata_code}</span>"
    url = f"https://content.airhex.com/content/logos/airlines_{iata_code.upper()}_100_100_s.png"
    # Use onerror to fallback to code if image fails to load
    # Remove background and border for a cleaner look
    # Simple logo rendering, no background or border modifications
    return f'<img src="{url}" alt="logo" width="20" style="vertical-align:middle; margin-right:4px;" onerror="this.style.display=\'none\';this.insertAdjacentHTML(\'afterend\',\'<span>{iata_code}</span>\');"/> '
"""
CoolFlightPrices - Streamlit UI (Updated with Date Range Search)

A web interface for searching and comparing flight prices across date ranges.
"""

import streamlit as st
from datetime import date, timedelta
from pathlib import Path
import sys
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.api.amadeus_client import AmadeusClient
from src.api.date_range_search import generate_date_combinations, estimate_api_calls, smart_sample_dates
from src.api.batch_search import BatchFlightSearch
from src.visualization.heatmap import (
    create_price_heatmap, 
    create_price_distribution, 
    create_price_by_duration,
    create_calendar_view,
    create_airport_price_comparison
)
from src.utils.airport_search import search_airports, parse_airport_input, get_airport_display_name, get_all_airport_options
from src.price_tracking.database import PriceTrackingDB
from src.price_tracking.tracker_ui import display_tracker_tab
from config.settings import Config


# Page configuration
st.set_page_config(
    page_title="CoolFlightPrices",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def display_track_button(flight: dict, index) -> bool:
    """
    Display a track price button for a flight (toggle on/off)
    
    Args:
        flight: Flight dictionary
        index: Unique index/identifier for the button (can be int or str)
        
    Returns:
        True if button was clicked, False otherwise
    """
    db = PriceTrackingDB()
    flight_id = db.generate_flight_id(flight)
    is_tracked = db.is_tracked(flight)
    
    if is_tracked:
        # Show "Untrack" button - clickable to remove from tracking
        if st.button("✅ Tracking (click to untrack)", key=f"track_{index}", use_container_width=True, type="secondary"):
            try:
                db.remove_tracked_flight(flight_id)
                st.success("🗑️ Flight removed from tracker!")
                # Remove from session state
                if 'tracked_flights' in st.session_state and flight_id in st.session_state.tracked_flights:
                    st.session_state.tracked_flights.remove(flight_id)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error removing flight from tracker: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")
            return True
        return False
    else:
        # Show "Track Price" button - clickable to add to tracking
        if st.button("📊 Track Price", key=f"track_{index}", use_container_width=True, type="primary"):
            try:
                db.add_tracked_flight(flight, flight['price'], flight['currency'])
                st.success("✅ Flight added to tracker! You can continue tracking more flights or check the 📊 Price Tracker page.")
                # Mark as tracked in session state to update button
                if 'tracked_flights' not in st.session_state:
                    st.session_state.tracked_flights = set()
                st.session_state.tracked_flights.add(flight_id)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error adding flight to tracker: {str(e)}")
                import traceback
                st.error(f"Details: {traceback.format_exc()}")
            return True
        return False


def check_api_credentials():
    """Check if API credentials are configured"""
    if not Config.AMADEUS_API_KEY or not Config.AMADEUS_API_SECRET:
        st.error("⚠️ Amadeus API credentials not configured!")
        st.info("""
        **Setup Instructions:**
        1. Go to https://developers.amadeus.com/
        2. Sign up and create a new app
        3. Copy your API Key and Secret
        4. Create a `.env` file in the project root
        5. Add your credentials:
           ```
           AMADEUS_API_KEY=your_key_here
           AMADEUS_API_SECRET=your_secret_here
           ```
        6. Restart the app
        """)
        return False
    return True


def single_date_search_ui(sidebar):
    """UI for single date search (original functionality)"""
    with sidebar:
        # Dates
        today = date.today()
        default_departure = today + timedelta(days=30)
        default_return = default_departure + timedelta(days=4)
        
        departure_date = st.date_input(
            "Departure Date",
            value=default_departure,
            min_value=today,
            help="When do you want to leave?"
        )
        
        trip_type = st.radio(
            "Trip Type",
            ["Roundtrip", "One-way"],
            horizontal=True
        )
        
        if trip_type == "Roundtrip":
            return_date = st.date_input(
                "Return Date",
                value=default_return,
                min_value=departure_date,
                help="When do you want to return?"
            )
        else:
            return_date = None
        
        # Passengers
        adults = st.number_input(
            "Adults",
            min_value=1,
            max_value=9,
            value=1
        )
        
        # Number of results
        max_results = st.slider(
            "Max Results",
            min_value=5,
            max_value=20,
            value=10,
            help="Maximum number of flight offers to display"
        )
        
        # Flight time preferences
        st.markdown("### ⏰ Flight Time Preferences")
        st.caption("Filter flights by departure/arrival times")
        
        with st.expander("Departure Time Filters", expanded=False):
            filter_dep = st.checkbox("Filter departure times", key="filter_dep_single", value=False)
            if filter_dep:
                dep_time_range = st.slider(
                    "Acceptable departure hours (24h format)",
                    min_value=0,
                    max_value=23,
                    value=(6, 22),
                    help="Only search for flights departing between these hours",
                    key="dep_range_single"
                )
                dep_min_hour, dep_max_hour = dep_time_range
            else:
                dep_min_hour, dep_max_hour = None, None
        
        with st.expander("Arrival Time Filters", expanded=False):
            filter_arr = st.checkbox("Filter arrival times", key="filter_arr_single", value=False)
            if filter_arr:
                arr_time_range = st.slider(
                    "Acceptable arrival hours (24h format)",
                    min_value=0,
                    max_value=23,
                    value=(6, 23),
                    help="Only search for flights arriving between these hours",
                    key="arr_range_single"
                )
                arr_min_hour, arr_max_hour = arr_time_range
            else:
                arr_min_hour, arr_max_hour = None, None
    
    return departure_date, return_date, adults, max_results, dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour


def date_range_search_ui(sidebar):
    """UI for flexible date range search (new functionality)"""
    with sidebar:
        st.markdown("### 📅 Departure Date Range")
        col1, col2 = st.columns(2)
        
        today = date.today()
        default_dep_start = today + timedelta(days=30)
        default_dep_end = default_dep_start + timedelta(days=4)
        
        with col1:
            dep_start = st.date_input(
                "Earliest",
                value=default_dep_start,
                min_value=today,
                help="Earliest you can depart",
                key="dep_start"
            )
        with col2:
            # Ensure dep_end default is valid
            safe_dep_end = max(default_dep_end, dep_start)
            dep_end = st.date_input(
                "Latest",
                value=safe_dep_end,
                min_value=dep_start,
                help="Latest you can depart",
                key="dep_end"
            )
        
        st.markdown("### 🔙 Return Date Range")
        col1, col2 = st.columns(2)
        
        # Calculate safe defaults for return dates
        min_ret_date = dep_start + timedelta(days=1)
        default_ret_start = max(dep_end + timedelta(days=3), min_ret_date)
        default_ret_end = default_ret_start + timedelta(days=4)
        
        with col1:
            # Ensure ret_start default is valid
            safe_ret_start = max(default_ret_start, min_ret_date)
            ret_start = st.date_input(
                "Earliest",
                value=safe_ret_start,
                min_value=min_ret_date,
                help="Earliest you can return",
                key="ret_start"
            )
        with col2:
            # Ensure ret_end default is valid
            safe_ret_end = max(default_ret_end, ret_start)
            ret_end = st.date_input(
                "Latest",
                value=safe_ret_end,
                min_value=ret_start,
                help="Latest you can return",
                key="ret_end"
            )
        
        # Trip duration preferences
        st.markdown("### ⏱️ Trip Duration")
        duration_mode = st.radio(
            "Vacation Length Strategy",
            options=["Flexible (any duration)", "Fixed duration", "Maximum days possible"],
            help="""
            - **Flexible**: Any trip length between selected dates
            - **Fixed**: Exact number of days (e.g., exactly 7 days)
            - **Maximum**: Prioritize longest possible stays
            """
        )
        
        if duration_mode == "Fixed duration":
            fixed_days = st.number_input(
                "Trip duration (days)",
                min_value=2,
                max_value=30,
                value=7,
                help="Total trip duration including departure and return days"
            )
            min_days = fixed_days - 1  # Convert to days at destination
            max_days = fixed_days - 1
        elif duration_mode == "Maximum days possible":
            min_days = st.slider(
                "Minimum trip length (days at destination)",
                min_value=1,
                max_value=14,
                value=5,
                help="Search for longest possible stays above this minimum"
            )
            max_days = None  # Will prioritize longest
        else:  # Flexible
            min_days = st.slider(
                "Minimum full days at destination",
                min_value=0,
                max_value=14,
                value=2,
                help="Minimum complete days you want to spend at destination"
            )
            max_days = None
        
        # Passengers
        adults = st.number_input(
            "Adults",
            min_value=1,
            max_value=9,
            value=1,
            key="adults_range"
        )
        
        # Flight time preferences
        st.markdown("### ⏰ Flight Time Preferences")
        st.caption("Filter flights by departure/arrival times")
        
        with st.expander("Departure Time Filters", expanded=False):
            filter_dep = st.checkbox("Filter departure times", key="filter_dep_range", value=False)
            if filter_dep:
                dep_time_range = st.slider(
                    "Acceptable departure hours (24h format)",
                    min_value=0,
                    max_value=23,
                    value=(6, 22),
                    help="Only search for flights departing between these hours",
                    key="dep_range_flex"
                )
                dep_min_hour, dep_max_hour = dep_time_range
            else:
                dep_min_hour, dep_max_hour = None, None
        
        with st.expander("Arrival Time Filters", expanded=False):
            filter_arr = st.checkbox("Filter arrival times", key="filter_arr_range", value=False)
            if filter_arr:
                arr_time_range = st.slider(
                    "Acceptable arrival hours (24h format)",
                    min_value=0,
                    max_value=23,
                    value=(6, 23),
                    help="Only search for flights arriving between these hours",
                    key="arr_range_flex"
                )
                arr_min_hour, arr_max_hour = arr_time_range
            else:
                arr_min_hour, arr_max_hour = None, None
        
        # Calculate combinations
        try:
            stats = estimate_api_calls(dep_start, dep_end, ret_start, ret_end, min_days, max_days)
            num_combinations = stats['total_combinations']
            
            st.info(f"""
            **📊 Search Preview:**
            - Departure options: {stats['departure_days']} days
            - Return options: {stats['return_days']} days
            - Valid combinations: **{num_combinations}**
            - API calls needed: {num_combinations}
            """)
            
            if num_combinations > 50:
                st.warning(f"⚠️ {num_combinations} API calls! Consider narrowing date ranges.")
                use_sampling = st.checkbox(
                    f"Smart sampling (reduce to ~20-30 searches)",
                    value=True,
                    help="Sample dates evenly to reduce API calls while maintaining good coverage"
                )
            else:
                use_sampling = False
            
            if num_combinations > 100:
                st.error("🛑 Too many combinations! Please reduce your date ranges.")
                return None
                
        except Exception as e:
            st.error(f"Error calculating combinations: {e}")
            return None
    
    return {
        'dep_start': dep_start,
        'dep_end': dep_end,
        'ret_start': ret_start,
        'ret_end': ret_end,
        'min_days': min_days,
        'max_days': max_days if duration_mode == "Fixed duration" else None,
        'duration_mode': duration_mode,
        'adults': adults,
        'use_sampling': use_sampling if num_combinations > 50 else False,
        'dep_min_hour': dep_min_hour,
        'dep_max_hour': dep_max_hour,
        'arr_min_hour': arr_min_hour,
        'arr_max_hour': arr_max_hour
    }


def filter_flights_by_time(flights, dep_min_hour=None, dep_max_hour=None, arr_min_hour=None, arr_max_hour=None):
    """
    Filter flights by departure and arrival times.
    
    Args:
        flights: List of flight dictionaries
        dep_min_hour: Minimum departure hour (0-23), None for no limit
        dep_max_hour: Maximum departure hour (0-23), None for no limit  
        arr_min_hour: Minimum arrival hour (0-23), None for no limit
        arr_max_hour: Maximum arrival hour (0-23), None for no limit
    
    Returns:
        Filtered list of flights
    """
    if not any([dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour]):
        return flights
    
    filtered = []
    for flight in flights:
        # Check outbound departure time
        if dep_min_hour is not None or dep_max_hour is not None:
            dep_time = flight['outbound']['departure_time']
            # Handle both datetime.time objects and strings
            if isinstance(dep_time, str):
                dep_hour = int(dep_time.split(':')[0])
            else:
                dep_hour = dep_time.hour
            
            if dep_min_hour is not None and dep_hour < dep_min_hour:
                continue
            if dep_max_hour is not None and dep_hour > dep_max_hour:
                continue
        
        # Check outbound arrival time
        if arr_min_hour is not None or arr_max_hour is not None:
            arr_time = flight['outbound']['arrival_time']
            # Handle both datetime.time objects and strings
            if isinstance(arr_time, str):
                arr_hour = int(arr_time.split(':')[0])
            else:
                arr_hour = arr_time.hour
            
            if arr_min_hour is not None and arr_hour < arr_min_hour:
                continue
            if arr_max_hour is not None and arr_hour > arr_max_hour:
                continue
        
        # Also check return flight times if it exists
        if flight.get('return'):
            if dep_min_hour is not None or dep_max_hour is not None:
                ret_dep_time = flight['return']['departure_time']
                # Handle both datetime.time objects and strings
                if isinstance(ret_dep_time, str):
                    ret_dep_hour = int(ret_dep_time.split(':')[0])
                else:
                    ret_dep_hour = ret_dep_time.hour
                
                if dep_min_hour is not None and ret_dep_hour < dep_min_hour:
                    continue
                if dep_max_hour is not None and ret_dep_hour > dep_max_hour:
                    continue
            
            if arr_min_hour is not None or arr_max_hour is not None:
                ret_arr_time = flight['return']['arrival_time']
                # Handle both datetime.time objects and strings
                if isinstance(ret_arr_time, str):
                    ret_arr_hour = int(ret_arr_time.split(':')[0])
                else:
                    ret_arr_hour = ret_arr_time.hour
                
                if arr_min_hour is not None and ret_arr_hour < arr_min_hour:
                    continue
                if arr_max_hour is not None and ret_arr_hour > arr_max_hour:
                    continue
        
        filtered.append(flight)
    
    return filtered


def display_single_search_results(flights, origin, destination):
    """Display results for single date search with visualizations (matching flexible search format)"""
    if not flights:
        st.warning("No flights found for your search criteria. Try different dates or airports.")
        return
    
    # Statistics
    prices = [f['price'] for f in flights]
    currency = flights[0]['currency'] if flights else 'EUR'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Flights", len(flights))
    with col2:
        st.metric("Cheapest", f"{currency} {min(prices):.2f}" if prices else "N/A")
    with col3:
        st.metric("Average", f"{currency} {sum(prices)/len(prices):.2f}" if prices else "N/A")
    with col4:
        st.metric("Most Expensive", f"{currency} {max(prices):.2f}" if prices else "N/A")
    
    # Top 5 Best Deals
    st.subheader("🏆 Top 5 Best Deals")
    
    # Sort by price (cheapest first) and show top 5
    sorted_flights = sorted(flights, key=lambda f: f['price'])[:5]
    
    for i, flight in enumerate(sorted_flights, 1):
        # Check if this is an open-jaw flight
        open_jaw_badge = "🔀 " if flight.get('is_open_jaw', False) else ""
        route_desc = f" - {flight.get('route_description', '')}" if flight.get('is_open_jaw', False) else ""
        
        with st.expander(
            f"#{i}: {open_jaw_badge}{flight['currency']} {flight['price']:.2f}{route_desc} - "
            f"{flight['outbound']['airline']} {flight['outbound']['flight_number']}"
            f"{' (Cheapest!)' if i == 1 else ''}",
            expanded=(i <= 2)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✈️ Outbound Flight**")
                outbound = flight['outbound']
                st.markdown(f"""
                - **Route:** {outbound['origin']} → {outbound['destination']}<br>
                - **Date:** {outbound['departure_date']}<br>
                - **Departure:** {outbound['departure_time']}<br>
                - **Arrival:** {outbound['arrival_time']}<br>
                - **Airline:** {get_airline_logo_html(outbound['airline'])}{outbound['flight_number']}<br>
                - **Stops:** {outbound['stops']}<br>
                - **Duration:** {outbound['duration']}<br>
                """, unsafe_allow_html=True)
            
            if flight['return']:
                with col2:
                    st.markdown("**🔙 Return Flight**")
                    return_flight = flight['return']
                    st.markdown(f"""
                    - **Route:** {return_flight['origin']} → {return_flight['destination']}<br>
                    - **Date:** {return_flight['departure_date']}<br>
                    - **Departure:** {return_flight['departure_time']}<br>
                    - **Arrival:** {return_flight['arrival_time']}<br>
                    - **Airline:** {get_airline_logo_html(return_flight['airline'])}{return_flight['flight_number']}<br>
                    - **Stops:** {return_flight['stops']}<br>
                    - **Duration:** {return_flight['duration']}<br>
                    """, unsafe_allow_html=True)
            
            st.markdown(f"**Seats Available:** {flight['number_of_bookable_seats']}")
            
            # Show open-jaw info if applicable
            if flight.get('is_open_jaw', False):
                st.info(
                    f"🔀 **Open-Jaw Flight:** This itinerary uses different airports. "
                    f"Route: {flight.get('route_description', 'N/A')}"
                )
            
            # Add track price button
            st.markdown("---")
            display_track_button(flight, f"single_{i}")
    
    # Visualizations
    st.subheader("📊 Price Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Price by Departure Time", "Price by Return Time", "Stops vs Price"])
    
    with tab1:
        try:
            # Create scatter plot for outbound departure time vs price
            import plotly.express as px
            from datetime import datetime
            
            departure_times = []
            prices_for_plot = []
            airlines = []
            hover_texts = []
            
            for f in flights:
                outbound = f['outbound']
                dep_time = outbound.get('departure_time')
                
                if dep_time:
                    # Convert time to decimal hours for plotting
                    if isinstance(dep_time, str):
                        time_parts = dep_time.split(':')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    else:  # datetime.time object
                        hours = dep_time.hour
                        minutes = dep_time.minute
                    
                    decimal_hour = hours + minutes / 60
                    departure_times.append(decimal_hour)
                    prices_for_plot.append(f['price'])
                    airlines.append(outbound['airline'])
                    hover_texts.append(
                        f"Airline: {outbound['airline']} {outbound['flight_number']}<br>"
                        f"Departure: {dep_time}<br>"
                        f"Price: {f['currency']} {f['price']:.2f}<br>"
                        f"Stops: {outbound['stops']}"
                    )
            
            if departure_times:
                fig = px.scatter(
                    x=departure_times,
                    y=prices_for_plot,
                    color=airlines,
                    labels={'x': 'Departure Time (hour of day)', 'y': f'Price ({currency})'},
                    title='Price by Outbound Departure Time',
                    height=400
                )
                fig.update_traces(marker=dict(size=12), hovertemplate='%{text}')
                fig.update_xaxes(
                    tickmode='linear',
                    tick0=0,
                    dtick=2,
                    tickformat='.0f',
                    range=[0, 24]
                )
                
                # Update hover text for each trace
                for i, trace in enumerate(fig.data):
                    trace_indices = [j for j, a in enumerate(airlines) if a == trace.name]
                    trace.customdata = [hover_texts[j] for j in trace_indices]
                    trace.hovertemplate = '%{customdata}<extra></extra>'
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 Find the cheapest time of day to depart. Morning flights are often cheaper!")
            else:
                st.info("Not enough data to create departure time chart")
        except Exception as e:
            st.error(f"Error creating departure time chart: {str(e)}")
    
    with tab2:
        try:
            # Create scatter plot for return departure time vs price (for roundtrips)
            import plotly.express as px
            
            return_times = []
            prices_for_plot = []
            airlines = []
            hover_texts = []
            
            for f in flights:
                if f.get('return'):
                    return_flight = f['return']
                    ret_time = return_flight.get('departure_time')
                    
                    if ret_time:
                        # Convert time to decimal hours for plotting
                        if isinstance(ret_time, str):
                            time_parts = ret_time.split(':')
                            hours = int(time_parts[0])
                            minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                        else:  # datetime.time object
                            hours = ret_time.hour
                            minutes = ret_time.minute
                        
                        decimal_hour = hours + minutes / 60
                        return_times.append(decimal_hour)
                        prices_for_plot.append(f['price'])
                        airlines.append(return_flight['airline'])
                        hover_texts.append(
                            f"Airline: {return_flight['airline']} {return_flight['flight_number']}<br>"
                            f"Return Departure: {ret_time}<br>"
                            f"Total Price: {f['currency']} {f['price']:.2f}<br>"
                            f"Stops: {return_flight['stops']}"
                        )
            
            if return_times:
                fig = px.scatter(
                    x=return_times,
                    y=prices_for_plot,
                    color=airlines,
                    labels={'x': 'Return Departure Time (hour of day)', 'y': f'Price ({currency})'},
                    title='Price by Return Departure Time',
                    height=400
                )
                fig.update_traces(marker=dict(size=12))
                fig.update_xaxes(
                    tickmode='linear',
                    tick0=0,
                    dtick=2,
                    tickformat='.0f',
                    range=[0, 24]
                )
                
                # Update hover text
                for i, trace in enumerate(fig.data):
                    trace_indices = [j for j, a in enumerate(airlines) if a == trace.name]
                    trace.customdata = [hover_texts[j] for j in trace_indices]
                    trace.hovertemplate = '%{customdata}<extra></extra>'
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 Return flight timing can significantly affect total price!")
            else:
                st.info("No return flights to analyze (one-way search)")
        except Exception as e:
            st.error(f"Error creating return time chart: {str(e)}")
    
    with tab3:
        try:
            # Create box plot for stops vs price
            import plotly.express as px
            
            stops_data = []
            prices_for_plot = []
            
            for f in flights:
                outbound_stops = f['outbound'].get('stops', 'Unknown')
                stops_data.append(f"{outbound_stops} stops" if outbound_stops != 'Direct' else 'Direct')
                prices_for_plot.append(f['price'])
            
            if stops_data:
                fig = px.box(
                    x=stops_data,
                    y=prices_for_plot,
                    labels={'x': 'Number of Stops', 'y': f'Price ({currency})'},
                    title='Price Distribution by Number of Stops',
                    height=400,
                    color=stops_data
                )
                fig.update_traces(marker=dict(size=8))
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 Direct flights are usually more expensive. Compare the price difference!")
            else:
                st.info("Not enough data to create stops analysis")
        except Exception as e:
            st.error(f"Error creating stops chart: {str(e)}")
    
    # Full results table
    with st.expander("📋 View All Results"):
        st.caption(f"Showing all {len(flights)} flight options")
        
        # Column headers
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 1.5, 1.2, 1.5, 0.8, 1, 0.8, 1])
        with col1:
            st.markdown("**Dep. Date**")
        with col2:
            st.markdown("**Departure Direction**")
        with col3:
            st.markdown("**Ret. Date**")
        with col4:
            st.markdown("**Return Direction**")
        with col5:
            st.markdown("**Days**")
        with col6:
            st.markdown("**Price**")
        with col7:
            st.markdown("**Curr.**")
        with col8:
            st.markdown("**Track**")
        
        st.markdown("---")
        
        for idx, flight in enumerate(flights):
            outbound = flight['outbound']
            return_flight = flight.get('return')
            
            # Calculate days at destination for roundtrips
            days_there = "N/A"
            if return_flight:
                try:
                    from datetime import datetime
                    dep_date = datetime.fromisoformat(str(outbound['departure_date'])).date() if isinstance(outbound['departure_date'], str) else outbound['departure_date']
                    ret_date = datetime.fromisoformat(str(return_flight['departure_date'])).date() if isinstance(return_flight['departure_date'], str) else return_flight['departure_date']
                    days_there = (ret_date - dep_date).days
                except:
                    days_there = "N/A"
            
            # Create columns for the data
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 1.5, 1.2, 1.5, 0.8, 1, 0.8, 1])
            
            with col1:
                st.markdown(f"**{outbound.get('departure_date', 'N/A')}**")
            with col2:
                st.markdown(f"{outbound['origin']} → {outbound['destination']}")
            with col3:
                if return_flight:
                    st.markdown(f"**{return_flight.get('departure_date', 'N/A')}**")
                else:
                    st.markdown("—")
            with col4:
                if return_flight:
                    st.markdown(f"{return_flight['origin']} → {return_flight['destination']}")
                else:
                    st.markdown("One-way")
            with col5:
                st.markdown(f"{days_there}")
            with col6:
                st.markdown(f"**{flight['price']:.2f}**")
            with col7:
                st.markdown(f"{flight['currency']}")
            with col8:
                display_track_button(flight, f"all_results_{idx}")
            
            if idx < len(flights) - 1:
                st.markdown("---")


def display_multi_airport_results(flights, airport_routes):
    """Display results for single date search with multiple airports"""
    if not flights:
        st.warning("No flights found for any route. Try different dates or airports.")
        return
    
    st.success(f"✅ Found {len(flights)} flight options across {len(airport_routes)} routes!")
    
    # Group flights by route for easy comparison
    route_counts = {}
    route_best_prices = {}
    for flight in flights:
        route = flight.get('search_route', 'Unknown')
        route_counts[route] = route_counts.get(route, 0) + 1
        # Track cheapest price per route
        if route not in route_best_prices or flight['price'] < route_best_prices[route]:
            route_best_prices[route] = flight['price']
    
    # Show route summary
    st.info(f"🛫 Results per route: {', '.join([f'{route}: {count}' for route, count in sorted(route_counts.items())])}")
    
    # Statistics
    prices = [f['price'] for f in flights]
    currency = flights[0]['currency'] if flights else 'EUR'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Flights", len(flights))
    with col2:
        st.metric("Cheapest", f"{currency} {min(prices):.2f}" if prices else "N/A")
    with col3:
        st.metric("Average", f"{currency} {sum(prices)/len(prices):.2f}" if prices else "N/A")
    with col4:
        st.metric("Most Expensive", f"{currency} {max(prices):.2f}" if prices else "N/A")
    
    # Visualizations for multi-airport comparison
    st.subheader("📊 Route Comparison Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Price by Route", "Price by Departure Time", "Airlines by Route"])
    
    with tab1:
        try:
            # Create bar chart comparing routes
            import plotly.graph_objects as go
            
            routes = list(route_best_prices.keys())
            best_prices = [route_best_prices[r] for r in routes]
            avg_prices = []
            
            for route in routes:
                route_flights = [f for f in flights if f.get('search_route') == route]
                avg_price = sum(f['price'] for f in route_flights) / len(route_flights)
                avg_prices.append(avg_price)
            
            fig = go.Figure(data=[
                go.Bar(name='Cheapest', x=routes, y=best_prices, marker_color='lightgreen'),
                go.Bar(name='Average', x=routes, y=avg_prices, marker_color='lightblue')
            ])
            
            fig.update_layout(
                title="Price Comparison by Route",
                xaxis_title="Route",
                yaxis_title=f"Price ({currency})",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("💡 Compare routes to find the cheapest airport combination")
        except Exception as e:
            st.error(f"Error creating route comparison: {str(e)}")
    
    with tab2:
        try:
            # Create scatter plot: departure time vs price, colored by route
            import plotly.express as px
            
            departure_times = []
            prices_for_plot = []
            routes_for_plot = []
            hover_texts = []
            
            for f in flights:
                outbound = f['outbound']
                dep_time = outbound.get('departure_time')
                
                if dep_time:
                    # Convert time to decimal hours
                    if isinstance(dep_time, str):
                        time_parts = dep_time.split(':')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    else:  # datetime.time object
                        hours = dep_time.hour
                        minutes = dep_time.minute
                    
                    decimal_hour = hours + minutes / 60
                    departure_times.append(decimal_hour)
                    prices_for_plot.append(f['price'])
                    routes_for_plot.append(f.get('search_route', 'Unknown'))
                    hover_texts.append(
                        f"Route: {f.get('search_route', 'Unknown')}<br>"
                        f"Airline: {outbound['airline']} {outbound['flight_number']}<br>"
                        f"Departure: {dep_time}<br>"
                        f"Price: {f['currency']} {f['price']:.2f}"
                    )
            
            if departure_times:
                fig = px.scatter(
                    x=departure_times,
                    y=prices_for_plot,
                    color=routes_for_plot,
                    labels={'x': 'Departure Time (hour of day)', 'y': f'Price ({currency})', 'color': 'Route'},
                    title='Price by Departure Time (All Routes)',
                    height=400
                )
                fig.update_traces(marker=dict(size=12))
                fig.update_xaxes(
                    tickmode='linear',
                    tick0=0,
                    dtick=2,
                    tickformat='.0f',
                    range=[0, 24]
                )
                
                # Update hover text
                for i, trace in enumerate(fig.data):
                    trace_indices = [j for j, r in enumerate(routes_for_plot) if r == trace.name]
                    trace.customdata = [hover_texts[j] for j in trace_indices]
                    trace.hovertemplate = '%{customdata}<extra></extra>'
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("💡 See if certain routes have better prices at specific times")
            else:
                st.info("Not enough data to create departure time chart")
        except Exception as e:
            st.error(f"Error creating departure time chart: {str(e)}")
    
    with tab3:
        try:
            # Create grouped bar chart: airlines by route
            import plotly.graph_objects as go
            from collections import defaultdict
            
            # Group by route and airline
            route_airline_counts = defaultdict(lambda: defaultdict(int))
            route_airline_prices = defaultdict(lambda: defaultdict(list))
            
            for f in flights:
                route = f.get('search_route', 'Unknown')
                airline = f['outbound']['airline']
                route_airline_counts[route][airline] += 1
                route_airline_prices[route][airline].append(f['price'])
            
            # Get all unique airlines
            all_airlines = set()
            for route_data in route_airline_counts.values():
                all_airlines.update(route_data.keys())
            
            # Create traces for each airline
            fig = go.Figure()
            
            for airline in sorted(all_airlines):
                avg_prices_by_route = []
                routes = sorted(route_airline_counts.keys())
                
                for route in routes:
                    if airline in route_airline_prices[route]:
                        avg_price = sum(route_airline_prices[route][airline]) / len(route_airline_prices[route][airline])
                        avg_prices_by_route.append(avg_price)
                    else:
                        avg_prices_by_route.append(None)
                
                fig.add_trace(go.Bar(
                    name=airline,
                    x=routes,
                    y=avg_prices_by_route
                ))
            
            fig.update_layout(
                title="Average Price by Airline and Route",
                xaxis_title="Route",
                yaxis_title=f"Average Price ({currency})",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("💡 Compare which airlines are cheapest for each route")
        except Exception as e:
            st.error(f"Error creating airline comparison: {str(e)}")
    
    # Top 5 Best Deals
    st.subheader("🏆 Top 5 Best Deals")
    
    sorted_flights = sorted(flights, key=lambda f: f['price'])[:5]
    
    for i, flight in enumerate(sorted_flights, 1):
        route = flight.get('search_route', 'Unknown')
        
        with st.expander(
            f"#{i}: {flight['currency']} {flight['price']:.2f} - [{route}] "
            f"{flight['outbound']['airline']} {flight['outbound']['flight_number']}"
            f"{' (Cheapest!)' if i == 1 else ''}",
            expanded=(i <= 2)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✈️ Outbound Flight**")
                outbound = flight['outbound']
                st.markdown(f"""
                - **Route:** {outbound['origin']} → {outbound['destination']}<br>
                - **Date:** {outbound['departure_date']}<br>
                - **Departure:** {outbound['departure_time']}<br>
                - **Arrival:** {outbound['arrival_time']}<br>
                - **Airline:** {get_airline_logo_html(outbound['airline'])}{outbound['flight_number']}<br>
                - **Stops:** {outbound['stops']}<br>
                - **Duration:** {outbound['duration']}<br>
                """, unsafe_allow_html=True)
            if flight['return']:
                with col2:
                    st.markdown("**🔙 Return Flight**")
                    return_flight = flight['return']
                    st.markdown(f"""
                    - **Route:** {return_flight['origin']} → {return_flight['destination']}<br>
                    - **Date:** {return_flight['departure_date']}<br>
                    - **Departure:** {return_flight['departure_time']}<br>
                    - **Arrival:** {return_flight['arrival_time']}<br>
                    - **Airline:** {get_airline_logo_html(return_flight['airline'])}{return_flight['flight_number']}<br>
                    - **Stops:** {return_flight['stops']}<br>
                    - **Duration:** {return_flight['duration']}<br>
                    """, unsafe_allow_html=True)
            st.markdown(f"**Seats Available:** {flight['number_of_bookable_seats']}")
            
            # Add track price button
            st.markdown("---")
            display_track_button(flight, f"multi_{i}")
    
    # Full results table
    with st.expander("📋 View All Flights"):
        df_data = []
        for flight in flights:
            outbound = flight['outbound']
            return_flight = flight.get('return')
            df_data.append({
                'Route': flight.get('search_route', 'Unknown'),
                'Price': flight['price'],
                'Currency': flight['currency'],
                'Outbound': f"{outbound['airline']} {outbound['flight_number']}",
                'Departure': outbound['departure_time'],
                'Return': f"{return_flight['airline']} {return_flight['flight_number']}" if return_flight else 'N/A',
                'Stops': outbound['stops'],
                'Seats': flight['number_of_bookable_seats']
            })
        
        import pandas as pd
        df = pd.DataFrame(df_data)
        df = df.sort_values('Price')
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_date_range_results(results, origin, destination, duration_mode=None):
    """Display results for date range search with visualizations (supports multi-airport)"""
    # Statistics
    stats = BatchFlightSearch(AmadeusClient()).get_statistics(results)
    
    # Check if this is multi-airport search
    is_multi_airport = any(r.origin or r.destination for r in results)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Searches", stats['total_searches'])
    with col2:
        st.metric("Found Flights", stats['successful_searches'])
    with col3:
        if stats['min_price']:
            st.metric("Cheapest", f"{stats['currency']} {stats['min_price']:.2f}")
    with col4:
        if stats['avg_price']:
            st.metric("Average", f"{stats['currency']} {stats['avg_price']:.2f}")
    
    # Best deals
    st.subheader("🏆 Best Deals")
    
    # Filter successful results
    successful_results = [r for r in results if r.success and r.cheapest_price is not None]
    
    # Sort based on duration mode
    if duration_mode == "Maximum days possible":
        # Sort by duration (longest first), then by price
        best_deals = sorted(successful_results, 
                           key=lambda r: (-r.total_duration, r.cheapest_price))[:5]
        st.info("📏 Showing longest stays with best prices")
    else:
        # Sort by price (cheapest first)
        best_deals = sorted(successful_results, 
                           key=lambda r: r.cheapest_price)[:5]
    
    for i, result in enumerate(best_deals, 1):
        # Show route info for multi-airport searches
        route_info = f" [{result.origin}→{result.destination}]" if is_multi_airport and result.origin else ""
        
        with st.expander(
            f"#{i}: {result.currency} {result.cheapest_price:.2f} - "
            f"{result.departure_date.strftime('%b %d')} → {result.return_date.strftime('%b %d')} "
            f"({result.total_duration} days){route_info}",
            expanded=(i <= 2)
        ):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                **Trip Details:**
                - Departure: {result.departure_date.strftime('%A, %B %d')}
                - Return: {result.return_date.strftime('%A, %B %d')}
                - Days at destination: {result.days_at_destination}
                - Total duration: {result.total_duration} days
                {f"- Route: {result.origin} → {result.destination}" if is_multi_airport and result.origin else ""}
                """)
            
            with col2:
                if result.cheapest_flight:
                    flight = result.cheapest_flight
                    outbound = flight['outbound']
                    st.markdown(f"""
                    **Best Flight:**<br>
                    - Price: {result.currency} {result.cheapest_price:.2f}<br>
                    - Outbound: {get_airline_logo_html(outbound['airline'])}<b>{outbound['airline']}</b> {outbound['flight_number']} at {outbound['departure_time']}<br>
                    - Stops: {outbound['stops']}<br>
                    """, unsafe_allow_html=True)
                    
                    if flight['return']:
                        ret = flight['return']
                        st.markdown(f"- Return: {get_airline_logo_html(ret['airline'])}<b>{ret['airline']}</b> {ret['flight_number']} at {ret['departure_time']}", unsafe_allow_html=True)
                    
                    # Add track price button for the cheapest flight
                    st.markdown("---")
                    display_track_button(result.cheapest_flight, f"flex_{i}")
    
    # Visualizations
    st.subheader("📊 Price Analysis")
    
    # Determine if multi-airport search
    dep_airports = set([getattr(r, 'origin', None) for r in results if getattr(r, 'origin', None)])
    arr_airports = set([getattr(r, 'destination', None) for r in results if getattr(r, 'destination', None)])
    multi_airport = len(dep_airports) > 1 or len(arr_airports) > 1

    tab_names = ["Price Heatmap"]
    if multi_airport:
        tab_names.append("Airport Price Comparison")
    else:
        tab_names.append("Distribution")
    tab_names += ["Duration vs Price", "Calendar View"]
    tab1, tab2, tab3, tab4 = st.tabs(tab_names)

    with tab1:
        try:
            fig = create_price_heatmap(results)
            st.plotly_chart(fig, width="stretch")
            st.caption("Green = Cheaper, Red = More Expensive")
        except Exception as e:
            st.error(f"Error creating price heatmap: {str(e)}")
            st.info("Try adjusting your search parameters or time filters.")

    with tab2:
        if multi_airport:
            try:
                from src.visualization.heatmap import create_airport_price_comparison
                figs = create_airport_price_comparison(results)
                for fig in figs:
                    st.plotly_chart(fig, width="stretch")
                st.caption("Shows average, min, and median prices per airport. Only available for multi-airport searches.")
            except Exception as e:
                st.error(f"Error creating airport price comparison: {str(e)}")
        else:
            try:
                fig = create_price_distribution(results)
                st.plotly_chart(fig, width="stretch")
            except Exception as e:
                st.error(f"Error creating price distribution: {str(e)}")

    with tab3:
        try:
            fig = create_price_by_duration(results)
            st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.error(f"Error creating duration vs price chart: {str(e)}")

    with tab4:
        try:
            fig = create_calendar_view(results)
            st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.error(f"Error creating calendar view: {str(e)}")
    
    # Full results table
    with st.expander("📋 View All Results"):
        # Filter results with valid flights
        valid_results = [r for r in results if r.success and r.cheapest_price and r.cheapest_flight]
        st.caption(f"Showing {len(valid_results)} date combinations with available flights")
        
        if valid_results:
            # Column headers
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 1.5, 1.2, 1.5, 0.8, 1, 0.8, 1])
            with col1:
                st.markdown("**Dep. Date**")
            with col2:
                st.markdown("**Departure Direction**")
            with col3:
                st.markdown("**Ret. Date**")
            with col4:
                st.markdown("**Return Direction**")
            with col5:
                st.markdown("**Days**")
            with col6:
                st.markdown("**Price**")
            with col7:
                st.markdown("**Curr.**")
            with col8:
                st.markdown("**Track**")
            
            st.markdown("---")
            
            for idx, r in enumerate(valid_results):
                flight = r.cheapest_flight
                outbound = flight['outbound']
                return_flight = flight.get('return')
                
                # Create columns for the data
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.2, 1.5, 1.2, 1.5, 0.8, 1, 0.8, 1])
                
                with col1:
                    st.markdown(f"**{r.departure_date.strftime('%b %d')}**")
                with col2:
                    st.markdown(f"{outbound['origin']} → {outbound['destination']}")
                with col3:
                    if return_flight:
                        st.markdown(f"**{r.return_date.strftime('%b %d')}**")
                    else:
                        st.markdown("—")
                with col4:
                    if return_flight:
                        st.markdown(f"{return_flight['origin']} → {return_flight['destination']}")
                    else:
                        st.markdown("One-way")
                with col5:
                    st.markdown(f"{r.days_at_destination}")
                with col6:
                    st.markdown(f"**{r.cheapest_price:.2f}**")
                with col7:
                    st.markdown(f"{r.currency}")
                with col8:
                    display_track_button(flight, f"flex_all_{idx}")
                
                if idx < len(valid_results) - 1:
                    st.markdown("---")
        else:
            st.info("No flight results available to display")


def main():
    """Main application"""
    
    # Header
    st.title("✈️ CoolFlightPrices")
    st.markdown("*Find the best flight deals and track prices over time*")
    
    # Check credentials
    if not check_api_credentials():
        st.stop()
    
    # Page selection in sidebar
    page = st.sidebar.radio(
        "Navigate",
        ["🔍 Search Flights", "📊 Price Tracker"],
        label_visibility="collapsed"
    )
    
    if page == "📊 Price Tracker":
        display_tracker_tab()
        return
    
    # Sidebar for search parameters
    st.sidebar.header("🔍 Search Flights")
    
    # Search mode selection
    search_mode = st.sidebar.radio(
        "Search Mode",
        ["💡 Flexible Dates (Date Range)", "📅 Single Date"],
        help="Flexible Dates: Compare prices across multiple date combinations\nSingle Date: Search for specific dates"
    )
    
    # Origin and destination (common for both modes)
    with st.sidebar:
        st.markdown("### 🛫 Airports")
        
        # Get all airport options for dropdown
        all_airport_options = get_all_airport_options()
        
        # Multi-airport toggle
        multi_airport = st.checkbox(
            "Compare multiple airports",
            value=False,
            help="Search multiple origin and/or destination airports to find the best deal"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if multi_airport:
                # Multiselect for multiple origins (no default to avoid conflicts)
                selected_origins = st.multiselect(
                    "From (select one or more)",
                    options=all_airport_options,
                    default=[],
                    help="Start typing to search airports by city, country, or code"
                )
                # Extract airport codes from selections
                origins = [opt.split(' - ')[0].strip() for opt in selected_origins] if selected_origins else []
            else:
                # Selectbox for single origin
                default_origin = "ZRH - Zurich, Switzerland"
                selected_origin = st.selectbox(
                    "From",
                    options=all_airport_options,
                    index=all_airport_options.index(default_origin) if default_origin in all_airport_options else 0,
                    help="Start typing to search airports"
                )
                # Extract airport code from selection
                origin = selected_origin.split(' - ')[0].strip() if selected_origin else ""
                origins = [origin] if origin else []
                
        with col2:
            if multi_airport:
                # Multiselect for multiple destinations (no default to avoid conflicts)
                selected_destinations = st.multiselect(
                    "To (select one or more)",
                    options=all_airport_options,
                    default=[],
                    help="Start typing to search airports by city, country, or code"
                )
                # Extract airport codes from selections
                destinations = [opt.split(' - ')[0].strip() for opt in selected_destinations] if selected_destinations else []
            else:
                # Selectbox for single destination
                default_destination = "LIS - Lisbon, Portugal"
                selected_destination = st.selectbox(
                    "To",
                    options=all_airport_options,
                    index=all_airport_options.index(default_destination) if default_destination in all_airport_options else 0,
                    help="Start typing to search airports"
                )
                # Extract airport code from selection
                destination = selected_destination.split(' - ')[0].strip() if selected_destination else ""
                destinations = [destination] if destination else []
        
        # Open-jaw toggle (only show if multi-airport is enabled and we have roundtrip)
        allow_open_jaw = False
        if multi_airport and search_mode == "📅 Single Date":
            allow_open_jaw = st.checkbox(
                "🔀 Allow different return airports (open-jaw)",
                value=False,
                help="Search for flights where you return from/to different airports. "
                     "Example: ZRH→LIS outbound, OPO→ZRH return. May find cheaper deals!"
            )
            
            if allow_open_jaw:
                st.info(
                    "💡 **Open-jaw mode enabled!** The app will search for combinations where:\n"
                    "- You can fly to any selected destination airport\n"
                    "- You can return from any selected destination airport (may be different)\n"
                    "- You must return to one of your origin airports\n\n"
                    "This can find significantly cheaper deals, especially in Europe!"
                )
        
        # Show airport combination count and validation
        if multi_airport:
            if not origins or not destinations:
                st.warning("⚠️ Please select at least one origin and one destination airport")
            elif origins and destinations:
                if allow_open_jaw:
                    # Open-jaw: all permutations of outbound + return
                    num_outbound = len(origins) * len(destinations)
                    num_return = len(destinations) * len(origins)
                    total_combinations = num_outbound  # Each outbound can pair with multiple returns
                    st.info(
                        f"🔀 **Open-jaw search:** {num_outbound} outbound route{'s' if num_outbound > 1 else ''} × "
                        f"multiple return options = testing all possible combinations!\n"
                        f"This will use 1 API call per unique open-jaw combination."
                    )
                    if total_combinations > 15:
                        st.warning("⚠️ Many combinations will take longer and use more API quota!")
                else:
                    # Normal roundtrip: same origin-destination pairs
                    num_combinations = len(origins) * len(destinations)
                    if num_combinations > 1:
                        st.info(f"🔄 Will search {num_combinations} airport combination{'s' if num_combinations > 1 else ''}: "
                               f"{len(origins)} origin × {len(destinations)} destination")
                        if num_combinations > 10:
                            st.warning("⚠️ Searching many airports will use more API calls and take longer!")
                    else:
                        st.info(f"✈️ Searching {origins[0]} → {destinations[0]}")
        elif not origins or not destinations:
            st.warning("⚠️ Please select origin and destination airports")
    
    # Mode-specific UI
    if search_mode == "💡 Flexible Dates (Date Range)":
        params = date_range_search_ui(st.sidebar)
        if params is None:
            st.stop()
        search_button = st.sidebar.button("🔍 Search Date Range", type="primary", width="stretch")
    else:
        departure_date, return_date, adults, max_results, dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour = single_date_search_ui(st.sidebar)
        search_button = st.sidebar.button("🔍 Search Flights", type="primary", width="stretch")
    
    # Main content area
    if search_button:
        # Store search parameters in session state
        st.session_state.last_search_mode = search_mode
        st.session_state.last_origins = origins
        st.session_state.last_destinations = destinations
        st.session_state.last_allow_open_jaw = allow_open_jaw if multi_airport else False
        
        # Generate route combinations based on search mode
        if allow_open_jaw and multi_airport:
            # Open-jaw mode: Generate all permutations of (origin→dest, dest2→origin2)
            # where dest2 can be any destination airport and origin2 can be any origin airport
            open_jaw_routes = []
            for out_origin in origins:
                for out_dest in destinations:
                    for ret_origin in destinations:  # Return FROM any destination
                        for ret_dest in origins:  # Return TO any origin
                            # Create tuple: ((outbound_origin, outbound_dest), (return_origin, return_dest))
                            route = ((out_origin, out_dest), (ret_origin, ret_dest))
                            # Add route metadata
                            is_truly_open_jaw = (out_origin != ret_dest) or (out_dest != ret_origin)
                            open_jaw_routes.append({
                                'route': route,
                                'is_open_jaw': is_truly_open_jaw,
                                'label': f"{out_origin}→{out_dest} / {ret_origin}→{ret_dest}"
                            })
            st.session_state.last_airport_routes = open_jaw_routes
        else:
            # Normal roundtrip mode: Same origin-destination pairs
            st.session_state.last_airport_routes = [(orig, dest) for orig in origins for dest in destinations]
        
        # Validate inputs
        if not origins:
            st.error("Please enter at least one origin airport code")
            st.stop()
        
        if not destinations:
            st.error("Please enter at least one destination airport code")
            st.stop()
        
        # Validate all airport codes
        invalid_origins = [code for code in origins if len(code) != 3]
        invalid_destinations = [code for code in destinations if len(code) != 3]
        
        if invalid_origins:
            st.error(f"Invalid origin airport codes (must be 3 letters): {', '.join(invalid_origins)}")
            st.stop()
        
        if invalid_destinations:
            st.error(f"Invalid destination airport codes (must be 3 letters): {', '.join(invalid_destinations)}")
            st.stop()
        
        # Create airport route combinations
        airport_routes = st.session_state.last_airport_routes
        
        try:
            client = AmadeusClient()
            
            if search_mode == "💡 Flexible Dates (Date Range)":
                # Date range search with multiple airports
                if len(airport_routes) == 1:
                    st.subheader(f"📊 Flexible Date Search: {origins[0]} → {destinations[0]}")
                else:
                    st.subheader(f"📊 Flexible Date Search: {len(origins)} origin(s) × {len(destinations)} destination(s)")
                    st.caption(f"Comparing: {', '.join([f'{o}→{d}' for o, d in airport_routes])}")
                
                # Generate date combinations
                if params['use_sampling']:
                    st.info("Using smart sampling to reduce API calls...")
                    combinations = smart_sample_dates(
                        params['dep_start'], params['dep_end'],
                        params['ret_start'], params['ret_end'],
                        target_combinations=25,
                        min_days_at_destination=params['min_days'],
                        max_days_at_destination=params.get('max_days')
                    )
                else:
                    combinations = generate_date_combinations(
                        params['dep_start'], params['dep_end'],
                        params['ret_start'], params['ret_end'],
                        params['min_days'],
                        params.get('max_days')
                    )
                
                total_searches = len(combinations) * len(airport_routes)
                st.info(f"Searching {len(combinations)} date combinations × {len(airport_routes)} airport route(s) = {total_searches} total searches")
                
                if total_searches > 100:
                    st.warning("⚠️ This will make many API calls and may take several minutes. Consider enabling 'Use Smart Sampling' to reduce calls.")
                
                # Show time filter info if applied
                if any([params.get('dep_min_hour'), params.get('dep_max_hour'), params.get('arr_min_hour'), params.get('arr_max_hour')]):
                    filter_info = []
                    if params.get('dep_min_hour') is not None or params.get('dep_max_hour') is not None:
                        filter_info.append(f"Departure: {params.get('dep_min_hour') or 0}:00-{params.get('dep_max_hour') or 23}:00")
                    if params.get('arr_min_hour') is not None or params.get('arr_max_hour') is not None:
                        filter_info.append(f"Arrival: {params.get('arr_min_hour') or 0}:00-{params.get('arr_max_hour') or 23}:00")
                    st.info(f"⏰ Time filters: {', '.join(filter_info)}")
                
                # For maximum days mode, add info about strategy
                if params.get('duration_mode') == "Maximum days possible":
                    st.info("🎯 Prioritizing longest possible stays in results...")
                
                # Batch search with progress for all airport combinations
                batch_search = BatchFlightSearch(client)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                all_results = []
                
                for route_idx, (origin, destination) in enumerate(airport_routes):
                    route_label = f"{origin}→{destination}"
                    
                    def update_progress(current, total, message):
                        overall_progress = (route_idx * len(combinations) + current) / total_searches
                        progress_bar.progress(overall_progress)
                        status_text.text(f"[{route_label}] {message} ({route_idx + 1}/{len(airport_routes)} routes)")
                    
                    results = batch_search.search_date_range(
                        origin=origin,
                        destination=destination,
                        date_combinations=combinations,
                        adults=params['adults'],
                        progress_callback=update_progress
                    )
                    
                    # Add route info to each result
                    for result in results:
                        result.origin = origin
                        result.destination = destination
                    
                    all_results.extend(results)
                
                progress_bar.progress(1.0)
                status_text.text(f"✅ Completed all {len(airport_routes)} routes!")
                
                if not all_results:
                    st.warning("No flights found for any route/date combination. Try different criteria.")
                    st.stop()
                
                progress_bar.empty()
                status_text.empty()
                
                # Apply time filters to all results if set
                if any([params.get('dep_min_hour'), params.get('dep_max_hour'), params.get('arr_min_hour'), params.get('arr_max_hour')]):
                    filtered_results = []
                    for result in all_results:
                        if result.success and result.all_flights:
                            # Filter flights within this date combination
                            from copy import copy
                            filtered_flights = filter_flights_by_time(
                                result.all_flights,
                                params.get('dep_min_hour'),
                                params.get('dep_max_hour'),
                                params.get('arr_min_hour'),
                                params.get('arr_max_hour')
                            )
                            if filtered_flights:
                                # Create a new result with filtered data
                                filtered_result = copy(result)
                                filtered_result.all_flights = filtered_flights
                                filtered_result.cheapest_price = min(f['price'] for f in filtered_flights)
                                filtered_result.cheapest_flight = min(filtered_flights, key=lambda f: f['price'])
                                filtered_result.flights_found = len(filtered_flights)
                                filtered_results.append(filtered_result)
                    
                    original_count = len([r for r in all_results if r.success])
                    if len(filtered_results) < original_count:
                        st.info(f"🔍 Time filters applied: {len(filtered_results)} of {original_count} date combinations have flights within your time preferences")
                    
                    all_results = filtered_results
                
                # Display results (handles both single and multi-airport)
                st.session_state.search_results = all_results
                st.session_state.search_params = params
                display_date_range_results(all_results, None, None, params.get('duration_mode'))
                
            else:
                # Single date search with multiple airports
                if len(airport_routes) == 1:
                    st.subheader("Search Results")
                    st.markdown(f"""
                    **Route:** {origins[0]} → {destinations[0]}  
                    **Departure:** {departure_date}  
                    {"**Return:** " + str(return_date) if return_date else "**Trip Type:** One-way"}  
                    **Passengers:** {adults} adult(s)
                    """)
                else:
                    st.subheader(f"Search Results: {len(airport_routes)} Route(s)")
                    st.caption(f"Comparing: {', '.join([f'{o}→{d}' for o, d in airport_routes])}")
                
                # Show time filter info if applied
                if any([dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour]):
                    filter_info = []
                    if dep_min_hour is not None or dep_max_hour is not None:
                        filter_info.append(f"Departure: {dep_min_hour or 0}:00-{dep_max_hour or 23}:00")
                    if arr_min_hour is not None or arr_max_hour is not None:
                        filter_info.append(f"Arrival: {arr_min_hour or 0}:00-{arr_max_hour or 23}:00")
                    st.info(f"⏰ Time filters: {', '.join(filter_info)}")
                
                all_flights = []
                
                # Check if we're in open-jaw mode
                is_open_jaw_mode = isinstance(airport_routes, list) and len(airport_routes) > 0 and isinstance(airport_routes[0], dict)
                
                if is_open_jaw_mode:
                    # Open-jaw mode: Search using multi-city API
                    for route_info in airport_routes:
                        route = route_info['route']
                        is_truly_open_jaw = route_info['is_open_jaw']
                        label = route_info['label']
                        
                        # route is ((out_origin, out_dest), (ret_origin, ret_dest))
                        (out_origin, out_dest), (ret_origin, ret_dest) = route
                        
                        with st.spinner(f"🔄 Searching {label}..."):
                            try:
                                # Use multi-city API for open-jaw
                                flights = client.get_cheapest_multi_city(
                                    origin_destination_pairs=[(out_origin, out_dest), (ret_origin, ret_dest)],
                                    departure_dates=[departure_date, return_date] if return_date else [departure_date],
                                    adults=adults,
                                    max_results=max_results,
                                    currency="EUR"
                                )
                                
                                # Add route info and open-jaw indicator to each flight
                                for flight in flights:
                                    flight['search_route'] = label
                                    flight['is_open_jaw'] = is_truly_open_jaw
                                    if 'route_description' not in flight:
                                        flight['route_description'] = label
                                
                                all_flights.extend(flights)
                                
                            except Exception as e:
                                st.warning(f"⚠️ Error searching {label}: {str(e)}")
                                continue
                else:
                    # Normal roundtrip mode: Search all airport combinations
                    for origin, destination in airport_routes:
                        route_label = f"{origin}→{destination}"
                        
                        with st.spinner(f"🔄 Searching {route_label}..."):
                            try:
                                flights = client.get_cheapest_flights(
                                    origin=origin,
                                    destination=destination,
                                    departure_date=departure_date,
                                    return_date=return_date,
                                    adults=adults,
                                    max_results=max_results
                                )
                                
                                # Add route info to each flight
                                for flight in flights:
                                    flight['search_route'] = route_label
                                    flight['is_open_jaw'] = False  # Regular roundtrip
                                
                                all_flights.extend(flights)
                                
                            except Exception as e:
                                st.warning(f"⚠️ Error searching {route_label}: {str(e)}")
                                continue
                
                if not all_flights:
                    st.warning("No flights found for any route. Try different dates or airports.")
                    st.stop()
                
                # Apply time filters if set
                if any([dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour]):
                    original_count = len(all_flights)
                    all_flights = filter_flights_by_time(all_flights, dep_min_hour, dep_max_hour, arr_min_hour, arr_max_hour)
                    if len(all_flights) < original_count:
                        st.info(f"🔍 Filtered to {len(all_flights)} flights (removed {original_count - len(all_flights)} outside time preferences)")
                
                # Sort by price
                all_flights.sort(key=lambda f: f['price'])
                
                # Store results in session state
                st.session_state.search_results = all_flights
                st.session_state.single_search_params = {
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'adults': adults
                }
                
                # Display results
                if len(airport_routes) == 1:
                    display_single_search_results(all_flights, origins[0], destinations[0])
                else:
                    display_multi_airport_results(all_flights, airport_routes)
            
        except Exception as e:
            st.error(f"❌ Error searching for flights: {str(e)}")
            st.info("""
            **Troubleshooting:**
            - Check your API credentials
            - Verify airport codes are valid (3-letter IATA codes)
            - Check if you've exceeded your API quota
            - Try different dates or airports
            """)
    
    elif 'search_results' in st.session_state and st.session_state.search_results:
        # Display previously stored search results after rerun
        if st.session_state.last_search_mode == "💡 Flexible Dates (Date Range)":
            # Re-display flexible date results
            all_results = st.session_state.search_results
            params = st.session_state.search_params
            airport_routes = st.session_state.last_airport_routes
            origins = st.session_state.last_origins
            destinations = st.session_state.last_destinations
            
            if len(airport_routes) == 1:
                st.subheader(f"📊 Flexible Date Search: {origins[0]} → {destinations[0]}")
            else:
                st.subheader(f"📊 Flexible Date Search: {len(origins)} origin(s) × {len(destinations)} destination(s)")
                st.caption(f"Comparing: {', '.join([f'{o}→{d}' for o, d in airport_routes])}")
            
            st.info("✅ Showing previous search results. Change search criteria and click search to update.")
            display_date_range_results(all_results, None, None, params.get('duration_mode'))
        else:
            # Re-display single date results
            all_flights = st.session_state.search_results
            single_params = st.session_state.single_search_params
            airport_routes = st.session_state.last_airport_routes
            origins = st.session_state.last_origins
            destinations = st.session_state.last_destinations
            
            if len(airport_routes) == 1:
                st.subheader("Search Results")
                st.markdown(f"""
                **Route:** {origins[0]} → {destinations[0]}  
                **Departure:** {single_params['departure_date']}  
                {"**Return:** " + str(single_params['return_date']) if single_params['return_date'] else "**Trip Type:** One-way"}  
                **Passengers:** {single_params['adults']} adult(s)
                """)
            else:
                st.subheader(f"Search Results: {len(airport_routes)} Route(s)")
                st.caption(f"Comparing: {', '.join([f'{o}→{d}' for o, d in airport_routes])}")
            
            st.info("✅ Showing previous search results. Change search criteria and click search to update.")
            
            if len(airport_routes) == 1:
                display_single_search_results(all_flights, origins[0], destinations[0])
            else:
                display_multi_airport_results(all_flights, airport_routes)
    
    else:
        # Welcome message
        st.info("""
        👈 Use the sidebar to search for flights
        
        **New! Flexible Date Search:**
        - Compare prices across multiple date combinations
        - Set departure and return date ranges
        - Specify minimum days at destination
        - View price heatmaps and trends
        - Find the cheapest option within your flexibility
        
        **Features:**
        - Search flights using Amadeus API
        - Single date or flexible date range search
        - Interactive price visualizations
        - Compare prices across dates
        
        **Popular Airport Codes:**
        - ZRH: Zurich, Switzerland
        - LIS: Lisbon, Portugal
        - JFK: New York, USA
        - LHR: London, UK
        - CDG: Paris, France
        - BCN: Barcelona, Spain
        """)
        
        # Display API status
        try:
            client = AmadeusClient()
            st.success("✅ Amadeus API connected")
        except:
            st.error("❌ Amadeus API not connected - check your credentials")


if __name__ == "__main__":
    main()
