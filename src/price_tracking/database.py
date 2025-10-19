"""
Price Tracking Database Module

Manages flight tracking data with price history and visualization support.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class PriceTrackingDB:
    """Database for tracking flight prices over time"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the price tracking database
        
        Args:
            db_path: Path to JSON database file
        """
        if db_path is None:
            db_path = Path(__file__).parent / 'tracked_flights.json'
        
        self.db_path = str(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"tracked_flights": {}}, f, indent=2)
    
    def _load_db(self) -> Dict:
        """Load database from file"""
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def _save_db(self, data: Dict):
        """Save database to file"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_flight_id(self, flight: Dict) -> str:
        """
        Generate unique ID for a flight
        
        Format: ORIGIN_DEST_DEPDATE_RETDATE_AIRLINE_FLIGHTNUM
        Example: ZRH_LIS_20251215_20251222_TP_1234
        
        Args:
            flight: Flight dictionary with outbound (and optionally return) info
            
        Returns:
            Unique flight identifier string
        """
        outbound = flight['outbound']
        origin = outbound.get('origin', 'UNK')
        destination = outbound.get('destination', 'UNK')
        dep_date = outbound.get('departure_date', '')
        
        # Handle return flights
        if flight.get('return'):
            ret_date = flight['return'].get('departure_date', 'OW')
        else:
            ret_date = 'OW'
        
        airline = outbound.get('airline', 'UNK')
        flight_num = outbound.get('flight_number', '0000')
        
        # Clean dates (remove hyphens) - convert to string first if needed
        if dep_date:
            dep_date_str = str(dep_date)  # Convert date object to string
            dep_date_clean = dep_date_str.replace('-', '')
        else:
            dep_date_clean = '00000000'
            
        if ret_date != 'OW':
            ret_date_str = str(ret_date)  # Convert date object to string
            ret_date_clean = ret_date_str.replace('-', '')
        else:
            ret_date_clean = 'OW'
        
        return f"{origin}_{destination}_{dep_date_clean}_{ret_date_clean}_{airline}_{flight_num}"
    
    def add_tracked_flight(self, flight: Dict, current_price: float, currency: str) -> str:
        """
        Add a new flight to tracking
        
        Args:
            flight: Flight dictionary from search results
            current_price: Current price of the flight
            currency: Price currency (e.g., 'EUR', 'USD')
            
        Returns:
            Flight ID of the tracked flight
        """
        db = self._load_db()
        flight_id = self.generate_flight_id(flight)
        
        # Extract flight details
        outbound = flight['outbound']
        return_flight = flight.get('return')
        
        flight_data = {
            'origin': outbound.get('origin'),
            'destination': outbound.get('destination'),
            'departure_date': outbound.get('departure_date'),
            'return_date': return_flight.get('departure_date') if return_flight else None,
            'airline': outbound.get('airline'),
            'flight_number': outbound.get('flight_number'),
            'return_airline': return_flight.get('airline') if return_flight else None,
            'return_flight_number': return_flight.get('flight_number') if return_flight else None,
            'is_roundtrip': flight.get('return') is not None,
            'initial_price': current_price,
            'latest_price': current_price,
            'currency': currency,
            'added_date': datetime.now().isoformat(),
            'price_history': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'price': current_price
                }
            ]
        }
        
        db['tracked_flights'][flight_id] = flight_data
        self._save_db(db)
        
        return flight_id
    
    def add_price_point(self, flight_id: str, price: float, timestamp: Optional[str] = None):
        """
        Add a new price observation for a tracked flight
        
        Args:
            flight_id: Unique flight identifier
            price: Observed price
            timestamp: ISO format timestamp (defaults to now)
        """
        db = self._load_db()
        
        if flight_id not in db['tracked_flights']:
            raise ValueError(f"Flight {flight_id} is not being tracked")
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        flight = db['tracked_flights'][flight_id]
        flight['price_history'].append({
            'timestamp': timestamp,
            'price': price
        })
        flight['latest_price'] = price
        
        self._save_db(db)
    
    def get_tracked_flights(self) -> Dict[str, Dict]:
        """
        Get all tracked flights
        
        Returns:
            Dictionary of flight_id -> flight_data
        """
        db = self._load_db()
        return db['tracked_flights']
    
    def get_flight(self, flight_id: str) -> Optional[Dict]:
        """
        Get a specific tracked flight
        
        Args:
            flight_id: Unique flight identifier
            
        Returns:
            Flight data dictionary or None if not found
        """
        db = self._load_db()
        return db['tracked_flights'].get(flight_id)
    
    def get_price_history(self, flight_id: str) -> List[Dict]:
        """
        Get price history for a specific flight
        
        Args:
            flight_id: Unique flight identifier
            
        Returns:
            List of price observations with timestamp and price
        """
        flight = self.get_flight(flight_id)
        if flight is None:
            return []
        return flight.get('price_history', [])
    
    def remove_tracked_flight(self, flight_id: str):
        """
        Stop tracking a flight
        
        Args:
            flight_id: Unique flight identifier
        """
        db = self._load_db()
        
        if flight_id in db['tracked_flights']:
            del db['tracked_flights'][flight_id]
            self._save_db(db)
    
    def is_tracked(self, flight: Dict) -> bool:
        """
        Check if a flight is already being tracked
        
        Args:
            flight: Flight dictionary
            
        Returns:
            True if flight is tracked, False otherwise
        """
        flight_id = self.generate_flight_id(flight)
        db = self._load_db()
        return flight_id in db['tracked_flights']
    
    def clear_all(self):
        """Remove all tracked flights"""
        self._save_db({"tracked_flights": {}})
    
    def get_stats(self) -> Dict:
        """
        Get statistics about tracked flights
        
        Returns:
            Dictionary with count, average_price_change, etc.
        """
        tracked = self.get_tracked_flights()
        
        if not tracked:
            return {
                'total_tracked': 0,
                'with_price_drops': 0,
                'with_price_increases': 0,
                'average_price_change_pct': 0
            }
        
        price_drops = 0
        price_increases = 0
        total_change_pct = 0
        
        for flight_data in tracked.values():
            initial = flight_data['initial_price']
            latest = flight_data['latest_price']
            
            if latest < initial:
                price_drops += 1
            elif latest > initial:
                price_increases += 1
            
            if initial > 0:
                change_pct = ((latest - initial) / initial) * 100
                total_change_pct += change_pct
        
        avg_change = total_change_pct / len(tracked) if tracked else 0
        
        return {
            'total_tracked': len(tracked),
            'with_price_drops': price_drops,
            'with_price_increases': price_increases,
            'average_price_change_pct': avg_change
        }
