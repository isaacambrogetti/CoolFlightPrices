# Trip Duration & Time Filtering Features

## Overview
New features to give you more control over flight search results based on your vacation preferences and schedule constraints.

## Feature 1: Trip Duration Strategy 🏖️

Choose how you want to approach your vacation length:

### 1. Flexible (any duration) - Default
- **Use when**: You have flexible time and want to see all options
- **Behavior**: Shows any trip length between your selected date ranges
- **Customize**: Set minimum days at destination (0-14 days)

### 2. Fixed duration
- **Use when**: You need exactly X days (e.g., exactly 7 days for a week vacation)
- **Behavior**: Only searches for trips with that exact duration
- **Customize**: Select trip duration (2-30 days)
- **Example**: If you select 7 days, it will only search for combinations where return date is exactly 7 days after departure

### 3. Maximum days possible
- **Use when**: You want the longest vacation possible within your flexibility
- **Behavior**: Prioritizes longer stays over cheaper prices
- **Customize**: Set minimum trip length
- **Results**: Sorted by longest duration first, then by price

## Feature 2: Flight Time Filtering ⏰

Filter results **after** search to exclude inconvenient flight times.

### Why after search?
- See all options first, then refine
- Don't miss good deals due to overly restrictive filters
- Flexible refinement without re-searching

### Departure Time Filter
**Exclude flights that depart too early or too late**

Examples:
- Don't want to wake up at 4 AM? Set minimum to 6:00
- Prefer morning flights? Set range 6:00 - 12:00
- Afternoon departures only? Set range 12:00 - 18:00

### Arrival Time Filter
**Exclude flights that arrive at inconvenient times**

Examples:
- Don't want to arrive late at night? Set maximum to 22:00
- Prefer daytime arrivals? Set range 6:00 - 20:00
- Avoid very early arrivals? Set minimum to 8:00

### How it works:
1. Search finds all available flights
2. Use the "⏰ Filter Results by Flight Times" expander
3. Enable departure and/or arrival filters
4. Use sliders to set acceptable time ranges (0-23 hours)
5. Results update immediately showing only flights within your time preferences

### Applied to:
- ✅ Outbound departure time
- ✅ Outbound arrival time
- ✅ Return departure time (for roundtrips)
- ✅ Return arrival time (for roundtrips)

## Usage Examples

### Example 1: Week-long vacation, no early mornings
```
Search Mode: Flexible Dates
Duration Strategy: Fixed duration (7 days)
Departure Range: Dec 1-5
Return Range: Dec 8-12

After search:
✓ Enable "Filter departure times"
✓ Set range: 08:00 - 22:00 (no early morning flights)
```

### Example 2: Maximum vacation time, reasonable hours
```
Search Mode: Flexible Dates
Duration Strategy: Maximum days possible
Minimum stay: 5 days
Departure Range: Nov 15-20
Return Range: Nov 25-30

After search:
✓ Enable "Filter departure times" → 7:00 - 21:00
✓ Enable "Filter arrival times" → 6:00 - 23:00
✓ Results show longest stays with convenient flight times
```

### Example 3: Flexible with no late night arrivals
```
Search Mode: Flexible Dates
Duration Strategy: Flexible
Minimum stay: 3 days
Departure Range: Jan 10-15
Return Range: Jan 15-20

After search:
✓ Enable "Filter arrival times"
✓ Set max to 22:00 (no midnight arrivals)
✓ Keep departure times unrestricted
```

## Benefits

### Trip Duration Control
- 🎯 **Fixed duration**: Get exactly the vacation length you need
- 📏 **Maximum days**: Prioritize longer stays for more exploration time
- 🔄 **Flexible**: See all options and choose based on price vs duration

### Time Filtering
- ☀️ **Convenience**: Avoid red-eye flights and dawn departures
- 🏠 **Logistics**: Plan around work schedules and family commitments
- 🛏️ **Comfort**: Ensure you arrive at reasonable hours
- 💰 **Smart**: See all deals first, filter by time second

## Technical Details

### Fixed Duration Implementation
- Converts total trip days to "days at destination" (excludes departure/return days)
- Filters date combinations to only include exact matches
- Example: 7-day trip = 6 days at destination + 1 day travel each way

### Maximum Days Strategy
- Generates all valid combinations above minimum
- Sorts results by duration (descending), then price (ascending)
- Shows longest possible stays at the top of results

### Time Filtering
- Applies after search completion (no additional API calls)
- Filters both outbound and return flights
- Updates price statistics based on filtered results
- Shows count of filtered combinations

## Tips

1. **Start broad, then narrow**: 
   - Use flexible duration first to see price trends
   - Then switch to fixed or maximum if you have specific needs

2. **Time filtering workflow**:
   - Run search first with no time restrictions
   - Review all options and price distribution
   - Apply time filters to exclude inconvenient flights
   - Compare filtered vs unfiltered prices to decide if time restrictions are worth it

3. **Balance duration vs price**:
   - "Maximum days" mode shows if longer stays are significantly more expensive
   - Use this to decide if 2-3 extra days are worth the price difference

4. **API efficiency**:
   - Fixed duration reduces API calls (fewer valid combinations)
   - Time filtering happens client-side (no extra API calls)

## Future Enhancements

Potential additions:
- Multiple time preferences (e.g., "prefer 10-14h but allow 6-22h")
- Connection time preferences
- Specific airline preferences
- Flight number restrictions
- Layover duration filtering
