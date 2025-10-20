# Open-Jaw Bug Fixes

## Issues Identified

### 1. **Open-Jaw Not Working - Root Cause**
**Problem:** The open-jaw feature was implemented but results were showing only closed-jaw (traditional roundtrip) flights.

**Root Cause:** Missing validation that open-jaw mode requires a roundtrip booking with a return date. The checkbox could be enabled even for one-way trips, causing the route generation to fail silently.

**Fix Applied:**
- Added validation after `return_date` is defined: if `allow_open_jaw` is enabled but `return_date` is `None`, show error and stop
- Updated route generation condition from `if allow_open_jaw and multi_airport:` to `if allow_open_jaw and multi_airport and return_date:`
- This ensures open-jaw routes are only generated when we have both a departure and return date

### 2. **Top 5 Best Deals Missing Return Route**
**Problem:** The Top 5 Best Deals section showed only the outbound airline info in the title, not the complete route including return direction.

**Example Before:**
```
#1: 🔀 EUR 165.48 - LX 1234 (Cheapest!)
```

**Example After:**
```
#1: 🔀 EUR 165.48 - ZRH→LIS / OPO→ZRH (Cheapest!)
```

**Fix Applied:**
- Extracted outbound route: `origin→destination`
- Extracted return route (if exists): `origin→destination`
- Combined into display format: `outbound / return`
- Removed airline info from title (still visible in expanded details)

## Code Changes

### `src/ui/app.py`

**Change 1: Validation for Open-Jaw**
```python
# Lines 1410-1415 (NEW)
if search_button:
    # Validate open-jaw requirements
    if allow_open_jaw and not return_date:
        st.error("🔀 Open-jaw flights require a roundtrip booking. Please select a return date or disable open-jaw mode.")
        st.stop()
```

**Change 2: Route Generation Condition**
```python
# Line 1420 (UPDATED)
# Before:
if allow_open_jaw and multi_airport:

# After:
if allow_open_jaw and multi_airport and return_date:
```

**Change 3: Top 5 Display Format**
```python
# Lines 503-515 (UPDATED)
for i, flight in enumerate(sorted_flights, 1):
    open_jaw_badge = "🔀 " if flight.get('is_open_jaw', False) else ""
    
    # Build route description
    outbound_route = f"{flight['outbound']['origin']}→{flight['outbound']['destination']}"
    if flight.get('return'):
        return_route = f"{flight['return']['origin']}→{flight['return']['destination']}"
        route_display = f"{outbound_route} / {return_route}"
    else:
        route_display = outbound_route
    
    with st.expander(
        f"#{i}: {open_jaw_badge}{flight['currency']} {flight['price']:.2f} - {route_display}"
        f"{' (Cheapest!)' if i == 1 else ''}",
        expanded=(i <= 2)
    ):
```

## Testing Checklist

To verify the fixes work:

1. **Test Open-Jaw with Roundtrip:**
   - ✅ Enable "Compare multiple airports"
   - ✅ Select 2+ origins (e.g., ZRH, GVA)
   - ✅ Select 2+ destinations (e.g., LIS, OPO)
   - ✅ Choose "📅 Single Date" mode
   - ✅ Select "Roundtrip" trip type
   - ✅ Set departure and return dates
   - ✅ Enable "🔀 Allow different return airports (open-jaw)"
   - ✅ Click "🔍 Search Flights"
   - **Expected:** Should see results with 🔀 badge and mixed routes like "ZRH→LIS / OPO→ZRH"

2. **Test Open-Jaw with One-Way (Should Fail):**
   - Enable "Compare multiple airports"
   - Select multiple airports
   - Choose "📅 Single Date" mode
   - Select "One-way" trip type
   - Enable "🔀 Allow different return airports (open-jaw)"
   - Click "🔍 Search Flights"
   - **Expected:** Error message: "🔀 Open-jaw flights require a roundtrip booking..."

3. **Test Top 5 Display:**
   - Run any search with results
   - Check "🏆 Top 5 Best Deals" section
   - **Expected:** Each item shows format like "#1: EUR 165.48 - ZRH→LIS / OPO→ZRH"
   - For one-way flights: "#1: EUR 100.00 - ZRH→LIS"

## Commit Information

- **Branch:** `open-jaw-flights`
- **Commit Hash:** `1f16a08`
- **Commit Message:**
  ```
  Fix: Add validation for open-jaw requiring roundtrip + Show return route in Top 5 Best Deals
  
  - Added validation to ensure open-jaw mode requires a return date (roundtrip)
  - Added explicit check: return_date must exist for open-jaw route generation
  - Updated Top 5 Best Deals display to show both outbound and return routes
  - Format: 'ZRH→LIS / OPO→ZRH' instead of just airline info
  - Open-jaw badge (🔀) preserved in display
  ```

## Next Steps

1. **Test the fixes:**
   - Run the app: `streamlit run src/ui/app.py`
   - Follow testing checklist above
   - Verify open-jaw results appear correctly
   - Verify validation works for one-way trips

2. **If tests pass:**
   - Merge `open-jaw-flights` branch to `main`
   - Delete feature branch
   - Update documentation if needed

3. **If issues persist:**
   - Check API quota (open-jaw uses multi-city endpoint)
   - Verify Amadeus credentials
   - Check terminal output for error messages
   - Review API response structure
