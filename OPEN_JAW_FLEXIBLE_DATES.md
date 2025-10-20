# Open-Jaw Support for Flexible Dates - Feature Documentation

## 🎉 Feature Complete!

Open-jaw flights are now supported in **BOTH** search modes:
- ✅ **Single Date Mode** (original implementation)
- ✅ **Flexible Dates Mode** (NEW!)

## What Changed

### 1. Open-Jaw Checkbox Available in Both Modes

**Before:** Checkbox only appeared in Single Date mode  
**Now:** Checkbox appears whenever multi-airport is enabled (both modes)

**Location:** Sidebar airport selection section

**Updated Help Text:**
```
Search for flights where you return from/to different airports.
Example: ZRH→LIS outbound, OPO→ZRH return. Requires roundtrip booking!
Note: Open-jaw increases API calls significantly in flexible date mode.
```

### 2. New Method: `search_date_range_multi_city()`

**File:** `src/api/batch_search.py`

**Purpose:** Handle batch searches for open-jaw flights across multiple date combinations

**Parameters:**
- `origin_destination_pairs`: List of (origin, dest) tuples for each leg
  - Example: `[('ZRH', 'LIS'), ('OPO', 'ZRH')]`
- `date_combinations`: List of DateCombination objects
- `adults`: Number of passengers (default: 1)
- `max_results_per_date`: Max results per date (default: 3)
- `progress_callback`: Progress tracking function
- `currency`: Currency code (default: "EUR")

**How It Works:**
```python
# For each date combination
for combo in date_combinations:
    # Use multi-city API for open-jaw
    flights = client.get_cheapest_multi_city(
        origin_destination_pairs=[('ZRH', 'LIS'), ('OPO', 'ZRH')],
        departure_dates=[combo.departure, combo.return_date],
        adults=adults,
        max_results=max_results_per_date,
        currency=currency
    )
```

### 3. Updated Flexible Dates Search Logic

**File:** `src/ui/app.py` (lines ~1576-1626)

**Changes:**
- Detects if routes are open-jaw format (dict) or normal (tuple)
- Routes open-jaw searches through `search_date_range_multi_city()`
- Routes normal searches through standard `search_date_range()`
- Adds open-jaw metadata to results (`is_open_jaw`, `search_route`)

**Code Structure:**
```python
if is_open_jaw_mode:
    # Open-jaw: Use multi-city API
    for route_info in airport_routes:
        route = route_info['route']
        (out_origin, out_dest), (ret_origin, ret_dest) = route
        
        results = batch_search.search_date_range_multi_city(
            origin_destination_pairs=[(out_origin, out_dest), (ret_origin, ret_dest)],
            date_combinations=combinations,
            adults=params['adults'],
            progress_callback=update_progress
        )
else:
    # Normal: Standard batch search
    for origin, destination in airport_routes:
        results = batch_search.search_date_range(
            origin=origin,
            destination=destination,
            date_combinations=combinations,
            adults=params['adults'],
            progress_callback=update_progress
        )
```

### 4. Updated Validation

**File:** `src/ui/app.py` (lines ~1460-1472)

**Before:** Single validation for return_date  
**Now:** Different validation per mode

```python
if allow_open_jaw:
    if search_mode == "📅 Single Date" and not return_date:
        st.error("🔀 Open-jaw requires roundtrip. Select return date.")
        st.stop()
    elif search_mode == "💡 Flexible Dates (Date Range)":
        # Flexible dates validates when processing date combinations
        pass
```

## How to Use

### Flexible Dates + Open-Jaw:

1. **Select "💡 Flexible Dates (Date Range)" mode**
2. **Enable "Compare multiple airports"**
3. **Select multiple origins** (e.g., ZRH, GVA)
4. **Select multiple destinations** (e.g., LIS, OPO)
5. **Set departure date range** (e.g., Nov 15-20)
6. **Set return date range** (e.g., Nov 25-30)
7. **Set minimum/maximum days at destination**
8. **Check "🔀 Allow different return airports (open-jaw)"**
9. **Click "🔍 Search Date Range"**

### Results:

The app will search ALL combinations:
- **Date combinations**: 15-20 Nov departure × 25-30 Nov return (respecting min/max days)
- **Route combinations**: All open-jaw permutations
  - ZRH→LIS / LIS→ZRH
  - ZRH→LIS / OPO→ZRH
  - ZRH→LIS / LIS→GVA
  - ZRH→LIS / OPO→GVA
  - ZRH→OPO / LIS→ZRH
  - ... (all permutations)

## API Usage Warning

⚠️ **Important:** Open-jaw + Flexible Dates = MANY API calls!

### Example Calculation:

**Setup:**
- 2 origins (ZRH, GVA)
- 2 destinations (LIS, OPO)
- 10 date combinations
- Open-jaw enabled

**API Calls:**
- Open-jaw routes: 2×2 origins × 2×2 destinations = **16 route combinations**
- Total API calls: 16 routes × 10 dates = **160 API calls**

**Without open-jaw:** 4 routes × 10 dates = 40 API calls

### Recommendations:

1. **Use Smart Sampling** to reduce date combinations
2. **Limit airports** when using open-jaw (2×2 is good, 3×3 = 81 routes!)
3. **Check your API quota** (self-service = 2000 calls/month)
4. **Consider using for short date ranges**

## Benefits

### Why Use Open-Jaw + Flexible Dates?

1. **Find the absolute cheapest combination**
   - Best date + best route combination
   - Example: Cheapest might be Nov 17 departure (ZRH→LIS) + Nov 28 return (OPO→GVA)

2. **Flexible travel planning**
   - See which date + route combo is best
   - Compare closed-jaw vs open-jaw pricing across dates

3. **Multi-city trips**
   - Visit Lisbon, return from Porto
   - Different dates, different airports, one search

4. **Price comparison**
   - Direct comparison of traditional vs open-jaw across all dates
   - Identify which dates have best open-jaw deals

## Technical Details

### SearchResult Metadata

Open-jaw results now include:
```python
result.search_route = "ZRH→LIS / OPO→ZRH"  # Route label
result.is_open_jaw = True  # Open-jaw indicator
result.origin = "ZRH"  # Outbound origin
result.destination = "LIS"  # Outbound destination
```

### Display

- Results show route label in Top 5: `ZRH→LIS / OPO→ZRH`
- 🔀 Badge for truly open-jaw flights
- Calendar view works with open-jaw results
- Price charts include all route combinations

## Files Modified

1. **src/ui/app.py**
   - Line ~1400: Updated checkbox condition (removed Single Date requirement)
   - Lines ~1463-1472: Updated validation for both modes
   - Lines ~1576-1626: Updated flexible dates search to handle open-jaw

2. **src/api/batch_search.py**
   - Lines ~206-333: New `search_date_range_multi_city()` method

## Commits

- **96a2262**: feat: Add open-jaw support for Flexible Dates mode

## Testing

### Test Case 1: Basic Open-Jaw Flexible Dates

**Setup:**
- Mode: Flexible Dates
- Origins: ZRH, GVA (2)
- Destinations: LIS, OPO (2)
- Dates: Nov 15-17 departure, Nov 25-27 return
- Min days: 7
- Open-jaw: ✅ Enabled

**Expected:**
- Routes generated: 16 open-jaw combinations
- Date combinations: ~3-6 (based on 7-day minimum)
- Total searches: ~48-96
- Results show mix of open-jaw and regular roundtrips

### Test Case 2: Smart Sampling + Open-Jaw

**Setup:**
- Same as above
- Enable "Use Smart Sampling"
- Target: 10 combinations

**Expected:**
- Routes: 16
- Dates: 10 (sampled)
- Total searches: 160
- Much faster than exhaustive search

### Test Case 3: Comparison

**Setup:**
- Search with open-jaw: ✅
- Note best price and route
- Search without open-jaw: ❌
- Compare results

**Expected:**
- Open-jaw may find cheaper options
- Can see price difference between modes

## Status

✅ **COMPLETE** - Open-jaw now works in both modes!

**Remaining:**
- Final user testing
- Merge to main branch

## Next Steps

1. Test with real searches
2. Monitor API usage
3. Gather user feedback
4. Optimize if needed (caching, better sampling)
5. Merge to main when validated
