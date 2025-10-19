"""
Flight Price Tracking Module

- Save and update tracked flight prices over time
- Query price history for plotting and analysis
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

TRACKED_PRICES_FILE = os.path.join(os.path.dirname(__file__), 'tracked_prices.json')

class PriceTracker:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or TRACKED_PRICES_FILE
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def add_price_entry(self, flight_info: Dict, price: float, currency: str, timestamp: Optional[datetime] = None):
        """Add a new price entry for a flight (by route, date, airline, etc.)"""
        entry = {
            'flight_info': flight_info,  # e.g. origin, destination, date, airline, flight_number, is_roundtrip
            'price': price,
            'currency': currency,
            'timestamp': (timestamp or datetime.utcnow()).isoformat()
        }
        data = self.load_all()
        data.append(entry)
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_all(self) -> List[Dict]:
        with open(self.storage_path, 'r') as f:
            return json.load(f)

    def get_history(self, filter_fn=None) -> List[Dict]:
        """Return all tracked price entries, optionally filtered by a function."""
        data = self.load_all()
        if filter_fn:
            data = [d for d in data if filter_fn(d)]
        return data

    def clear(self):
        with open(self.storage_path, 'w') as f:
            json.dump([], f)
