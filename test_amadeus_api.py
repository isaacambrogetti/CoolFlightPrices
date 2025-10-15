"""
Test script for Amadeus API

This script tests the Amadeus API connection and searches for flights.

Before running:
1. Sign up at https://developers.amadeus.com/
2. Create an app to get your API key and secret
3. Copy .env.example to .env
4. Add your credentials to .env
5. Run: python test_amadeus_api.py
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.amadeus_client import AmadeusClient
from config.settings import Config


def test_amadeus_connection():
    """Test basic Amadeus API connection"""
    print("=" * 60)
    print("Testing Amadeus API Connection")
    print("=" * 60)
    
    # Check if credentials are set
    if not Config.AMADEUS_API_KEY or not Config.AMADEUS_API_SECRET:
        print("\n❌ ERROR: Amadeus credentials not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://developers.amadeus.com/")
        print("2. Sign up for a free account")
        print("3. Create a new app (Self-Service)")
        print("4. Copy your API Key and API Secret")
        print("5. Copy .env.example to .env")
        print("6. Add your credentials to .env:")
        print("   AMADEUS_API_KEY=your_key_here")
        print("   AMADEUS_API_SECRET=your_secret_here")
        return False
    
    try:
        client = AmadeusClient()
        print("\n✅ Amadeus client initialized successfully!")
        print(f"API Key: {Config.AMADEUS_API_KEY[:10]}...")
        return True
    except Exception as e:
        print(f"\n❌ Error initializing client: {e}")
        return False


def test_flight_search():
    """Test flight search functionality"""
    print("\n" + "=" * 60)
    print("Testing Flight Search")
    print("=" * 60)
    
    try:
        client = AmadeusClient()
        
        # Search parameters (ZRH to LIS, similar to your original project)
        origin = "ZRH"  # Zurich
        destination = "LIS"  # Lisbon
        departure_date = date.today() + timedelta(days=30)  # 30 days from now
        return_date = departure_date + timedelta(days=4)  # 4-day trip
        
        print(f"\nSearching flights:")
        print(f"  Route: {origin} → {destination}")
        print(f"  Departure: {departure_date}")
        print(f"  Return: {return_date}")
        print(f"  Passengers: 1 adult")
        print("\nFetching data from Amadeus...")
        
        # Search for flights
        offers = client.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=1,
            max_results=5
        )
        
        print(f"\n✅ Found {len(offers)} flight offers!")
        
        # Parse and display results
        print("\n" + "-" * 60)
        print("Flight Options (sorted by price):")
        print("-" * 60)
        
        cheapest_flights = client.get_cheapest_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            max_results=5
        )
        
        for i, flight in enumerate(cheapest_flights, 1):
            print(f"\n{i}. Price: {flight['currency']} {flight['price']}")
            print(f"   Offer ID: {flight['offer_id']}")
            
            # Outbound flight
            outbound = flight['outbound']
            print(f"   Outbound: {outbound['origin']} → {outbound['destination']}")
            print(f"            {outbound['departure_date']} {outbound['departure_time']}")
            print(f"            Airline: {outbound['airline']} {outbound['flight_number']}")
            print(f"            Stops: {outbound['stops']}")
            print(f"            Duration: {outbound['duration']}")
            
            # Return flight
            if flight['return']:
                return_flight = flight['return']
                print(f"   Return:   {return_flight['origin']} → {return_flight['destination']}")
                print(f"            {return_flight['departure_date']} {return_flight['departure_time']}")
                print(f"            Airline: {return_flight['airline']} {return_flight['flight_number']}")
                print(f"            Stops: {return_flight['stops']}")
                print(f"            Duration: {return_flight['duration']}")
            
            print(f"   Seats available: {flight['number_of_bookable_seats']}")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during flight search: {e}")
        print("\nTroubleshooting:")
        print("- Check your API credentials in .env")
        print("- Verify you're using valid airport codes (IATA)")
        print("- Check if you've exceeded your API quota")
        print("- Make sure your Amadeus account is active")
        return False


def main():
    """Run all tests"""
    print("\n🛫 CoolFlightPrices - Amadeus API Test\n")
    
    # Test 1: Connection
    if not test_amadeus_connection():
        sys.exit(1)
    
    # Test 2: Flight search
    if not test_flight_search():
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("\nNext steps:")
    print("1. Check TODO.md for implementation roadmap")
    print("2. Run the Streamlit UI: streamlit run src/ui/app.py")
    print("3. Start building features incrementally")


if __name__ == "__main__":
    main()
