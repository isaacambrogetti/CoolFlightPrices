# Open-Jaw Flight Search Implementation

## Overview
This feature allows searching for flights where the return journey can be from a different destination airport or to a different origin airport than the outbound flight.

### Example Use Cases
- **Scenario 1**: Fly ZRH → LIS, return OPO → ZRH
- **Scenario 2**: Fly ZRH → LIS, return LIS → GVA
- **Scenario 3**: Multi-city trip exploration

## Implementation Approach: Option 1 (One-Way Combination)

Since the Amadeus Flight Offers Search API doesn't natively support multi-city/open-jaw searches in the basic tier, we'll combine separate one-way flight searches.

### How It Works

1. **User Input**:
   - Departure airports: [ZRH, GVA]
   - Arrival airports: [LIS, OPO]
   - Toggle: ☑️ "Allow different return airports (open-jaw)"

2. **Search Strategy**:
   
   **Normal Mode (Current)**:
   - 4 roundtrip searches:
     - ZRH ↔ LIS
     - ZRH ↔ OPO
     - GVA ↔ LIS
     - GVA ↔ OPO
   
   **Open-Jaw Mode (New)**:
   - 8 one-way searches (4 outbound + 4 return):
     - Outbound: ZRH → LIS, ZRH → OPO, GVA → LIS, GVA → OPO
     - Return: LIS → ZRH, LIS → GVA, OPO → ZRH, OPO → GVA
   - Combine compatible pairs to create complete itineraries
   - Total combinations: 16 possible open-jaw routes

3. **Combination Logic**:
   ```
   For each outbound flight (origin1 → dest1):
       For each return flight (origin2 → dest2):
           If outbound.destination == return.origin:  # Must depart from where you arrived
               If return.destination in user_origin_airports:  # Must return to one of origin airports
                   Create combined itinerary
                   Total price = outbound.price + return.price
   ```

### API Impact

**API Calls Comparison**:
- Normal roundtrip: 1 API call per route
- Open-jaw (one-way combination): 2 API calls per route (outbound + return)

**Example with 2 origins × 2 destinations**:
- Normal: 4 roundtrip calls = **4 API calls**
- Open-jaw: (4 outbound + 4 return) = **8 API calls**
- But creates: **16 possible itineraries** (much more flexibility!)

### UI Changes

1. **New Checkbox** (in multi-airport section):
   ```
   ☑️ Allow different return airports (open-jaw)
      ℹ️ Find cheaper deals by returning from/to different airports
      ⚠️ Note: Doubles API usage but may find significant savings
   ```

2. **Flight Display**:
   - Badge: `🔀 Open-Jaw` for mixed-airport itineraries
   - Clear route display: "ZRH → LIS / OPO → ZRH"
   - Price breakdown: Show combined price from two one-way flights

3. **Results Filtering**:
   - Option to show only open-jaw flights
   - Option to show only traditional roundtrips
   - Option to show all

### Files to Modify

1. **`src/api/amadeus_client.py`**:
   - Add method: `search_one_way_flights()`
   - Add method: `combine_one_way_flights()`

2. **`src/ui/app.py`**:
   - Add open-jaw checkbox in multi-airport section
   - Modify search logic to handle one-way combinations
   - Update route generation logic

3. **`src/api/batch_search.py`**:
   - Add support for one-way searches
   - Add method to combine results

4. **`src/visualization/heatmap.py`** (optional):
   - Update to handle open-jaw flight data

### Advantages of This Approach

✅ **Works with current API tier** - No special access needed
✅ **More flexibility** - Finds deals roundtrips can't
✅ **Transparent pricing** - Shows combined one-way prices
✅ **User control** - Optional toggle, not forced
✅ **Fallback safe** - Can keep both modes available

### Potential Improvements (Future)

- **Smart filtering**: Exclude unrealistic combinations (e.g., layover time too short)
- **Ground transport info**: Show travel time between airports (OPO → LIS)
- **Price comparison**: Highlight when open-jaw is cheaper than roundtrip
- **Multi-city extension**: Extend to 3+ cities if demand exists

### Testing Strategy

1. Test with 2×2 airport combination
2. Verify API call count matches expectations
3. Check price calculations are correct (sum of one-ways)
4. Ensure UI clearly distinguishes open-jaw vs roundtrip
5. Validate date logic (return date > departure date)

---

## Alternative: Option 2 (Multi-City API)

If Amadeus provides access to multi-city search endpoint:
- Would require testing `POST` to flight-offers-search with multi-segment request
- More efficient (1 API call instead of 2)
- Native pricing from airline (may differ from one-way sum)
- Implementation would be in separate branch for comparison

**Decision**: Implement Option 1 first (this branch), test Option 2 later if API access confirmed.
