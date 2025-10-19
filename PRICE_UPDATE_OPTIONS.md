# Price Update Implementation Options

This document describes different approaches for automatically updating tracked flight prices over time.

## Overview

The app currently tracks flights and stores their initial price. To build price history over time, we need to periodically fetch updated prices. Here are three implementation options:

---

## Option 1: Manual "Refresh All Prices" Button ⭐ SIMPLEST

### Description
Add a button in the Price Tracker page that allows users to manually refresh all tracked flight prices.

### How It Works
1. User opens the Price Tracker page
2. Clicks "🔄 Refresh All Prices" button
3. App makes API calls to fetch current prices for all tracked flights
4. New prices are added to the price history
5. Graphs update to show new data points

### Pros
- ✅ Full user control over when API calls are made
- ✅ No background infrastructure required
- ✅ No server needs to be running 24/7
- ✅ Simple to implement
- ✅ Minimal API usage - only when user clicks
- ✅ Easy to understand and debug

### Cons
- ❌ Requires manual action - user must remember to check
- ❌ Irregular data points if user forgets to check
- ❌ Gaps in price history during vacations/busy periods

### API Usage
- **Per refresh**: 1 API call × number of tracked flights
- **Example**: 10 tracked flights = 10 API calls per manual refresh
- **Monthly estimate**: Depends on user behavior (could be 0-300 calls)

### Implementation Steps

1. **Add refresh method to `PriceTrackingDB`**:
```python
def refresh_flight_price(self, flight_id: str, client: AmadeusClient) -> dict:
    """
    Fetch current price for a tracked flight and update history
    
    Returns:
        dict with 'success', 'new_price', 'old_price', 'message'
    """
    # Get tracked flight details
    flight_data = self.get_flight(flight_id)
    if not flight_data:
        return {'success': False, 'message': 'Flight not found'}
    
    # Search for current price using Amadeus API
    try:
        results = client.get_cheapest_flights(
            origin=flight_data['origin'],
            destination=flight_data['destination'],
            departure_date=flight_data['departure_date'],
            return_date=flight_data.get('return_date'),
            adults=1,
            max_results=1
        )
        
        if results:
            new_price = results[0]['price']
            old_price = flight_data['latest_price']
            
            # Add new price point
            self.add_price_point(flight_id, new_price)
            
            return {
                'success': True,
                'new_price': new_price,
                'old_price': old_price,
                'message': f'Price updated: {old_price} → {new_price}'
            }
        else:
            return {'success': False, 'message': 'No flights found'}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}
```

2. **Add "Refresh All" button in `tracker_ui.py`**:
```python
def display_tracker_tab():
    # ... existing code ...
    
    # Add refresh button at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("🔄 Refresh All Prices", use_container_width=True, type="primary"):
            with st.spinner("Fetching current prices..."):
                client = AmadeusClient()
                db = PriceTrackingDB()
                tracked = db.get_tracked_flights()
                
                results = []
                for flight_id in tracked.keys():
                    result = db.refresh_flight_price(flight_id, client)
                    results.append(result)
                
                # Show summary
                success_count = sum(1 for r in results if r['success'])
                st.success(f"✅ Updated {success_count}/{len(results)} flights")
                st.rerun()
```

### Best For
- Users who want full control
- Low-frequency checking (weekly/monthly)
- Testing and development phase
- Users with limited API quota

---

## Option 2: Automatic Background Server ⭐ FULLY AUTOMATED

### Description
Set up a separate scheduled process (cron job or background script) that runs independently of the Streamlit app to automatically update prices.

### How It Works
1. Background Python script runs on a schedule (e.g., daily at 6 AM)
2. Script reads the tracked flights database
3. Makes API calls to fetch current prices
4. Updates the database with new price points
5. Next time user opens the app, they see updated prices

### Pros
- ✅ Fully automated - no user action required
- ✅ Consistent data collection (same time every day)
- ✅ Complete price history over time
- ✅ Works even when user doesn't visit the app
- ✅ Can run at optimal times (e.g., early morning)

### Cons
- ❌ Requires always-on infrastructure
- ❌ More complex setup and maintenance
- ❌ Uses API calls even if user isn't actively using the app
- ❌ Needs error handling and logging
- ❌ Potential costs for cloud hosting

### API Usage
- **Per day**: 1 API call × number of tracked flights
- **Example**: 10 tracked flights = 10 API calls/day = 300 calls/month
- **Monthly estimate**: Tracked flights × 30 (consistent and predictable)

### Implementation Steps

#### A. Create Background Script

Create `scripts/update_prices.py`:
```python
#!/usr/bin/env python3
"""
Background script to automatically update tracked flight prices
Run this as a scheduled task (cron job) once or twice per day
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.price_tracking.database import PriceTrackingDB
from src.api.amadeus_client import AmadeusClient

def update_all_prices():
    """Update prices for all tracked flights"""
    print(f"\n{'='*60}")
    print(f"Price Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    db = PriceTrackingDB()
    client = AmadeusClient()
    
    tracked_flights = db.get_tracked_flights()
    total = len(tracked_flights)
    
    if total == 0:
        print("No tracked flights to update.")
        return
    
    print(f"Updating prices for {total} tracked flights...\n")
    
    success_count = 0
    error_count = 0
    
    for idx, (flight_id, flight_data) in enumerate(tracked_flights.items(), 1):
        route = f"{flight_data['origin']} → {flight_data['destination']}"
        print(f"[{idx}/{total}] {route} (Dep: {flight_data['departure_date']})")
        
        try:
            # Search for current price
            results = client.get_cheapest_flights(
                origin=flight_data['origin'],
                destination=flight_data['destination'],
                departure_date=flight_data['departure_date'],
                return_date=flight_data.get('return_date'),
                adults=1,
                max_results=1
            )
            
            if results:
                new_price = results[0]['price']
                old_price = flight_data['latest_price']
                
                # Add price point
                db.add_price_point(flight_id, new_price)
                
                change = new_price - old_price
                change_str = f"{'+' if change > 0 else ''}{change:.2f}"
                print(f"  ✅ Price: {old_price:.2f} → {new_price:.2f} ({change_str})")
                success_count += 1
            else:
                print(f"  ⚠️  No flights found")
                error_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
        
        print()  # Empty line
    
    print(f"{'='*60}")
    print(f"Summary: {success_count} updated, {error_count} errors")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    update_all_prices()
```

Make it executable:
```bash
chmod +x scripts/update_prices.py
```

#### B. Set Up Scheduled Execution

**Option 2A: Unix/Linux/macOS (Cron Job)**

1. Edit crontab:
```bash
crontab -e
```

2. Add entry (runs daily at 6 AM):
```bash
0 6 * * * cd /path/to/CoolFlightPrices && /path/to/.venv/bin/python scripts/update_prices.py >> logs/price_updates.log 2>&1
```

3. Alternative schedule examples:
```bash
# Twice per day (6 AM and 6 PM)
0 6,18 * * * cd /path/to/CoolFlightPrices && /path/to/.venv/bin/python scripts/update_prices.py >> logs/price_updates.log 2>&1

# Every 12 hours
0 */12 * * * cd /path/to/CoolFlightPrices && /path/to/.venv/bin/python scripts/update_prices.py >> logs/price_updates.log 2>&1

# Every day at 7:30 AM
30 7 * * * cd /path/to/CoolFlightPrices && /path/to/.venv/bin/python scripts/update_prices.py >> logs/price_updates.log 2>&1
```

**Option 2B: Windows (Task Scheduler)**

1. Open Task Scheduler
2. Create Basic Task:
   - **Name**: "Update Flight Prices"
   - **Trigger**: Daily at 6:00 AM
   - **Action**: Start a program
   - **Program**: `C:\path\to\.venv\Scripts\python.exe`
   - **Arguments**: `C:\path\to\CoolFlightPrices\scripts\update_prices.py`
   - **Start in**: `C:\path\to\CoolFlightPrices`

**Option 2C: Docker Container (Advanced)**

Create `Dockerfile.scheduler`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run cron
RUN apt-get update && apt-get install -y cron
COPY scripts/crontab /etc/cron.d/flight-tracker
RUN chmod 0644 /etc/cron.d/flight-tracker
RUN crontab /etc/cron.d/flight-tracker

CMD ["cron", "-f"]
```

#### C. Infrastructure Options

1. **Local Computer** (Free but requires always-on)
   - Run on your personal computer
   - Must be powered on and connected to internet
   - Good for: Testing, personal use

2. **Raspberry Pi** (One-time cost ~$50)
   - Low power consumption (< $5/year electricity)
   - Always-on home server
   - Good for: Long-term personal use

3. **Cloud VM** (Paid, ~$5-10/month)
   - **AWS EC2** (Free tier for 12 months, then ~$5/month)
   - **Google Cloud Compute** (Free tier, then ~$5/month)
   - **DigitalOcean** (~$5/month droplet)
   - **Heroku** (Free tier limited, hobby ~$7/month)
   - Good for: Production, sharing with others

4. **GitHub Actions** (Free for public repos)
   - Run as GitHub Actions workflow
   - Limited to 2,000 minutes/month on free tier
   - Good for: Open source projects

#### D. Monitoring and Logs

Create logs directory:
```bash
mkdir -p logs
```

View logs:
```bash
# View recent updates
tail -50 logs/price_updates.log

# View live updates
tail -f logs/price_updates.log

# Search for errors
grep "Error" logs/price_updates.log
```

### Best For
- Users who want comprehensive price tracking
- Sharing the app with others
- Production deployment
- Long-term price trend analysis
- Users with sufficient API quota

### Cost Estimate
- **API calls**: 10 flights × 30 days = 300 calls/month (within free tier)
- **Infrastructure**: $0-10/month depending on hosting choice
- **Time investment**: 2-4 hours initial setup, minimal maintenance

---

## Option 3: In-App Auto-Check ⭐ BEST BALANCE

### Description
The app automatically checks if prices need updating when the user visits the Price Tracker page. If prices are older than 24 hours, it refreshes them automatically.

### How It Works
1. User opens the Price Tracker page
2. App checks the `last_updated` timestamp for each flight
3. If > 24 hours old, automatically fetches new prices
4. Updates happen in the background with a loading indicator
5. User sees fresh prices without manual action

### Pros
- ✅ Automatic updates (no user action needed)
- ✅ No background infrastructure required
- ✅ Efficient API usage (only when app is used)
- ✅ Simple to implement and maintain
- ✅ Works with any deployment (cloud or local)
- ✅ Can manually force refresh if needed

### Cons
- ❌ Only updates when user visits the app
- ❌ Potential gaps if app not used for days
- ❌ Initial page load may be slower during updates

### API Usage
- **Per day**: Maximum 1 API call per flight (only if you visit the page)
- **Example**: 10 tracked flights, visit page daily = 10 calls/day = 300 calls/month
- **If you skip days**: Automatically catches up next time you visit
- **Monthly estimate**: Variable based on usage (typically 150-400 calls)

### Implementation
See the `in-app_auto-check` branch for full implementation.

### Best For
- Most users in most situations
- Personal use with regular checking
- Learning and experimentation
- Users who want automation without complexity
- Apps deployed to cloud platforms (Streamlit Cloud, Heroku, etc.)

---

## Comparison Table

| Feature | Option 1: Manual | Option 2: Background | Option 3: Auto-Check |
|---------|-----------------|---------------------|---------------------|
| **Automation** | ❌ Manual | ✅ Full | ✅ Semi-automatic |
| **Infrastructure** | None | Always-on server | None |
| **Complexity** | Low | High | Medium |
| **API Efficiency** | High (user control) | Medium (fixed schedule) | High (on-demand) |
| **Data Consistency** | Variable | Excellent | Good |
| **Setup Time** | 30 min | 2-4 hours | 1 hour |
| **Maintenance** | None | Ongoing | Minimal |
| **Cost** | Free | $0-10/month | Free |
| **Best For** | Testing/control | Production/sharing | Personal use |

---

## Recommendation

**Start with Option 3** (In-App Auto-Check):
- Provides automation without complexity
- No infrastructure costs
- Easy to upgrade to Option 2 later if needed
- Good balance for most use cases

**Upgrade to Option 2** if:
- You want guaranteed daily updates
- You're deploying for multiple users
- You need consistent data for analysis
- You have budget for infrastructure

**Use Option 1** if:
- You're testing the feature
- You have very limited API quota
- You only check prices occasionally
- You want maximum control

---

## Future Enhancements

Regardless of which option you choose, consider adding:

1. **Configurable update frequency** (6h, 12h, 24h, 48h)
2. **Price change notifications** (email/SMS when price drops)
3. **Smart update timing** (prioritize flights closer to departure)
4. **Batch update optimization** (group similar searches)
5. **Price prediction** (ML model to predict future prices)
6. **Alert thresholds** (notify when price drops below X%)

---

*Last updated: 2025-10-19*
