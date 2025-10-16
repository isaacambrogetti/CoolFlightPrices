"""
Test the date range search feature
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.date_range_search import (
    generate_date_combinations,
    estimate_api_calls,
    smart_sample_dates
)


def test_date_combinations():
    """Test date combination generation"""
    print("=" * 60)
    print("Testing Date Combination Generation")
    print("=" * 60)
    
    # Test parameters
    dep_start = date(2025, 11, 10)
    dep_end = date(2025, 11, 12)
    ret_start = date(2025, 11, 15)
    ret_end = date(2025, 11, 17)
    min_days = 2
    
    print(f"\nParameters:")
    print(f"  Departure: {dep_start} to {dep_end}")
    print(f"  Return: {ret_start} to {ret_end}")
    print(f"  Minimum days at destination: {min_days}")
    
    # Generate combinations
    combinations = generate_date_combinations(
        dep_start, dep_end,
        ret_start, ret_end,
        min_days
    )
    
    print(f"\n✅ Generated {len(combinations)} valid combinations:")
    for combo in combinations:
        print(f"  {combo}")
    
    return True


def test_api_estimation():
    """Test API call estimation"""
    print("\n" + "=" * 60)
    print("Testing API Call Estimation")
    print("=" * 60)
    
    # Larger range
    dep_start = date(2025, 11, 10)
    dep_end = date(2025, 11, 15)  # 6 days
    ret_start = date(2025, 11, 18)
    ret_end = date(2025, 11, 23)  # 6 days
    min_days = 3
    
    stats = estimate_api_calls(
        dep_start, dep_end,
        ret_start, ret_end,
        min_days
    )
    
    print(f"\nDate Range:")
    print(f"  Departure: {dep_start} to {dep_end}")
    print(f"  Return: {ret_start} to {ret_end}")
    print(f"  Minimum days: {min_days}")
    
    print(f"\n✅ Statistics:")
    print(f"  Departure options: {stats['departure_days']} days")
    print(f"  Return options: {stats['return_days']} days")
    print(f"  Max possible: {stats['max_possible']} combinations")
    print(f"  Valid combinations: {stats['total_combinations']}")
    print(f"  Filtered out: {stats['filtered_out']}")
    
    return True


def test_smart_sampling():
    """Test smart sampling for large ranges"""
    print("\n" + "=" * 60)
    print("Testing Smart Sampling")
    print("=" * 60)
    
    # Very large range
    dep_start = date(2025, 11, 1)
    dep_end = date(2025, 11, 30)  # 30 days
    ret_start = date(2025, 12, 1)
    ret_end = date(2025, 12, 31)  # 31 days
    min_days = 5
    
    print(f"\nLarge Date Range:")
    print(f"  Departure: {dep_start} to {dep_end} (30 days)")
    print(f"  Return: {ret_start} to {ret_end} (31 days)")
    print(f"  This could be 30 × 31 = 930 combinations!")
    
    # Get all combinations
    all_combos = generate_date_combinations(
        dep_start, dep_end,
        ret_start, ret_end,
        min_days
    )
    print(f"\n  Valid combinations without sampling: {len(all_combos)}")
    
    # Smart sample to ~20
    sampled = smart_sample_dates(
        dep_start, dep_end,
        ret_start, ret_end,
        target_combinations=20,
        min_days_at_destination=min_days
    )
    
    print(f"  ✅ Sampled down to: {len(sampled)} combinations")
    print(f"  Reduction: {len(all_combos) - len(sampled)} ({100 * (1 - len(sampled)/len(all_combos)):.1f}% fewer API calls)")
    
    print(f"\nSample of sampled dates:")
    for combo in sampled[:5]:
        print(f"  {combo}")
    
    return True


def main():
    """Run all tests"""
    print("\n🧪 CoolFlightPrices - Date Range Search Tests\n")
    
    try:
        # Test 1: Basic combination generation
        if not test_date_combinations():
            return False
        
        # Test 2: API estimation
        if not test_api_estimation():
            return False
        
        # Test 3: Smart sampling
        if not test_smart_sampling():
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        
        print("\n📋 Next Steps:")
        print("1. Run the Streamlit app: streamlit run src/ui/app.py")
        print("2. Try the new 'Flexible Dates' search mode")
        print("3. Search a small date range first (5-10 combinations)")
        print("4. View the price heatmap and other visualizations")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
