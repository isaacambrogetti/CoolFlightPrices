"""
Flight API Client Module

This module handles communication with flight data providers (Skyscanner, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import date


class FlightAPIClient(ABC):
    """Abstract base class for flight API clients"""
    
    @abstractmethod
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        **kwargs
    ) -> List[Dict]:
        """
        Search for flights
        
        Args:
            origin: Origin airport code (e.g., 'ZRH')
            destination: Destination airport code (e.g., 'LIS')
            departure_date: Date of departure
            return_date: Date of return (None for one-way)
            adults: Number of adult passengers
            **kwargs: Additional parameters specific to the API
            
        Returns:
            List of flight dictionaries with standardized format
        """
        pass
    
    @abstractmethod
    def get_flight_details(self, flight_id: str) -> Dict:
        """Get detailed information about a specific flight"""
        pass


class SkyscannerClient(FlightAPIClient):
    """
    Skyscanner API Client
    
    TODO: Implement actual API calls once we decide on the data source
    (RapidAPI, direct scraping, or alternative API)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # TODO: Initialize API client
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: Optional[date] = None,
        adults: int = 1,
        **kwargs
    ) -> List[Dict]:
        """
        Search for flights on Skyscanner
        
        Returns standardized flight data format:
        {
            'flight_id': str,
            'origin': str,
            'destination': str,
            'departure_date': date,
            'departure_time': str,
            'arrival_time': str,
            'airline': str,
            'price': float,
            'currency': str,
            'duration': int (minutes),
            'stops': int,
            'return_flight': dict (if roundtrip)
        }
        """
        # TODO: Implement API call
        raise NotImplementedError("API client not yet implemented")
    
    def get_flight_details(self, flight_id: str) -> Dict:
        """Get detailed information about a specific flight"""
        # TODO: Implement
        raise NotImplementedError("API client not yet implemented")


# Placeholder for other potential clients
class KiwiClient(FlightAPIClient):
    """Kiwi.com API Client (alternative to Skyscanner)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def search_flights(self, *args, **kwargs) -> List[Dict]:
        raise NotImplementedError("Kiwi client not yet implemented")
    
    def get_flight_details(self, flight_id: str) -> Dict:
        raise NotImplementedError("Kiwi client not yet implemented")
