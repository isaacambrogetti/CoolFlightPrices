"""
Test script to check if Amadeus Multi-City API access is available

This tests the POST endpoint for flight-offers-search with multiple segments (originDestinations).
If this works, we can use native multi-city/open-jaw search instead of combining one-way flights.
"""

from amadeus import Client, ResponseError
from config.settings import Config
from datetime import date, timedelta
import json


def test_multi_city_access():
    """Test if multi-city API endpoint is accessible"""
    
    print("🔍 Testing Amadeus Multi-City API Access...")
    print("=" * 60)
    
    # Initialize client
    try:
        client = Client(
            client_id=Config.AMADEUS_API_KEY,
            client_secret=Config.AMADEUS_API_SECRET
        )
        print("✅ Amadeus client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Test dates
    today = date.today()
    departure_date = today + timedelta(days=30)
    return_date = today + timedelta(days=37)
    
    print(f"\n📅 Test Parameters:")
    print(f"   Outbound: ZRH → LIS on {departure_date}")
    print(f"   Return:   OPO → ZRH on {return_date}")
    print()
    
    # Multi-city request body (POST)
    # This is the format for open-jaw flights
    request_body = {
        "currencyCode": "EUR",
        "originDestinations": [
            {
                "id": "1",
                "originLocationCode": "ZRH",
                "destinationLocationCode": "LIS",
                "departureDateTimeRange": {
                    "date": departure_date.isoformat()
                }
            },
            {
                "id": "2",
                "originLocationCode": "OPO",
                "destinationLocationCode": "ZRH",
                "departureDateTimeRange": {
                    "date": return_date.isoformat()
                }
            }
        ],
        "travelers": [
            {
                "id": "1",
                "travelerType": "ADULT"
            }
        ],
        "sources": [
            "GDS"
        ],
        "searchCriteria": {
            "maxFlightOffers": 5
        }
    }
    
    print("📡 Attempting POST request to flight-offers-search...")
    print(f"   Request body: {json.dumps(request_body, indent=2)}")
    print()
    
    try:
        # Attempt POST request for multi-city search
        response = client.shopping.flight_offers_search.post(request_body)
        
        print("✅ SUCCESS! Multi-City API is accessible!")
        print("=" * 60)
        print(f"\n📊 Results:")
        print(f"   Found {len(response.data)} flight offers")
        
        if response.data:
            first_offer = response.data[0]
            print(f"\n💰 Sample offer:")
            print(f"   Price: {first_offer['price']['total']} {first_offer['price']['currency']}")
            print(f"   Itineraries: {len(first_offer['itineraries'])}")
            
            for idx, itinerary in enumerate(first_offer['itineraries'], 1):
                segments = itinerary['segments']
                first_seg = segments[0]
                last_seg = segments[-1]
                print(f"\n   Itinerary {idx}:")
                print(f"      {first_seg['departure']['iataCode']} → {last_seg['arrival']['iataCode']}")
                print(f"      Departure: {first_seg['departure']['at']}")
                print(f"      Stops: {len(segments) - 1}")
        
        print("\n" + "=" * 60)
        print("🎉 RECOMMENDATION: Use Option 2 (Native Multi-City API)")
        print("   This is more efficient and provides native pricing!")
        print("=" * 60)
        
        return True
        
    except ResponseError as error:
        print(f"❌ API Error: {error}")
        print(f"   Code: {error.code if hasattr(error, 'code') else 'N/A'}")
        print(f"   Description: {error.description if hasattr(error, 'description') else 'N/A'}")
        print("\n" + "=" * 60)
        print("⚠️  RECOMMENDATION: Use Option 1 (Combine One-Way Flights)")
        print("   Multi-city endpoint not available with current API tier")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Type: {type(e).__name__}")
        print("\n" + "=" * 60)
        print("⚠️  RECOMMENDATION: Use Option 1 (Combine One-Way Flights)")
        print("   Multi-city endpoint encountered unexpected error")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_multi_city_access()
    exit(0 if success else 1)
