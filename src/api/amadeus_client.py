"""
Amadeus API Client Implementation

Official Amadeus Python SDK documentation:
https://github.com/amadeus4dev/amadeus-python
"""

from typing import List, Dict, Optional
from datetime import date, datetime, time as dt_time
from amadeus import Client, ResponseError
from config.settings import Config
from src.models.flight import Flight, RoundtripFlight


class AmadeusClient:
    """
    Amadeus API Client for flight searches
    
    Amadeus offers:
    - Flight offers search
    - Flight price analysis
    - Airport and airline info
    - Free tier: 2000 API calls/month
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Amadeus client
        
        Args:
            api_key: Amadeus API key (or use from config)
            api_secret: Amadeus API secret (or use from config)
        """
        self.api_key = api_key or Config.AMADEUS_API_KEY
        self.api_secret = api_secret or Config.AMADEUS_API_SECRET
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Amadeus API credentials not found. "
                "Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env file"
            )
        
        self.client = Client(
            client_id=self.api_key,
            client_secret=self.api_secret
        )
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        max_results: int = 10,
        currency: str = "EUR",
        **kwargs
    ) -> List[Dict]:
        """
        Search for flights using Amadeus API
        
        Args:
            origin: IATA airport code (e.g., 'ZRH')
            destination: IATA airport code (e.g., 'LIS')
            departure_date: Date of departure
            return_date: Date of return (None for one-way)
            adults: Number of adult passengers
            max_results: Maximum number of results to return
            currency: Currency code (default: EUR)
            **kwargs: Additional Amadeus API parameters
            
        Returns:
            List of flight offer dictionaries
        """
        try:
            # Prepare search parameters
            search_params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date.isoformat(),
                'adults': adults,
                'currencyCode': currency,
                'max': max_results,
            }
            
            # Add return date if roundtrip
            if return_date:
                search_params['returnDate'] = return_date.isoformat()
            
            # Add any additional parameters
            search_params.update(kwargs)
            
            # Make API call
            response = self.client.shopping.flight_offers_search.get(**search_params)
            
            # Return raw data (we'll process it later)
            return response.data
            
        except ResponseError as error:
            print(f"Amadeus API Error: {error}")
            raise
    
    def parse_flight_offer(self, offer: Dict) -> Dict:
        """
        Parse an Amadeus flight offer into our standard format
        
        Args:
            offer: Raw offer from Amadeus API
            
        Returns:
            Parsed flight data in standard format
        """
        try:
            # Extract basic info
            price = float(offer['price']['total'])
            currency = offer['price']['currency']
            
            # Extract itineraries (outbound and return)
            itineraries = offer['itineraries']
            
            # Parse segments
            parsed_flights = []
            for itinerary in itineraries:
                segments = itinerary['segments']
                
                # For simplicity, take first and last segment for timing
                first_segment = segments[0]
                last_segment = segments[-1]
                
                # Parse departure
                departure_datetime = datetime.fromisoformat(
                    first_segment['departure']['at'].replace('Z', '+00:00')
                )
                
                # Parse arrival
                arrival_datetime = datetime.fromisoformat(
                    last_segment['arrival']['at'].replace('Z', '+00:00')
                )
                
                # Calculate duration
                duration_str = itinerary['duration']  # Format: PT12H30M
                
                flight_data = {
                    'origin': first_segment['departure']['iataCode'],
                    'destination': last_segment['arrival']['iataCode'],
                    'departure_date': departure_datetime.date(),
                    'departure_time': departure_datetime.time(),
                    'arrival_date': arrival_datetime.date(),
                    'arrival_time': arrival_datetime.time(),
                    'airline': first_segment['carrierCode'],
                    'flight_number': first_segment['number'],
                    'stops': len(segments) - 1,
                    'duration': duration_str,
                }
                
                parsed_flights.append(flight_data)
            
            return {
                'offer_id': offer['id'],
                'price': price,
                'currency': currency,
                'outbound': parsed_flights[0],
                'return': parsed_flights[1] if len(parsed_flights) > 1 else None,
                'number_of_bookable_seats': offer.get('numberOfBookableSeats', 'N/A'),
                'raw_offer': offer  # Keep raw data for reference
            }
            
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing flight offer: {e}")
            return None
    
    def get_cheapest_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Get cheapest flight options, sorted by price
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date (optional)
            
        Returns:
            List of parsed flight offers, sorted by price
        """
        offers = self.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            **kwargs
        )
        
        # Parse all offers
        parsed_offers = []
        for offer in offers:
            parsed = self.parse_flight_offer(offer)
            if parsed:
                parsed_offers.append(parsed)
        
        # Sort by price
        parsed_offers.sort(key=lambda x: x['price'])
        
        return parsed_offers
