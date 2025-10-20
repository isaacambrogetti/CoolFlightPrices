# Open-Jaw Investigation & View All Flights Update

## Changes Made

### 1. 🔍 Enhanced Debug Output for Open-Jaw

Added comprehensive debugging at TWO critical points:

**A. At the Checkbox (Line ~1374):**
```python
st.write(f"🔍 DEBUG (checkbox): allow_open_jaw set to {allow_open_jaw}")
```
This shows the value RIGHT when the checkbox is set.

**B. At the Search Button (Line ~1439):**
```python
st.write(f"🔍 DEBUG: allow_open_jaw={allow_open_jaw}, multi_airport={multi_airport}, return_date={return_date}, search_mode={search_mode}")
st.write(f"🔍 DEBUG: Condition result: {allow_open_jaw and multi_airport and return_date}")
```
This shows ALL condition values and the final boolean result.

### 2. ✅ Updated "View All Flights" Table Format

**Changed from:** Pandas DataFrame with columns: Route, Price, Currency, Outbound, Departure, Return, Stops, Seats

**Changed to:** Column layout (matching flexible date format) with:
- **Route**: Search route label
- **Departure Direction**: Origin → Destination
- **Return Direction**: Origin → Destination (or "One-way")
- **Airline**: Airline code + flight number
- **Price**: Bold price
- **Curr.**: Currency
- **Track**: Track price button

Now **both single date and flexible date** use the same visual format!

## Testing Instructions

### Test Open-Jaw with Debug Output

1. **Start the app** (should already be running at http://localhost:8501)

2. **Setup:**
   - Select "📅 Single Date" mode
   - Enable "Compare multiple airports"
   - Enter origins: `ZRH, GVA`
   - Enter destinations: `LIS, OPO`
   - Select "Roundtrip"
   - Set departure date: Nov 18, 2025
   - Set return date: Nov 28, 2025

3. **Enable open-jaw:**
   - Check the "🔀 Allow different return airports (open-jaw)" checkbox
   - **LOOK FOR DEBUG OUTPUT** right below the checkbox:
     ```
     🔍 DEBUG (checkbox): allow_open_jaw set to True
     ```

4. **Click "🔍 Search Flights"**

5. **Check debug output at top of results:**
   ```
   🔍 DEBUG: allow_open_jaw=True, multi_airport=True, return_date=2025-11-28, search_mode=📅 Single Date
   🔍 DEBUG: Condition result: True
   ```

6. **Expected behavior:**
   - If condition is `True`, you should see:
     ```
     ✅ Generating 2×2 open-jaw route combinations...
     ```
   - Results should show 🔀 badge with mixed routes like "ZRH→LIS / OPO→ZRH"

7. **If condition is `False`:**
   - Check which value is wrong:
     - `allow_open_jaw` should be `True`
     - `multi_airport` should be `True`
     - `return_date` should NOT be `None`
     - `search_mode` should be `"📅 Single Date"`

### Test View All Flights Table

1. **Run any multi-airport search** (with or without open-jaw)

2. **Scroll down** past Top 5 and visualizations

3. **Expand "📋 View All Flights"**

4. **Verify format:**
   - Should show columns: Route | Departure Direction | Return Direction | Airline | Price | Curr. | Track
   - Each row should have clear direction arrows: `ZRH → LIS` and `LIS → ZRH`
   - Should look similar to flexible date "📋 View All Results"

## What to Report

### If Open-Jaw Still Doesn't Work:

Please screenshot or copy the **DEBUG output** you see:
1. The debug line below the checkbox
2. The two debug lines after clicking search
3. Any error messages

This will tell us exactly which condition is failing.

### If Open-Jaw Works:

Great! Let me know and I'll remove the debug output and prepare for merge.

### Possible Issues & Solutions:

**Issue 1: Checkbox doesn't appear**
- Check that both "Compare multiple airports" AND "📅 Single Date" are selected
- The checkbox only appears when BOTH conditions are met

**Issue 2: `allow_open_jaw=False` even when checked**
- This would indicate a Streamlit state issue
- Try refreshing the page (F5) and testing again

**Issue 3: `return_date=None` even with roundtrip selected**
- Verify "Roundtrip" is selected (not "One-way")
- Check that a return date is actually set

**Issue 4: Routes still closed-jaw despite condition=True**
- This would mean the route generation logic needs fixing
- But we need to confirm condition is True first

## Files Modified

- `src/ui/app.py`:
  - Line ~1374: Debug output at checkbox
  - Line ~1439-1440: Debug output at search button
  - Line ~1050-1099: Updated View All Flights table format

## Next Steps

1. **Test now** and check the debug output
2. **Report findings** - which values are shown in debug?
3. **Fix root cause** based on debug information
4. **Remove debug** once working
5. **Test all scenarios** (open-jaw, flexible dates, single date)
6. **Merge to main** if all tests pass
