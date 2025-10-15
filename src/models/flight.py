"""
Flight data models
"""

from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional, List
from enum import Enum


class FlightClass(Enum):
    """Flight class enumeration"""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


@dataclass
class Flight:
    """Represents a single flight segment"""
    
    flight_id: str
    origin: str
    destination: str
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    airline: str
    flight_number: str
    price: float
    currency: str = "EUR"
    duration_minutes: int = 0
    stops: int = 0
    flight_class: FlightClass = FlightClass.ECONOMY
    
    def __str__(self):
        return (f"{self.airline} {self.flight_number}: "
                f"{self.origin}->{self.destination} "
                f"{self.departure_date} {self.departure_time} "
                f"{self.currency} {self.price}")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'flight_id': self.flight_id,
            'origin': self.origin,
            'destination': self.destination,
            'departure_date': self.departure_date.isoformat(),
            'departure_time': self.departure_time.isoformat(),
            'arrival_date': self.arrival_date.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'airline': self.airline,
            'flight_number': self.flight_number,
            'price': self.price,
            'currency': self.currency,
            'duration_minutes': self.duration_minutes,
            'stops': self.stops,
            'flight_class': self.flight_class.value
        }


@dataclass
class RoundtripFlight:
    """Represents a roundtrip flight with outbound and return segments"""
    
    outbound: Flight
    return_flight: Flight
    total_price: float
    currency: str = "EUR"
    
    def __str__(self):
        return (f"Roundtrip: {self.outbound.origin}->{self.outbound.destination} "
                f"({self.outbound.departure_date}) - "
                f"{self.return_flight.origin}->{self.return_flight.destination} "
                f"({self.return_flight.departure_date}) "
                f"{self.currency} {self.total_price}")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'outbound': self.outbound.to_dict(),
            'return': self.return_flight.to_dict(),
            'total_price': self.total_price,
            'currency': self.currency
        }


@dataclass
class TrackedFlight:
    """
    Represents a flight being tracked for price changes
    """
    
    tracking_id: str
    flight: Flight  # or RoundtripFlight
    initial_price: float
    current_price: float
    lowest_price: float
    highest_price: float
    tracked_since: date
    last_checked: date
    alert_threshold: Optional[float] = None  # Alert if price drops below this
    price_history: List[tuple] = field(default_factory=list)  # [(date, price), ...]
    
    def update_price(self, new_price: float, check_date: date):
        """Update with new price information"""
        self.current_price = new_price
        self.last_checked = check_date
        self.lowest_price = min(self.lowest_price, new_price)
        self.highest_price = max(self.highest_price, new_price)
        self.price_history.append((check_date, new_price))
    
    def price_dropped(self) -> bool:
        """Check if price has dropped since initial"""
        return self.current_price < self.initial_price
    
    def should_alert(self) -> bool:
        """Check if we should send an alert based on threshold"""
        if self.alert_threshold is None:
            return False
        return self.current_price <= self.alert_threshold
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'tracking_id': self.tracking_id,
            'flight': self.flight.to_dict(),
            'initial_price': self.initial_price,
            'current_price': self.current_price,
            'lowest_price': self.lowest_price,
            'highest_price': self.highest_price,
            'tracked_since': self.tracked_since.isoformat(),
            'last_checked': self.last_checked.isoformat(),
            'alert_threshold': self.alert_threshold,
            'price_history': [(d.isoformat(), p) for d, p in self.price_history]
        }
