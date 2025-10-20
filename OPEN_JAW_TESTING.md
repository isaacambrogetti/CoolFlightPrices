# Open-Jaw Testing & Debugging Summary

## Current Status

### Changes Implemented

1. **Debug Output Added** (Line ~1433):
   - Shows `allow_open_jaw`, `multi_airport`, and `return_date` values when open-jaw is enabled
   - Shows info message when generating open-jaw route combinations
   - Will help identify why routes aren't being generated as open-jaw

2. **Caption Display Fixed** (Line ~1619):
   - Now handles both open-jaw (dict) and normal (tuple) formats
   - Prevents crashes when displaying route summaries

3. **Flexible Dates Top 5 Enhanced** (Line ~1003):
   - Shows both outbound and return routes: `ZRH→LIS / OPO→ZRH`
   - Includes search route label in brackets: `[ZRH-LIS]`

4. **Multi-Airport Results Order Changed** (Line ~835):
   - **New Order**: Statistics → **Top 5 Best Deals** → Visualizations
   - User can see best deals immediately without scrolling past charts

## Testing Plan

### Test 1: Open-Jaw Single Date Search

**Steps:**
1. Start app: `streamlit run src/ui/app.py`
2. In sidebar:
   - Select "📅 Single Date" mode
   - Enable "Compare multiple airports"
   - Origins: `ZRH, GVA` (2 airports)
   - Destinations: `LIS, OPO` (2 airports)
   - Trip Type: **Roundtrip** (required!)
   - Set departure date: e.g., Nov 18, 2025
   - Set return date: e.g., Nov 28, 2025
   - Enable "🔀 Allow different return airports (open-jaw)"
3. Click "🔍 Search Flights"

**Expected Results:**
- Debug output should show:
  - `🔍 DEBUG: allow_open_jaw=True, multi_airport=True, return_date=<date>`
  - `✅ Generating 2×2 open-jaw route combinations...`
- Results should include open-jaw flights with 🔀 badge:
  - `ZRH→LIS / OPO→ZRH`
  - `GVA→OPO / LIS→ZRH`
  - etc.

**If It Fails:**
- Check debug output values
- Verify `allow_open_jaw` is actually `True`
- Verify `multi_airport` is `True`
- Verify `return_date` is not `None`
- Check terminal logs for errors

### Test 2: Open-Jaw with One-Way (Should Error)

**Steps:**
1. Same setup as Test 1
2. But select "One-way" trip type
3. Try to enable open-jaw checkbox (should still appear)
4. Click search

**Expected Results:**
- Error message: "🔀 Open-jaw flights require a roundtrip booking. Please select a return date or disable open-jaw mode."
- Search should stop

### Test 3: Flexible Dates Top 5 Display

**Steps:**
1. Select "💡 Flexible Dates (Date Range)" mode
2. Enable "Compare multiple airports"
3. Select 2+ origins and 2+ destinations
4. Set date range (e.g., Nov 15-20 departure, Nov 25-30 return)
5. Search

**Expected Results:**
- Top 5 Best Deals titles should show:
  - `#1: EUR 165.48 - ZRH→LIS / LIS→ZRH [ZRH-LIS] (Cheapest!)`
  - Format includes both outbound and return routes

### Test 4: Single Date Multi-Airport Top 5 Order

**Steps:**
1. Select "📅 Single Date" mode
2. Enable "Compare multiple airports"
3. Select 2+ airports for origin and destination
4. **Do NOT enable open-jaw** (test normal mode)
5. Search

**Expected Results:**
- Results page shows in order:
  1. Statistics (4 metrics)
  2. **🏆 Top 5 Best Deals**
  3. 📊 Route Comparison Analysis (visualizations)
- Top 5 should appear BEFORE the charts

## Debugging Checklist

If open-jaw still doesn't work:

- [ ] Check if `allow_open_jaw` checkbox is visible in sidebar
- [ ] Verify checkbox is checked (value should be True)
- [ ] Check if debug output appears when clicking search
- [ ] Verify debug shows `allow_open_jaw=True`
- [ ] Verify `return_date` is not `None`
- [ ] Check terminal logs for API errors
- [ ] Verify `airport_routes` format in debug
- [ ] Check if `is_open_jaw_mode` is True (line ~1624)
- [ ] Verify multi-city API is being called (should see different spinner text)

## Known Issues

1. **Open-Jaw Not Working**: Routes are still being generated as closed-jaw (same airport pairs)
   - **Status**: Investigating with debug output
   - **Next Step**: Test with debug enabled to see values

2. **Potential Root Causes**:
   - `allow_open_jaw` variable scope issue?
   - Checkbox value not being captured?
   - Condition at line 1430 evaluating to False?
   - Session state issue?

## Files Modified

- `src/ui/app.py`: Main changes
  - Line ~1433: Debug output
  - Line ~1619: Caption format handling
  - Line ~835: Top 5 moved before visualizations
  - Line ~1003: Flexible dates Top 5 format

- `OPEN_JAW_FIXES.md`: Documentation of previous fixes

## Next Actions

1. **Run Test 1** with debug output enabled
2. **Analyze** the debug values shown
3. **Fix** the root cause based on findings
4. **Remove** debug output once working
5. **Test** all scenarios
6. **Merge** to main if successful
