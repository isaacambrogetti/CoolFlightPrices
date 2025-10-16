# Price Tracking Tool

This module allows you to track the price of flights over time and visualize their development.

## Features
- Track prices for any searched flight (by route, date, airline, etc.)
- View a plot of price development for all tracked flights
- Filter plots by roundtrip/one-way, direct/with stops, destination country, or month
- Compare prices for flights in the same month, to different destinations, or for roundtrips only

## Usage
- Use the main app to add flights to the tracker (integration coming soon)
- Open `src/ui/price_tracking_app.py` in Streamlit to view and analyze tracked prices:

```bash
streamlit run src/ui/price_tracking_app.py
```

## Data Storage
- Tracked prices are stored in `src/price_tracking/tracked_prices.json`
- You can clear all tracked data using the `clear()` method in `PriceTracker`

---

Development started on branch `price-tracking-tool`.
