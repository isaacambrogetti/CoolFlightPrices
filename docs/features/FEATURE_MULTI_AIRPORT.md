# Multi-Airport Search Feature

## Overview
The multi-airport search feature allows you to compare flight prices across multiple origin and/or destination airports simultaneously. This helps you find the absolute cheapest option when you have flexibility with your departure or arrival airports.

## Use Cases

### Common Scenarios
1. **Multiple nearby airports**: Compare ZRH (Zurich), GVA (Geneva), and BSL (Basel) when flying from Switzerland
2. **City with multiple airports**: Search NYC (JFK, LGA, EWR) or London (LHR, LGW, STN, LTN)
3. **Flexible destination**: Compare multiple Portuguese airports (LIS, OPO, FAO) to find best deal
4. **Regional flexibility**: Search all major European hubs (FRA, AMS, CDG, MUC) for connections

## How to Use

### 1. Enable Multi-Airport Mode
In the sidebar:
1. Check ✅ **"Compare multiple airports"**
2. Text inputs change from single-line to multi-line text areas

### 2. Enter Airport Codes
Enter multiple 3-letter IATA airport codes separated by commas:

**From (Origins):**
```
ZRH, GVA, BSL
```

**To (Destinations):**
```
LIS, OPO, FAO
```

### 3. View Combination Count
The UI shows how many routes will be searched:
```
🔄 Will search 9 airport combinations: 3 origin × 3 destination
```

If searching >10 combinations:
```
⚠️ Searching many airports will use more API calls and take longer!
```

### 4. Search & Compare
- **Single Date Mode**: All routes searched with same date, results sorted by price
- **Flexible Date Mode**: All routes searched across all date combinations

## Features

### Smart Route Display
Results clearly show which route each flight belongs to:

**Single Date Search:**
```
💰 EUR 156.42 - [ZRH→LIS] LH 1234 (Cheapest!)
💰 EUR 162.80 - [GVA→LIS] EZY 5678
💰 EUR 178.90 - [ZRH→OPO] TP 9012
```

**Flexible Date Search:**
```
#1: EUR 142.30 - Dec 15 → Dec 22 (8 days) [BSL→FAO]
#2: EUR 156.42 - Dec 20 → Dec 27 (8 days) [ZRH→LIS]
#3: EUR 162.80 - Dec 18 → Dec 25 (8 days) [GVA→OPO]
```

### Route Statistics
See results per route:
```
🛫 Results per route: BSL→FAO: 12, GVA→LIS: 8, ZRH→LIS: 15, ZRH→OPO: 10
```

### Integrated with All Features
Multi-airport works seamlessly with:
- ✅ Single date search
- ✅ Flexible date range search  
- ✅ Time filtering (departure/arrival hours)
- ✅ Trip duration strategies (Fixed/Flexible/Maximum days)
- ✅ Price visualizations (heatmaps show all routes)

## API Call Estimation

### Single Date Search
```
API Calls = Number of Origins × Number of Destinations
```

Examples:
- 1 origin, 3 destinations = 3 API calls
- 3 origins, 3 destinations = 9 API calls
- 5 origins, 5 destinations = 25 API calls

### Flexible Date Search
```
API Calls = (Num Origins × Num Destinations) × Num Date Combinations
```

Examples:
- 2 origins, 2 destinations, 25 dates = 100 API calls
- 3 origins, 3 destinations, 30 dates = 270 API calls

**Tip**: Use "Smart Sampling" to reduce date combinations!

## Performance Considerations

### API Quota
With Amadeus free tier (2000 calls/month):
- Daily limit: ~66 calls/day
- Multi-airport searches count toward this limit
- Monitor your usage carefully

### Search Time
- Each route takes ~2-5 seconds (with rate limiting)
- 10 routes = ~20-50 seconds
- Progress bar shows current route being searched

### Recommendations
1. **Start small**: Test with 2-3 airports first
2. **Use smart sampling**: Enable for date range searches
3. **Combine strategically**: 3×3 (9 routes) is usually sufficient
4. **Nearby airports only**: Airports within 100km are most useful

## Examples

### Example 1: Swiss Departure Flexibility
```
From: ZRH, GVA, BSL
To: LIS
```
Finds cheapest way to get from Switzerland to Lisbon, comparing Zurich, Geneva, and Basel airports.

### Example 2: Portuguese Destination Flexibility
```
From: ZRH
To: LIS, OPO, FAO
```
Compares Lisbon, Porto, and Faro to find best Portuguese destination deal.

### Example 3: Full Flexibility
```
From: ZRH, GVA
To: LIS, OPO
```
4 combinations: ZRH→LIS, ZRH→OPO, GVA→LIS, GVA→OPO

### Example 4: NYC Airports (One-way)
```
From: JFK, LGA, EWR
To: LAX
Trip Type: One-way
```
Compare all three New York area airports for flight to Los Angeles.

## Technical Details

### Data Structure
Each `SearchResult` now includes:
```python
@dataclass
class SearchResult:
    # ... existing fields ...
    origin: Optional[str] = None          # e.g., "ZRH"
    destination: Optional[str] = None      # e.g., "LIS"
```

### Search Flow

**Single Date Mode:**
1. Parse comma-separated airport codes
2. Create route combinations: `[(O1,D1), (O1,D2), (O2,D1), ...]`
3. Search each route sequentially
4. Tag each flight with `search_route` key
5. Combine all results and sort by price
6. Display with route labels

**Flexible Date Mode:**
1. Parse airport codes and create route combinations
2. Generate date combinations (same for all routes)
3. For each route:
   - Search all date combinations
   - Track progress per route
   - Tag results with origin/destination
4. Combine all results from all routes
5. Sort by price (or duration for "Maximum days" mode)
6. Display with route info in expandable sections

### Validation
- Each airport code must be exactly 3 letters
- Invalid codes rejected with error message
- Empty lists rejected
- Shows which codes are invalid

### Progress Tracking
```
[ZRH→LIS] Searching date combinations (25/30) (1/4 routes)
[GVA→LIS] Searching date combinations (10/30) (2/4 routes)
```

## Limitations

### Current Limitations
1. **No radius search**: Must manually enter nearby airports
2. **No automatic airport suggestions**: User must know IATA codes
3. **No filtering by airport**: Can't exclude specific combinations after search
4. **Sequential search**: Routes searched one at a time (not parallel)

### Future Enhancements
Possible improvements:
1. **Airport autocomplete**: Type-ahead with airport names
2. **Nearby airport finder**: "Show all airports within 100km of ZRH"
3. **Airport groups**: Save "Swiss Airports" = ZRH,GVA,BSL
4. **Parallel search**: Search multiple routes simultaneously
5. **Result filtering**: Filter by origin/destination after search
6. **Price comparison table**: Matrix view of all route/date combinations
7. **Distance consideration**: Factor in travel distance to airport

## Tips & Tricks

### 1. Nearby Airport Research
Before searching, find nearby airports:
- Google: "airports near [city]"
- Wikipedia: Most cities list all nearby airports
- Airlines: Check which airports they serve

### 2. Strategic Combinations
- **High-cost origin**: Compare multiple cheap destination airports
- **Expensive destination**: Compare multiple origin airports
- **Connection hubs**: Include major hub airports for better prices

### 3. Time Optimization
- Test single date first to verify all airports work
- Use "Smart Sampling" for flexible date searches
- Limit to 3-4 airports per side for reasonable search time

### 4. API Quota Management
- **Morning check**: 3×3 airports, 25 dates = 225 calls (~11% monthly quota)
- **Quick compare**: 2×2 airports, single date = 4 calls
- Track your usage to stay under 2000/month

### 5. Best Value Searches
Most valuable multi-airport scenarios:
1. **Budget airlines**: Often use secondary airports (Ryanair, EasyJet)
2. **Multiple Swiss airports**: Significant price differences common
3. **London airports**: LHR vs LGW vs STN can vary by 50%+
4. **NYC/Bay Area**: JFK/LGA/EWR or SFO/OAK/SJC

## Troubleshooting

### "No flights found for any route"
- Verify all airport codes are valid
- Try different dates (some routes may have limited service)
- Check if airports have connections to each other

### "Search taking too long"
- Reduce number of airports
- Enable "Smart Sampling" for date ranges
- Use single date search first to test

### "Too many API calls warning"
- Reduce number of airports (e.g., 3×3 instead of 5×5)
- Reduce date range or use sampling
- Split search into multiple smaller searches

### Invalid airport codes
- Must be exactly 3 letters
- Must be IATA codes (not ICAO or city codes)
- Example valid: ZRH, JFK, LHR
- Example invalid: Zurich, LSZH, New York

## Examples by Region

### Europe
```
Switzerland to Portugal:
From: ZRH, GVA, BSL
To: LIS, OPO, FAO

UK to Spain:
From: LHR, LGW, STN
To: MAD, BCN, AGP

Germany to Greece:
From: FRA, MUC, BER
To: ATH, HER, RHO
```

### North America
```
East Coast to West Coast:
From: JFK, LGA, EWR
To: LAX, SFO, SAN

Florida to NYC:
From: MIA, FLL, PBI
To: JFK, LGA, EWR

Texas Triangle:
From: DFW, DAL
To: IAH, HOU
```

### Asia
```
Japan Multi-City:
From: NRT, HND
To: KIX, ITM, KOB

Southeast Asia:
From: SIN, KUL
To: BKK, HKT, CNX
```

## Summary

The multi-airport search feature is perfect for:
- ✅ Finding absolute cheapest flights when you have airport flexibility
- ✅ Comparing budget airline hubs vs major airports
- ✅ Exploring multiple destination options
- ✅ Maximizing value from your Amadeus API quota

**Pro tip**: Combine multi-airport with flexible dates and time filtering for the ultimate flight deal finder! 🚀

## Related Documentation
- `USAGE_GUIDE.md` - General usage instructions
- `DATE_RANGE_COMPLETE.md` - Flexible date search feature
- `FEATURE_TRIP_PREFERENCES.md` - Duration strategies and time filtering
- `API_QUOTA_MANAGEMENT.md` - Managing your API usage (TODO)
