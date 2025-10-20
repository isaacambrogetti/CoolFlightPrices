# Flight Tracking ID Fix

## Issue Reported

When tracking roundtrip flights with the **same outbound flight** but **different return flights**, tracking one flight would automatically mark the other as tracked, even though they are completely different roundtrips.

### Example:
- **Flight A**: ZRH→LIS (TP 1234) / LIS→ZRH (TP 5678) - €200
- **Flight B**: ZRH→LIS (TP 1234) / OPO→ZRH (TP 9999) - €250

Tracking Flight A would incorrectly mark Flight B as tracked too, because they share the same outbound flight.

## Root Cause

The `generate_flight_id()` method in `src/price_tracking/database.py` was generating IDs based on:
- **Outbound**: origin, destination, date, airline, flight_number ✅
- **Return**: Only the departure_date ❌

This meant that two roundtrips with identical outbound flights but different return flights (different airlines, flight numbers, or even origins/destinations in open-jaw cases) would get the **same ID**.

### Old ID Format:
```
{origin}_{destination}_{dep_date}_{ret_date}_{airline}_{flight_num}
Example: ZRH_LIS_20251215_20251222_TP_1234
```

**Problem**: This only uses outbound flight details! Return flight details were missing.

## Solution

Updated `generate_flight_id()` to include **complete information** for BOTH legs:

### New ID Format:

**Roundtrip:**
```
OUT_{origin}_{destination}_{date}_{airline}_{num}_RET_{origin}_{destination}_{date}_{airline}_{num}
```

**Example (normal roundtrip):**
```
OUT_ZRH_LIS_20251215_TP_1234_RET_LIS_ZRH_20251222_TP_5678
```

**Example (open-jaw):**
```
OUT_ZRH_LIS_20251215_TP_1234_RET_OPO_ZRH_20251222_TP_9999
```

**One-way:**
```
OUT_{origin}_{destination}_{date}_{airline}_{num}_OW
Example: OUT_ZRH_LIS_20251215_TP_1234_OW
```

## What's Included Now

### Outbound (OUT) Segment:
- Origin airport
- Destination airport
- Departure date
- Airline code
- Flight number

### Return (RET) Segment:
- Origin airport (return from)
- Destination airport (return to)
- Departure date (return date)
- Airline code
- Flight number

## Why This Matters

This fix is **especially critical** for:

1. **Open-jaw flights**: Where return airports differ from outbound
   - ZRH→LIS / OPO→ZRH
   - GVA→OPO / LIS→GVA

2. **Same route, different airlines**: 
   - Outbound: Lufthansa
   - Return: Swiss

3. **Same route, different times/dates**:
   - Early morning return vs evening return

4. **Multi-airport searches**: Where users compare many combinations

## Changes Made

**File**: `src/price_tracking/database.py`

**Method**: `generate_flight_id()`

**Lines**: 62-116 (updated)

### Code Changes:
- Separated outbound and return data extraction
- Added prefix `OUT_` and `RET_` to clearly identify segments
- Included ALL flight details for both segments
- Maintained backward compatibility with one-way flights (suffix `_OW`)

## Testing

### Before Fix:
```python
flight_a = {
    'outbound': {'origin': 'ZRH', 'destination': 'LIS', 'date': '2025-12-15', 'airline': 'TP', 'flight_number': '1234'},
    'return': {'origin': 'LIS', 'destination': 'ZRH', 'date': '2025-12-22', 'airline': 'TP', 'flight_number': '5678'}
}
flight_b = {
    'outbound': {'origin': 'ZRH', 'destination': 'LIS', 'date': '2025-12-15', 'airline': 'TP', 'flight_number': '1234'},
    'return': {'origin': 'OPO', 'destination': 'ZRH', 'date': '2025-12-22', 'airline': 'TP', 'flight_number': '9999'}
}

# OLD: Both would generate: ZRH_LIS_20251215_20251222_TP_1234 ❌
# NEW: 
# Flight A: OUT_ZRH_LIS_20251215_TP_1234_RET_LIS_ZRH_20251222_TP_5678 ✅
# Flight B: OUT_ZRH_LIS_20251215_TP_1234_RET_OPO_ZRH_20251222_TP_9999 ✅
```

### After Fix:
- ✅ Each unique roundtrip gets a unique ID
- ✅ Tracking one flight doesn't affect others
- ✅ Open-jaw flights tracked correctly
- ✅ Same outbound + different returns distinguished

## Backward Compatibility

**Important**: Existing tracked flights in the database will have OLD format IDs. These will continue to work, but:
- If you track the same flight again, it will create a NEW entry with the new ID format
- Old entries can be manually cleaned up or will naturally expire

To avoid duplicates, consider:
1. Clearing tracked flights after update (if desired)
2. Or let them coexist (old format will gradually be replaced)

## Impact

- **User Experience**: ✅ Fixed! Tracking now works correctly
- **Database**: Compatible - new format coexists with old
- **Performance**: No impact - same complexity
- **API**: No changes - this is internal ID generation

## Commit

**Branch**: `open-jaw-flights`
**Commit**: `bbf72ba`
**Message**: "Fix: Include return flight details in tracking ID to distinguish different roundtrips"

## Status

✅ **FIXED** - Ready for testing and merge to main
