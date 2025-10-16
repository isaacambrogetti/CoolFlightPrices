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
    create_calendar_view
)
from config.settings import Config


# Page configuration
st.set_page_config(
    page_title="CoolFlightPrices",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
    
    return departure_date, return_date, adults, max_results


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
            dep_end = st.date_input(
                "Latest",
                value=default_dep_end,
                min_value=dep_start,
                help="Latest you can depart",
                key="dep_end"
            )
        
        st.markdown("### 🔙 Return Date Range")
        col1, col2 = st.columns(2)
        
        default_ret_start = default_dep_end + timedelta(days=3)
        default_ret_end = default_ret_start + timedelta(days=4)
        
        with col1:
            ret_start = st.date_input(
                "Earliest",
                value=default_ret_start,
                min_value=dep_start + timedelta(days=1),
                help="Earliest you can return",
                key="ret_start"
            )
        with col2:
            ret_end = st.date_input(
                "Latest",
                value=default_ret_end,
                min_value=ret_start,
                help="Latest you can return",
                key="ret_end"
            )
        
        # Minimum days at destination
        min_days = st.slider(
            "Minimum full days at destination",
            min_value=0,
            max_value=14,
            value=2,
            help="Minimum complete days you want to spend at destination (arrival/departure days don't count)"
        )
        
        # Passengers
        adults = st.number_input(
            "Adults",
            min_value=1,
            max_value=9,
            value=1,
            key="adults_range"
        )
        
        # Calculate combinations
        try:
            stats = estimate_api_calls(dep_start, dep_end, ret_start, ret_end, min_days)
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
        'adults': adults,
        'use_sampling': use_sampling if num_combinations > 50 else False
    }


def display_single_search_results(flights, origin, destination):
    """Display results for single date search"""
    if not flights:
        st.warning("No flights found for your search criteria. Try different dates or airports.")
        return
    
    st.success(f"✅ Found {len(flights)} flight options!")
    
    # Display flights
    for i, flight in enumerate(flights, 1):
        with st.expander(
            f"💰 {flight['currency']} {flight['price']:.2f} - "
            f"{flight['outbound']['airline']} {flight['outbound']['flight_number']}"
            f"{' (Cheapest!)' if i == 1 else ''}",
            expanded=(i <= 3)
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✈️ Outbound Flight**")
                outbound = flight['outbound']
                st.markdown(f"""
                - **Route:** {outbound['origin']} → {outbound['destination']}
                - **Date:** {outbound['departure_date']}
                - **Departure:** {outbound['departure_time']}
                - **Arrival:** {outbound['arrival_time']}
                - **Airline:** {outbound['airline']} {outbound['flight_number']}
                - **Stops:** {outbound['stops']}
                - **Duration:** {outbound['duration']}
                """)
            
            if flight['return']:
                with col2:
                    st.markdown("**🔙 Return Flight**")
                    return_flight = flight['return']
                    st.markdown(f"""
                    - **Route:** {return_flight['origin']} → {return_flight['destination']}
                    - **Date:** {return_flight['departure_date']}
                    - **Departure:** {return_flight['departure_time']}
                    - **Arrival:** {return_flight['arrival_time']}
                    - **Airline:** {return_flight['airline']} {return_flight['flight_number']}
                    - **Stops:** {return_flight['stops']}
                    - **Duration:** {return_flight['duration']}
                    """)
            
            st.markdown(f"**Seats Available:** {flight['number_of_bookable_seats']}")


def display_date_range_results(results, origin, destination):
    """Display results for date range search with visualizations"""
    # Statistics
    stats = BatchFlightSearch(AmadeusClient()).get_statistics(results)
    
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
    best_deals = [r for r in results if r.success and r.cheapest_price is not None][:5]
    
    for i, result in enumerate(best_deals, 1):
        with st.expander(
            f"#{i}: {result.currency} {result.cheapest_price:.2f} - "
            f"{result.departure_date.strftime('%b %d')} → {result.return_date.strftime('%b %d')} "
            f"({result.total_duration} days)",
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
                """)
            
            with col2:
                if result.cheapest_flight:
                    flight = result.cheapest_flight
                    outbound = flight['outbound']
                    st.markdown(f"""
                    **Best Flight:**
                    - Price: {result.currency} {result.cheapest_price:.2f}
                    - Outbound: {outbound['airline']} {outbound['flight_number']} at {outbound['departure_time']}
                    - Stops: {outbound['stops']}
                    """)
                    
                    if flight['return']:
                        ret = flight['return']
                        st.markdown(f"- Return: {ret['airline']} {ret['flight_number']} at {ret['departure_time']}")
    
    # Visualizations
    st.subheader("📊 Price Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Price Heatmap", "Distribution", "Duration vs Price", "Calendar View"])
    
    with tab1:
        st.plotly_chart(create_price_heatmap(results), use_container_width=True)
        st.caption("Green = Cheaper, Red = More Expensive")
    
    with tab2:
        st.plotly_chart(create_price_distribution(results), use_container_width=True)
    
    with tab3:
        st.plotly_chart(create_price_by_duration(results), use_container_width=True)
    
    with tab4:
        st.plotly_chart(create_calendar_view(results), use_container_width=True)
    
    # Full results table
    with st.expander("📋 View All Results"):
        df_data = []
        for r in results:
            if r.success and r.cheapest_price:
                df_data.append({
                    'Departure': r.departure_date.strftime('%b %d'),
                    'Return': r.return_date.strftime('%b %d'),
                    'Duration': f"{r.total_duration} days",
                    'Days There': r.days_at_destination,
                    'Price': r.cheapest_price,
                    'Currency': r.currency
                })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=400)


def main():
    """Main application"""
    
    # Header
    st.title("✈️ CoolFlightPrices")
    st.markdown("*Find the best flight deals across flexible dates*")
    
    # Check credentials
    if not check_api_credentials():
        st.stop()
    
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
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input(
                "From",
                value="ZRH",
                max_chars=3,
                help="3-letter IATA airport code"
            ).upper()
        with col2:
            destination = st.text_input(
                "To",
                value="LIS",
                max_chars=3,
                help="3-letter IATA airport code"
            ).upper()
    
    # Mode-specific UI
    if search_mode == "💡 Flexible Dates (Date Range)":
        params = date_range_search_ui(st.sidebar)
        if params is None:
            st.stop()
        search_button = st.sidebar.button("🔍 Search Date Range", type="primary", use_container_width=True)
    else:
        departure_date, return_date, adults, max_results = single_date_search_ui(st.sidebar)
        search_button = st.sidebar.button("🔍 Search Flights", type="primary", use_container_width=True)
    
    # Main content area
    if search_button:
        # Validate inputs
        if not origin or len(origin) != 3:
            st.error("Please enter a valid 3-letter origin airport code")
            st.stop()
        
        if not destination or len(destination) != 3:
            st.error("Please enter a valid 3-letter destination airport code")
            st.stop()
        
        try:
            client = AmadeusClient()
            
            if search_mode == "💡 Flexible Dates (Date Range)":
                # Date range search
                st.subheader(f"📊 Flexible Date Search: {origin} → {destination}")
                
                # Generate date combinations
                if params['use_sampling']:
                    st.info("Using smart sampling to reduce API calls...")
                    combinations = smart_sample_dates(
                        params['dep_start'], params['dep_end'],
                        params['ret_start'], params['ret_end'],
                        target_combinations=25,
                        min_days_at_destination=params['min_days']
                    )
                else:
                    combinations = generate_date_combinations(
                        params['dep_start'], params['dep_end'],
                        params['ret_start'], params['ret_end'],
                        params['min_days']
                    )
                
                st.info(f"Searching {len(combinations)} date combinations...")
                
                # Batch search with progress
                batch_search = BatchFlightSearch(client)
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total, message):
                    progress_bar.progress(current / total)
                    status_text.text(f"{message} ({current}/{total})")
                
                results = batch_search.search_date_range(
                    origin=origin,
                    destination=destination,
                    date_combinations=combinations,
                    adults=params['adults'],
                    progress_callback=update_progress
                )
                
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                display_date_range_results(results, origin, destination)
                
            else:
                # Single date search
                st.subheader("Search Results")
                st.markdown(f"""
                **Route:** {origin} → {destination}  
                **Departure:** {departure_date}  
                {"**Return:** " + str(return_date) if return_date else "**Trip Type:** One-way"}  
                **Passengers:** {adults} adult(s)
                """)
                
                with st.spinner("🔄 Searching for flights..."):
                    flights = client.get_cheapest_flights(
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        return_date=return_date,
                        adults=adults,
                        max_results=max_results
                    )
                    
                    display_single_search_results(flights, origin, destination)
            
        except Exception as e:
            st.error(f"❌ Error searching for flights: {str(e)}")
            st.info("""
            **Troubleshooting:**
            - Check your API credentials
            - Verify airport codes are valid (3-letter IATA codes)
            - Check if you've exceeded your API quota
            - Try different dates or airports
            """)
    
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
