# CoolFlightPrices - Usage Guide

## Quick Start

1. **Start the application**:
   ```bash
   cd /Users/isaac/Documents/Progettini/CoolFlightPrices
   source .venv/bin/activate
   streamlit run src/ui/app.py
   ```

2. **Open in browser**: http://localhost:8501

## Search Modes

### Single Date Search 📅
**Use when**: You know exactly when you want to travel

**Steps**:
1. Select "📅 Single Date" from sidebar
2. Enter origin and destination (e.g., ZRH, LIS)
3. Select departure date
4. Select return date (or leave blank for one-way)
5. Choose number of adults
6. Click "Search Flights"

**Features**:
- Shows up to 10 cheapest flights
- Can filter results by departure/arrival times after search
- Displays flight details, stops, duration

### Flexible Dates Search 🗓️
**Use when**: You have flexibility and want to find the best deal

**Steps**:
1. Select "💡 Flexible Dates" from sidebar
2. Enter origin and destination
3. Set departure date range (earliest → latest)
4. Set return date range (earliest → latest)
5. Choose trip duration strategy:
   - **Flexible**: Any duration
   - **Fixed**: Exactly X days (e.g., 7 days)
   - **Maximum days**: Prioritize longest stays
6. Set minimum days at destination
7. Click "Search Flights"

**Features**:
- Searches multiple date combinations
- Smart sampling for large date ranges
- Interactive visualizations:
  - Price heatmap (departure vs return dates)
  - Price distribution histogram
  - Duration vs Price scatter plot
  - Calendar view of prices
- Filter by flight times after results appear

## Trip Duration Strategies

### 1. Flexible (any duration)
- Shows all trip lengths within your date ranges
- Customize minimum days at destination (0-14)
- Results sorted by price (cheapest first)

### 2. Fixed duration
- Search only for trips of exact length
- Example: Set "7 days" to find week-long vacations
- Reduces API calls (fewer valid combinations)
- Results sorted by price

### 3. Maximum days possible
- Find longest vacations within your flexibility
- Set minimum trip length
- Results sorted by duration (longest first), then price
- Great for maximizing exploration time

## Time Filtering

**Available after search completes** - no additional API calls!

### Departure Time Filter
Filter out flights that depart too early or too late:
- Early morning: Exclude flights before 6:00 AM
- Late evening: Exclude flights after 10:00 PM
- Custom range: Set any hour range (0-23)

### Arrival Time Filter
Filter out flights that arrive at inconvenient times:
- Late night: Exclude arrivals after 11:00 PM
- Very early: Exclude arrivals before 6:00 AM
- Custom range: Set any hour range

### How to Use:
1. Run search first (see all options)
2. Expand "⏰ Filter Results by Flight Times"
3. Enable departure and/or arrival filters
4. Adjust time ranges with sliders
5. Results update instantly

**Applies to**: Both outbound and return flights (for roundtrips)

## Smart Features

### API Call Optimization
- **Small searches** (< 50 combinations): Searches all dates
- **Medium searches** (50-100): Optional smart sampling
- **Large searches** (> 100): Must narrow date ranges or use sampling

### Smart Sampling
When enabled:
- Samples ~20-30 date combinations from your range
- Evenly distributed across departure and return ranges
- Always includes first and last dates
- Maintains good coverage while reducing API calls

### Progress Tracking
- Real-time progress bar during searches
- Shows current/total searches
- Displays any errors encountered
- Continues even if some searches fail

## Understanding Results

### Statistics Dashboard
- **Searches**: Total date combinations searched
- **Found Flights**: How many had available flights
- **Cheapest**: Lowest price found
- **Average**: Average price across all results

### Best Deals Section
Shows top 5 best options:
- **Flexible/Fixed mode**: Sorted by price (cheapest first)
- **Maximum days mode**: Sorted by duration (longest first)
- Click to expand for full flight details

### Visualizations

#### Price Heatmap
- X-axis: Departure dates
- Y-axis: Return dates
- Color: Price (green = cheaper, red = expensive)
- Hover: See exact dates and prices

#### Price Distribution
- Histogram showing price frequency
- See if most flights are in a certain price range
- Identify outliers (very cheap or expensive)

#### Duration vs Price
- Scatter plot: trip length vs price
- See if longer trips cost more
- Find sweet spots (good price for longer stays)

#### Calendar View
- Bar chart by departure date
- Compare prices across different departure days
- Identify cheapest days to depart

## Tips & Best Practices

### 1. Start Broad
- Begin with wide date ranges to see trends
- Then narrow down based on results
- Use visualizations to identify patterns

### 2. Time Filtering Strategy
```
1. Search without time restrictions first
2. Review all options and price distribution
3. Apply time filters to exclude inconvenient flights
4. Compare filtered vs unfiltered prices
5. Decide if convenience is worth price difference
```

### 3. Duration Optimization
- Use "Flexible" to see price vs duration trade-offs
- Switch to "Fixed" when you know exact vacation length
- Use "Maximum days" to find best price for longest stays

### 4. API Quota Management
- Free tier: 2000 API calls/month
- Small date ranges: More precise results
- Large date ranges: Use smart sampling
- Track usage to avoid exceeding quota

### 5. Airport Codes
Common IATA codes:
- **ZRH**: Zurich, Switzerland
- **LIS**: Lisbon, Portugal
- **JFK**: New York JFK, USA
- **LHR**: London Heathrow, UK
- **CDG**: Paris Charles de Gaulle, France
- **AMS**: Amsterdam, Netherlands
- **BCN**: Barcelona, Spain
- **FCO**: Rome Fiumicino, Italy

Search online for other airport codes.

## Troubleshooting

### "No flights found"
- ✓ Verify airport codes (3-letter IATA codes)
- ✓ Try different dates
- ✓ Check if route is valid (some airports may not have direct connections)
- ✓ Try more popular nearby airports

### "API Error" / "401 Unauthorized"
- ✓ Check API credentials in `.env` file
- ✓ Verify credentials are valid on Amadeus dashboard
- ✓ Ensure API key hasn't expired

### "Too many API calls"
- ✓ Narrow your date ranges
- ✓ Enable smart sampling
- ✓ Increase minimum days at destination (filters out more combinations)

### "Time filter shows no results"
- ✓ Your time restrictions may be too narrow
- ✓ Try expanding the acceptable time ranges
- ✓ Check if flights on that route typically operate during excluded hours

### Slow searches
- ✓ Normal for date range searches (multiple API calls)
- ✓ Expect ~1-2 seconds per date combination
- ✓ 20 combinations = ~30-40 seconds
- ✓ Use smart sampling for large ranges

## Example Workflows

### Example 1: Weekend Getaway
```
Mode: Single Date
From: ZRH
To: LIS
Departure: Friday, Nov 29
Return: Sunday, Dec 1
Adults: 2

After results:
- Filter departure: 14:00-20:00 (afternoon flights)
- Filter arrival: 8:00-23:00 (no very early arrivals)
```

### Example 2: Flexible Week Vacation
```
Mode: Flexible Dates
From: ZRH
To: BCN
Departure Range: Dec 10-15 (6 days)
Return Range: Dec 17-22 (6 days)
Duration: Fixed duration (7 days)
Adults: 1

Smart sampling: Enabled
After results:
- View heatmap to find cheapest date combo
- Apply time filters if needed
```

### Example 3: Long Vacation Hunt
```
Mode: Flexible Dates
From: LHR
To: JFK
Departure Range: Jan 5-10
Return Range: Jan 20-30
Duration: Maximum days possible
Minimum stay: 10 days
Adults: 2

After results:
- Results show longest trips first
- Compare 14-day vs 10-day prices
- Filter for convenient flight times
```

## Next Steps

Want more features? Check out:
- `NEXT_STEPS.md` - Roadmap for flight tracking, price alerts
- `FEATURE_DATE_RANGE.md` - Technical details on date range search
- `FEATURE_TRIP_PREFERENCES.md` - Deep dive into duration and time filtering
- `TODO.md` - Planned features and improvements

## Support

Having issues? 
1. Check the troubleshooting section above
2. Review documentation files
3. Check Amadeus API dashboard for quota/status
4. Verify `.env` configuration
