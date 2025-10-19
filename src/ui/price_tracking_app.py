"""
Streamlit UI for Flight Price Tracking

- Show tracked price history
- Filter by roundtrip, direct, country, month, etc.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from datetime import datetime
from src.price_tracking.tracker import PriceTracker

st.set_page_config(page_title="Flight Price Tracking", page_icon="📈", layout="wide")

st.title("Flight Price Tracking 📈")
tracker = PriceTracker()

# Load all tracked prices
data = tracker.load_all()
df = pd.DataFrame(data)

if df.empty:
    st.info("No price history yet. Start tracking flights to see price development!")
    st.stop()

# Flatten flight_info for filtering
flight_df = pd.json_normalize(df['flight_info'])
df = pd.concat([df, flight_df], axis=1)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['month'] = df['timestamp'].dt.to_period('M')

# Sidebar filters
st.sidebar.header("Filters")
roundtrip = st.sidebar.selectbox("Trip Type", options=["All", "Roundtrip", "One-way"])
direct = st.sidebar.selectbox("Direct Flight", options=["All", "Direct", "With Stops"])
country = st.sidebar.text_input("Destination Country (optional)")
month = st.sidebar.text_input("Month (YYYY-MM, optional)")

filtered = df.copy()
if roundtrip != "All":
    filtered = filtered[filtered['flight_info.is_roundtrip'] == (roundtrip == "Roundtrip")]
if direct != "All":
    filtered = filtered[filtered['flight_info.stops'] == (0 if direct == "Direct" else filtered['flight_info.stops'] > 0)]
if country:
    filtered = filtered[filtered['flight_info.destination_country'].str.contains(country, case=False, na=False)]
if month:
    filtered = filtered[filtered['month'] == month]

if filtered.empty:
    st.warning("No tracked flights match your filters.")
    st.stop()

# Plot price development for all filtered flights
st.subheader("Price Development of Tracked Flights")
for key, group in filtered.groupby(['flight_info.origin', 'flight_info.destination', 'flight_info.departure_date']):
    label = f"{key[0]} → {key[1]} on {key[2]}"
    st.line_chart(group.set_index('timestamp')['price'], height=200, use_container_width=True)
    st.caption(label)
