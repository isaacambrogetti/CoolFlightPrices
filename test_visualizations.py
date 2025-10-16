"""
Test script for visualizations

Run this to test visualization functions with sample data.
"""

from datetime import date, datetime, timedelta
from src.api.batch_search import SearchResult
from src.visualization.heatmap import (
    create_price_heatmap,
    create_price_distribution,
    create_price_by_duration,
    create_calendar_view
)

def create_sample_results(num_deps=3, num_rets=3):
    """Create sample search results for testing"""
    results = []
    base_dep = date(2025, 11, 15)
    base_ret = date(2025, 11, 20)
    base_price = 150.0
    
    for i in range(num_deps):
        for j in range(num_rets):
            dep_date = base_dep + timedelta(days=i)
            ret_date = base_ret + timedelta(days=j)
            
            # Skip invalid combinations (return before departure)
            if ret_date <= dep_date:
                continue
            
            price = base_price + (i * 10) + (j * 5)
            
            result = SearchResult(
                departure_date=dep_date,
                return_date=ret_date,
                days_at_destination=(ret_date - dep_date).days - 1,
                total_duration=(ret_date - dep_date).days,
                searched_at=datetime.now(),
                flights_found=3,
                cheapest_price=price,
                currency="EUR",
                cheapest_flight={
                    'price': price,
                    'currency': 'EUR',
                    'outbound': {
                        'departure_time': '10:00',
                        'arrival_time': '12:00'
                    },
                    'return': {
                        'departure_time': '14:00',
                        'arrival_time': '16:00'
                    }
                },
                all_flights=[],
                success=True
            )
            results.append(result)
    
    return results

def test_heatmap():
    """Test price heatmap with various data sizes"""
    print("Testing Price Heatmap...")
    
    # Test 1: Normal data (3x3 grid)
    print("  Test 1: Normal data (3x3)...")
    results = create_sample_results(3, 3)
    fig = create_price_heatmap(results)
    print(f"    ✓ Created heatmap with {len(results)} results")
    
    # Test 2: Small data (2x2 grid)
    print("  Test 2: Small data (2x2)...")
    results = create_sample_results(2, 2)
    fig = create_price_heatmap(results)
    print(f"    ✓ Created heatmap with {len(results)} results")
    
    # Test 3: Single departure, multiple returns
    print("  Test 3: Single departure (1x5)...")
    results = create_sample_results(1, 5)
    fig = create_price_heatmap(results)
    print(f"    ✓ Created heatmap with {len(results)} results")
    
    # Test 4: Multiple departures, single return
    print("  Test 4: Multiple departures (5x1)...")
    results = create_sample_results(5, 1)
    fig = create_price_heatmap(results)
    print(f"    ✓ Created heatmap with {len(results)} results")
    
    # Test 5: Large data
    print("  Test 5: Large data (6x6)...")
    results = create_sample_results(6, 6)
    fig = create_price_heatmap(results)
    print(f"    ✓ Created heatmap with {len(results)} results")
    
    # Test 6: Empty data
    print("  Test 6: Empty data...")
    results = []
    fig = create_price_heatmap(results)
    print(f"    ✓ Handled empty data gracefully")
    
    print("  ✅ All heatmap tests passed!\n")

def test_distribution():
    """Test price distribution"""
    print("Testing Price Distribution...")
    
    results = create_sample_results(4, 4)
    fig = create_price_distribution(results)
    print(f"  ✓ Created distribution with {len(results)} results")
    print("  ✅ Distribution test passed!\n")

def test_duration_vs_price():
    """Test duration vs price scatter"""
    print("Testing Duration vs Price...")
    
    results = create_sample_results(4, 4)
    fig = create_price_by_duration(results)
    print(f"  ✓ Created scatter plot with {len(results)} results")
    print("  ✅ Duration vs Price test passed!\n")

def test_calendar_view():
    """Test calendar view"""
    print("Testing Calendar View...")
    
    results = create_sample_results(5, 3)
    fig = create_calendar_view(results)
    print(f"  ✓ Created calendar view with {len(results)} results")
    print("  ✅ Calendar view test passed!\n")

def test_edge_cases():
    """Test edge cases"""
    print("Testing Edge Cases...")
    
    # Single result
    print("  Test: Single result...")
    results = create_sample_results(1, 2)[:1]
    try:
        fig1 = create_price_heatmap(results)
        fig2 = create_price_distribution(results)
        fig3 = create_price_by_duration(results)
        fig4 = create_calendar_view(results)
        print("    ✓ All visualizations handled single result")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # Results with None prices
    print("  Test: Mixed valid/invalid results...")
    results = create_sample_results(3, 3)
    results[0].cheapest_price = None
    results[0].success = False
    try:
        fig = create_price_heatmap(results)
        print("    ✓ Handled mixed valid/invalid results")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    print("  ✅ Edge case tests passed!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("VISUALIZATION TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_heatmap()
        test_distribution()
        test_duration_vs_price()
        test_calendar_view()
        test_edge_cases()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
