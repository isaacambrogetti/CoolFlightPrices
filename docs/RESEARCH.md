# Research Notes: Skyscanner API Options

## Date: October 15, 2025

### Option 1: RapidAPI Skyscanner
- **URL**: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
- **Status**: Need to check current availability and pricing
- **Pros**: Official, reliable, well-documented
- **Cons**: May have subscription costs

### Option 2: Kiwi.com Tequila API
- **URL**: https://tequila.kiwi.com/
- **Status**: Alternative with good documentation
- **Free Tier**: Available for testing
- **Pros**: Free tier available, good support
- **Cons**: Different from Skyscanner data

### Option 3: Amadeus for Developers
- **URL**: https://developers.amadeus.com/
- **Free Tier**: 2000 API calls/month
- **Pros**: Industry standard, free tier
- **Cons**: Learning curve

### Option 4: Aviationstack
- **URL**: https://aviationstack.com/
- **Status**: Real-time flight data
- **Limited**: May not have price predictions

## Recommended Approach

### Phase 1: Start with RapidAPI Research
1. Check current RapidAPI Skyscanner availability
2. Review pricing tiers
3. Test with free tier if available

### Phase 2: Fallback to Kiwi.com
- If Skyscanner is too expensive or unavailable
- Kiwi has a generous free tier
- Good for prototyping

### Phase 3: Web Scraping (Last Resort)
- Only if APIs don't work
- Legal and ethical concerns
- Maintenance burden

## Next Actions

- [ ] Sign up for RapidAPI account
- [ ] Test Skyscanner API availability
- [ ] Test Kiwi.com API
- [ ] Compare response formats
- [ ] Choose best option for this project
- [ ] Implement proof of concept

## API Response Format to Design Around

Based on typical flight APIs, we need to handle:
- Multiple carriers/airlines
- Layovers and connections
- Price variations by date
- Booking links
- Real-time vs cached data

## UI Framework Decision

Recommend **Streamlit** for initial development:
- Fastest to prototype
- Python-only (no HTML/CSS/JS needed)
- Built-in date pickers and selection widgets
- Easy to show dataframes and plots
- Can migrate to Flask later if needed

Would look something like:
```python
import streamlit as st

st.title("Flight Price Tracker")

col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("From", "ZRH")
with col2:
    destination = st.text_input("To", "LIS")

departure = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

if st.button("Search Flights"):
    # Search and display results
    pass
```
