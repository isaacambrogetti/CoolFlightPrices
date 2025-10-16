# Intelligent Date Range Search - Implementation Plan

## 🎯 Goal
Enable users to search flights across multiple date combinations to find the best deals within their flexible travel window.

## 📋 Requirements

### User Needs:
1. **Flexible departure dates** - "I can leave between Nov 10-15"
2. **Flexible return dates** - "I can return between Nov 20-25"
3. **Minimum stay** - "I need at least 3 full days at destination"
4. **Price comparison** - "Show me all options sorted by price"
5. **Visual overview** - "Let me see prices across all date combinations"

### Use Case Example:
```
User wants a trip to Lisbon:
- Can depart: Nov 10, 11, 12, 13, or 14 (5 options)
- Can return: Nov 20, 21, 22, or 23 (4 options)
- Must be in Lisbon for at least 3 full days
- Total combinations: 5 × 4 = 20 searches
- Valid combinations: Only those where stay >= 3 days
```

## 🏗️ Architecture

### 1. Date Range Logic
```python
class DateRangeSearch:
    def generate_combinations(
        departure_start: date,
        departure_end: date,
        return_start: date,
        return_end: date,
        min_days_at_destination: int
    ) -> List[Tuple[date, date]]:
        """
        Generate all valid (departure, return) combinations
        that satisfy minimum stay requirement
        """
```

### 2. API Call Strategy

**Option A: Brute Force (Simple)**
- Call API for each date combination
- Pros: Complete data, simple logic
- Cons: Many API calls, slow
- Example: 5×4 = 20 API calls

**Option B: Amadeus Flight Inspiration Search (Smart)**
- Single API call for flexible dates
- Pros: 1 API call, faster, cheaper
- Cons: Less precise, may not have all combinations
- API: `GET /v1/shopping/flight-dates`

**Recommendation**: Start with Option A (brute force) with rate limiting, add Option B as optimization later.

### 3. Rate Limiting Strategy
```python
- Batch searches with delays
- Show progress bar during search
- Cache results to avoid duplicate calls
- Option to limit max combinations (e.g., "search max 30 combinations")
```

### 4. Results Display

**Table View:**
```
| Departure | Return | Duration | Price | Airline | Details |
|-----------|--------|----------|-------|---------|---------|
| Nov 10    | Nov 20 | 10 days  | €162  | TAP     | [View]  |
| Nov 10    | Nov 21 | 11 days  | €175  | TAP     | [View]  |
| Nov 11    | Nov 20 | 9 days   | €158  | TAP     | [View]  | ← Cheapest
| ...       | ...    | ...      | ...   | ...     | ...     |
```

**Calendar Heatmap:**
```
          Return Date
          20   21   22   23
Dep  10  €162 €175 €180 €190
     11  €158 €165 €172 €185
     12  €170 €172 €178 €195
     13  €165 €168 €175 €188
     14  €180 €185 €190 €200
     
Color scale: Green (cheap) → Red (expensive)
```

## 📝 Implementation Steps

### Step 1: Backend - Date Range Generator
**File**: `src/api/date_range_search.py`

```python
from datetime import date, timedelta
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class DateCombination:
    departure: date
    return_date: date
    days_at_destination: int
    
    @property
    def total_duration(self) -> int:
        return (self.return_date - self.departure).days

def generate_date_combinations(
    departure_start: date,
    departure_end: date,
    return_start: date,
    return_end: date,
    min_days_at_destination: int = 0
) -> List[DateCombination]:
    """
    Generate all valid date combinations
    
    Args:
        departure_start: Earliest departure date
        departure_end: Latest departure date
        return_start: Earliest return date
        return_end: Latest return date
        min_days_at_destination: Minimum full days at destination
        
    Returns:
        List of valid DateCombination objects
    """
    combinations = []
    
    current_dep = departure_start
    while current_dep <= departure_end:
        current_ret = return_start
        while current_ret <= return_end:
            # Calculate days at destination
            # Arrival day doesn't count, departure day doesn't count
            days_at_dest = (current_ret - current_dep).days - 1
            
            if days_at_dest >= min_days_at_destination:
                combinations.append(DateCombination(
                    departure=current_dep,
                    return_date=current_ret,
                    days_at_destination=days_at_dest
                ))
            
            current_ret += timedelta(days=1)
        current_dep += timedelta(days=1)
    
    return combinations
```

### Step 2: Backend - Batch Flight Search
**File**: `src/api/batch_search.py`

```python
from typing import List, Dict, Callable
from datetime import date
import time
from src.api.amadeus_client import AmadeusClient
from src.api.rate_limiter import RateLimiter

class BatchFlightSearch:
    def __init__(self, client: AmadeusClient):
        self.client = client
        self.rate_limiter = RateLimiter(calls_per_minute=10)
    
    def search_date_range(
        self,
        origin: str,
        destination: str,
        date_combinations: List[DateCombination],
        progress_callback: Callable[[int, int], None] = None
    ) -> List[Dict]:
        """
        Search flights for multiple date combinations
        
        Args:
            origin: Origin airport
            destination: Destination airport
            date_combinations: List of date combinations to search
            progress_callback: Function to report progress (current, total)
            
        Returns:
            List of search results with metadata
        """
        results = []
        total = len(date_combinations)
        
        for i, combo in enumerate(date_combinations):
            # Rate limiting
            self.rate_limiter.wait_if_needed()
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total)
            
            try:
                # Search flights
                flights = self.client.get_cheapest_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=combo.departure,
                    return_date=combo.return_date,
                    max_results=3  # Only get top 3 for each date
                )
                
                # Add metadata
                result = {
                    'departure_date': combo.departure,
                    'return_date': combo.return_date,
                    'days_at_destination': combo.days_at_destination,
                    'total_duration': combo.total_duration,
                    'flights': flights,
                    'cheapest_price': flights[0]['price'] if flights else None,
                    'searched_at': date.today()
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"Error searching {combo.departure} -> {combo.return_date}: {e}")
                results.append({
                    'departure_date': combo.departure,
                    'return_date': combo.return_date,
                    'error': str(e)
                })
        
        return results
```

### Step 3: Frontend - Updated UI
**File**: `src/ui/app.py` (modifications)

Add new UI components:
```python
# In sidebar
search_mode = st.radio(
    "Search Mode",
    ["Single Date", "Date Range (Flexible)"],
    help="Single date for specific flights, Date Range to compare multiple dates"
)

if search_mode == "Date Range (Flexible)":
    st.markdown("### Departure Dates")
    col1, col2 = st.columns(2)
    with col1:
        dep_start = st.date_input("From", ...)
    with col2:
        dep_end = st.date_input("To", ...)
    
    st.markdown("### Return Dates")
    col1, col2 = st.columns(2)
    with col1:
        ret_start = st.date_input("From", ...)
    with col2:
        ret_end = st.date_input("To", ...)
    
    min_days = st.slider(
        "Minimum days at destination",
        min_value=0,
        max_value=14,
        value=3,
        help="Minimum full days you want to spend at destination"
    )
    
    # Show preview
    num_combinations = calculate_combinations(...)
    st.info(f"This will search {num_combinations} date combinations")
    
    if num_combinations > 50:
        st.warning("⚠️ Many combinations! This will use {num_combinations} API calls.")
```

### Step 4: Results Display
```python
# Display results as DataFrame
df = pd.DataFrame(results)
df = df.sort_values('cheapest_price')

# Add styling
st.dataframe(
    df,
    column_config={
        "cheapest_price": st.column_config.NumberColumn(
            "Price",
            format="€%.2f"
        ),
        "days_at_destination": st.column_config.NumberColumn(
            "Days There",
            format="%d days"
        )
    }
)

# Highlight best deal
best_deal = df.iloc[0]
st.success(f"🎉 Best Deal: {best_deal['departure_date']} → {best_deal['return_date']} for €{best_deal['cheapest_price']}")
```

### Step 5: Visualization - Price Heatmap
**File**: `src/visualization/heatmap.py`

```python
import plotly.graph_objects as go
import pandas as pd

def create_price_heatmap(results: List[Dict]) -> go.Figure:
    """
    Create a heatmap showing prices across date combinations
    """
    # Create pivot table
    df = pd.DataFrame(results)
    pivot = df.pivot_table(
        values='cheapest_price',
        index='departure_date',
        columns='return_date',
        aggfunc='min'
    )
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[d.strftime('%b %d') for d in pivot.columns],
        y=[d.strftime('%b %d') for d in pivot.index],
        colorscale='RdYlGn_r',  # Red (expensive) to Green (cheap)
        text=pivot.values,
        texttemplate='€%{text:.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Price (EUR)")
    ))
    
    fig.update_layout(
        title="Price Comparison Across Dates",
        xaxis_title="Return Date",
        yaxis_title="Departure Date",
        height=500
    )
    
    return fig
```

## 🎨 UI/UX Considerations

### Progress Indication
```python
progress_bar = st.progress(0)
status_text = st.empty()

def update_progress(current, total):
    progress_bar.progress(current / total)
    status_text.text(f"Searching... {current}/{total} combinations")
```

### Caching
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def search_date_range_cached(origin, dest, dep_start, dep_end, ret_start, ret_end, min_days):
    # ... search logic
    return results
```

### Smart Defaults
- Default range: 3-5 days for departure, 3-5 days for return
- Auto-calculate reasonable minimum stay (e.g., trip_duration / 3)
- Limit max combinations to 30 initially

## 📊 Testing Strategy

### Test Cases:
1. **Small range**: 2 departure dates × 2 return dates = 4 combinations
2. **Medium range**: 5 departure dates × 4 return dates = 20 combinations
3. **Large range**: 7 departure dates × 7 return dates = 49 combinations
4. **Edge cases**:
   - Return date before departure date (should be filtered)
   - Minimum days not met (should be filtered)
   - API errors (should show partial results)

### API Quota Management:
- Show warning if combinations > 50
- Allow user to reduce range
- Option to "sample" dates (every 2-3 days) for large ranges

## 🚀 Rollout Plan

### Version 1.1: Basic Date Range
- ✅ Date range pickers
- ✅ Combination generator
- ✅ Batch search with progress
- ✅ Results table sorted by price
- ⏳ Basic filtering

### Version 1.2: Enhanced Display
- ⏳ Price heatmap visualization
- ⏳ Interactive filtering
- ⏳ Export results to CSV
- ⏳ Save search criteria

### Version 1.3: Optimization
- ⏳ Result caching
- ⏳ Smart sampling for large ranges
- ⏳ Amadeus Flight Inspiration API integration
- ⏳ Background search option

## 💡 Future Enhancements

- **Flexible duration**: "3-5 day trips"
- **Day of week preferences**: "Prefer weekend departures"
- **Price alerts**: "Notify if price drops below €150"
- **Historical data**: Show price trends
- **Recommendations**: "Best value" vs "Shortest trip" vs "Most flexible"

---

Ready to implement? Let's start with Step 1! 🚀
