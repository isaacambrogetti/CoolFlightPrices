# Visualization Error Fixes

## Issues Resolved

Fixed errors occurring in the Price Heatmap, Price Distribution, Duration vs Price, and Calendar View visualizations.

## Root Causes Identified

### 1. Data Mutation Issues
**Problem**: When applying time filters, the code was modifying `SearchResult` objects in place, which could cause:
- Inconsistent data across visualizations
- Side effects when results were reused
- Unexpected behavior when switching between filtered/unfiltered views

**Solution**: Create copies of `SearchResult` objects when filtering:
```python
from copy import copy
filtered_result = copy(result)
filtered_result.all_flights = filtered_flights
filtered_result.cheapest_price = min(f['price'] for f in filtered_flights)
```

### 2. Missing Type Validation
**Problem**: Price data wasn't being validated or converted to proper types:
- `cheapest_price` could be None, string, or numeric
- Date fields might not be properly formatted
- Missing null checks before calculations

**Solution**: Added explicit type conversion and validation:
```python
prices = [float(r.cheapest_price) for r in valid_results]
durations.append(int(r.total_duration))
prices.append(float(r.cheapest_price))
```

### 3. Edge Case Handling
**Problem**: Visualizations crashed when:
- Only 1 data point (can't create meaningful heatmap)
- All results filtered out by time preferences
- Empty results after grouping operations
- Invalid date formatting

**Solution**: Added checks for edge cases:
```python
if not data:
    fig = go.Figure()
    fig.add_annotation(
        text="No valid data for heatmap",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20)
    )
    return fig
```

### 4. Unhandled Exceptions
**Problem**: Errors in visualization code would crash the entire page:
- Pandas pivot table failures
- Plotly rendering errors
- Data type mismatches

**Solution**: Wrapped all visualization generation in try-catch blocks:
```python
with tab1:
    try:
        fig = create_price_heatmap(results)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Green = Cheaper, Red = More Expensive")
    except Exception as e:
        st.error(f"Error creating price heatmap: {str(e)}")
        st.info("Try adjusting your search parameters or time filters.")
```

## Specific Fixes by Visualization

### Price Heatmap (`create_price_heatmap`)
**Fixed**:
- ✅ Validate data before DataFrame creation
- ✅ Skip results with invalid data (missing dates, null prices)
- ✅ Handle pivot table failures (single row/column)
- ✅ Convert prices to float explicitly
- ✅ Informative error messages for edge cases

**Edge cases handled**:
- Single departure or return date (can't pivot)
- Missing price data
- Date formatting issues

### Price Distribution (`create_price_distribution`)
**Fixed**:
- ✅ Type validation for all prices
- ✅ Handle empty price lists
- ✅ Catch ValueError/TypeError exceptions
- ✅ Convert prices to float before histogram

**Edge cases handled**:
- All prices are None
- Non-numeric price values
- Single price point

### Duration vs Price (`create_price_by_duration`)
**Fixed**:
- ✅ Validate each data point individually
- ✅ Skip invalid entries (continue loop instead of crash)
- ✅ Ensure durations and prices arrays match length
- ✅ Convert durations to int, prices to float
- ✅ Handle missing or malformed dates in hover text

**Edge cases handled**:
- Mixed valid/invalid data points
- Missing duration or price fields
- Date formatting failures

### Calendar View (`create_calendar_view`)
**Fixed**:
- ✅ Convert prices to float before grouping
- ✅ Handle groupby aggregation errors
- ✅ Validate DataFrame before operations
- ✅ Catch all exceptions with informative messages

**Edge cases handled**:
- Single departure date (groupby returns 1 row)
- Duplicate dates with different prices
- Invalid date types

## Error Handling Strategy

### Three-Layer Protection

**Layer 1: Input Validation**
```python
valid_results = [r for r in results if r.success and r.cheapest_price is not None]

if not valid_results:
    # Return figure with message
    return fig
```

**Layer 2: Data Processing**
```python
try:
    prices = [float(r.cheapest_price) for r in valid_results]
    # ... process data
except (ValueError, TypeError, AttributeError) as e:
    # Return figure with error message
    return fig
```

**Layer 3: Visualization Generation**
```python
with tab1:
    try:
        fig = create_price_heatmap(results)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating price heatmap: {str(e)}")
```

## User-Facing Improvements

### Before Fixes
- ❌ Page crashes with Python traceback
- ❌ No indication of what went wrong
- ❌ Must restart application
- ❌ Lose all search results

### After Fixes
- ✅ Graceful error messages
- ✅ Other visualizations still work
- ✅ Clear explanation of issue
- ✅ Suggestions for resolution
- ✅ Can adjust filters without re-searching

## Testing Scenarios

### Recommended Test Cases

1. **Normal operation**
   - Search with 10-20 date combinations
   - All visualizations should render

2. **Edge case: Single date**
   - Search with 1 departure, 1 return date
   - Should show message: "Not enough data to create heatmap"
   - Other charts should still work

3. **Edge case: Time filter eliminates all**
   - Search flexible dates
   - Apply very restrictive time filters (e.g., 2:00-3:00)
   - Should show: "No flights match your time preferences"
   - Won't crash application

4. **Edge case: Single departure date, multiple returns**
   - Departure: Nov 15-15 (1 day)
   - Return: Nov 20-25 (6 days)
   - Heatmap might fail (expected), calendar view should work

5. **Edge case: All searches fail**
   - Invalid route (e.g., ZRH to ZZZ)
   - Should handle gracefully with empty state messages

## Performance Considerations

### Copy vs Reference
Using `copy()` for filtered results adds minimal overhead:
- `SearchResult` objects are lightweight dataclasses
- Only copied when time filters are applied
- Prevents hard-to-debug mutation issues

### Error Message Display
- Error messages shown inline, don't break page layout
- Each visualization independent - one failure doesn't cascade
- Users can continue using working features

## Known Limitations

### Pivot Table Requirements
The heatmap requires:
- At least 2 different departure dates
- At least 2 different return dates
- Otherwise shows "Not enough data" message

**Workaround**: Use other visualizations (distribution, calendar view) which work with single dates.

### Grouping Operations
Calendar view groups by departure date:
- Works fine with single date (shows 1 bar)
- Multiple dates with same prices handled correctly

## Future Improvements

Potential enhancements:
1. **Smarter fallbacks**: Show simplified version when data insufficient
2. **Data quality warnings**: Alert if many results have missing data
3. **Alternative visualizations**: Offer different chart types for edge cases
4. **Export data**: Allow CSV export even when visualizations fail
5. **Caching**: Cache visualization data to speed up filter adjustments

## Debugging Tips

### If visualizations still fail:

1. **Check browser console**: Look for JavaScript errors
2. **Verify data types**: Print result objects to check structure
3. **Test with minimal data**: Single search to isolate issue
4. **Update dependencies**: Ensure plotly, pandas are current versions
5. **Check Streamlit version**: Some features require newer versions

### Common issues:

**"No valid data for heatmap"**
- Too few date combinations (need 2x2 minimum)
- All searches failed (check API credentials)
- Time filters too restrictive

**"Error processing price data"**
- Check SearchResult structure hasn't changed
- Verify currency field is populated
- Ensure prices are numeric

**Blank visualization**
- Usually means empty results after filtering
- Check filter settings
- Try wider date ranges

## Related Files Modified

- `src/visualization/heatmap.py` - All 4 visualization functions enhanced
- `src/ui/app.py` - Time filtering logic fixed, try-catch added
- `USAGE_GUIDE.md` - Documentation created
- `FEATURE_TRIP_PREFERENCES.md` - Feature documentation

## Commit

```
commit b632970
Fix visualization errors with robust error handling

- Add try-catch blocks around all visualization generation
- Validate data before creating plots (type conversion, null checks)
- Handle edge cases (single data point, empty results after filtering)
- Create copies of SearchResult when filtering to avoid mutation
- Add informative error messages in visualizations
- Prevent crashes when time filters eliminate all results
```
