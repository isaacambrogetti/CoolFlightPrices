"""
CoolFlightPrices - Streamlit UI

A simple web interface for searching and tracking flight prices.
"""

import streamlit as st
from datetime import date, timedelta
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.api.amadeus_client import AmadeusClient
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


def main():
    """Main application"""
    
    # Header
    st.title("✈️ CoolFlightPrices")
    st.markdown("*Track flight prices and find the best deals*")
    
    # Check credentials
    if not check_api_credentials():
        st.stop()
    
    # Sidebar for search parameters
    st.sidebar.header("🔍 Search Flights")
    
    with st.sidebar:
        # Origin and destination
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input(
                "From",
                value="ZRH",
                max_chars=3,
                help="3-letter IATA airport code (e.g., ZRH for Zurich)"
            ).upper()
        
        with col2:
            destination = st.text_input(
                "To",
                value="LIS",
                max_chars=3,
                help="3-letter IATA airport code (e.g., LIS for Lisbon)"
            ).upper()
        
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
        
        # Search button
        search_button = st.button("🔍 Search Flights", type="primary", use_container_width=True)
    
    # Main content area
    if search_button:
        # Validate inputs
        if not origin or len(origin) != 3:
            st.error("Please enter a valid 3-letter origin airport code")
            st.stop()
        
        if not destination or len(destination) != 3:
            st.error("Please enter a valid 3-letter destination airport code")
            st.stop()
        
        # Search for flights
        with st.spinner("🔄 Searching for flights..."):
            try:
                client = AmadeusClient()
                
                # Display search parameters
                st.subheader("Search Results")
                st.markdown(f"""
                **Route:** {origin} → {destination}  
                **Departure:** {departure_date}  
                {"**Return:** " + str(return_date) if return_date else "**Trip Type:** One-way"}  
                **Passengers:** {adults} adult(s)
                """)
                
                # Get flights
                flights = client.get_cheapest_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    return_date=return_date,
                    adults=adults,
                    max_results=max_results
                )
                
                if not flights:
                    st.warning("No flights found for your search criteria. Try different dates or airports.")
                    st.stop()
                
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
                        
                        # Track button (placeholder for now)
                        if st.button(f"📌 Track this flight", key=f"track_{i}"):
                            st.info("Tracking feature coming soon! 🚧")
                
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
        
        **Features:**
        - Search flights using Amadeus API
        - Compare prices across different options
        - Track flights (coming soon)
        - Price history visualization (coming soon)
        
        **Popular Airport Codes:**
        - ZRH: Zurich, Switzerland
        - LIS: Lisbon, Portugal
        - JFK: New York, USA
        - LHR: London, UK
        - CDG: Paris, France
        - FCO: Rome, Italy
        - BCN: Barcelona, Spain
        - AMS: Amsterdam, Netherlands
        """)
        
        # Display API status
        try:
            client = AmadeusClient()
            st.success("✅ Amadeus API connected")
        except:
            st.error("❌ Amadeus API not connected - check your credentials")


if __name__ == "__main__":
    main()
