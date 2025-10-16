"""
Batch Flight Search Module

Search flights for multiple date combinations with rate limiting and progress tracking.
"""

from typing import List, Dict, Callable, Optional
from datetime import date, datetime
import time
from dataclasses import dataclass, asdict

from src.api.amadeus_client import AmadeusClient
from src.api.rate_limiter import RateLimiter
from src.api.date_range_search import DateCombination


@dataclass
class SearchResult:
    """Result of a single date combination search"""
    
    departure_date: date
    return_date: date
    days_at_destination: int
    total_duration: int
    searched_at: datetime
    
    # Flight data
    flights_found: int
    cheapest_price: Optional[float]
    currency: Optional[str]
    cheapest_flight: Optional[Dict]
    
    # All flights for this combination
    all_flights: List[Dict]
    
    # Error handling
    error: Optional[str] = None
    success: bool = True
    
    # Airport route info (optional, for multi-airport searches)
    origin: Optional[str] = None
    destination: Optional[str] = None
    
    def to_dict(self):
        """Convert to dictionary for easy serialization"""
        result = asdict(self)
        # Convert dates to ISO format
        result['departure_date'] = self.departure_date.isoformat()
        result['return_date'] = self.return_date.isoformat()
        result['searched_at'] = self.searched_at.isoformat()
        return result


class BatchFlightSearch:
    """
    Perform batch flight searches across multiple date combinations.
    
    Features:
    - Rate limiting to respect API quotas
    - Progress tracking with callbacks
    - Error handling per search
    - Result aggregation and sorting
    """
    
    def __init__(
        self,
        client: AmadeusClient,
        calls_per_minute: int = 10,
        calls_per_hour: int = 100
    ):
        """
        Initialize batch search
        
        Args:
            client: Amadeus API client
            calls_per_minute: Rate limit for API calls per minute
            calls_per_hour: Rate limit for API calls per hour
        """
        self.client = client
        self.rate_limiter = RateLimiter(
            calls_per_minute=calls_per_minute,
            calls_per_hour=calls_per_hour
        )
    
    def search_date_range(
        self,
        origin: str,
        destination: str,
        date_combinations: List[DateCombination],
        adults: int = 1,
        max_results_per_date: int = 3,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        currency: str = "EUR"
    ) -> List[SearchResult]:
        """
        Search flights for multiple date combinations.
        
        Args:
            origin: Origin airport code (e.g., 'ZRH')
            destination: Destination airport code (e.g., 'LIS')
            date_combinations: List of DateCombination objects to search
            adults: Number of adult passengers
            max_results_per_date: Max flight options to return per date combination
            progress_callback: Function(current, total, message) called for progress updates
            currency: Currency code for prices
            
        Returns:
            List of SearchResult objects, sorted by cheapest price
        """
        results = []
        total = len(date_combinations)
        
        print(f"\n🔍 Starting batch search for {total} date combinations...")
        print(f"   Route: {origin} → {destination}")
        print(f"   Passengers: {adults} adult(s)\n")
        
        for i, combo in enumerate(date_combinations, 1):
            # Rate limiting - wait if needed
            self.rate_limiter.wait_if_needed()
            
            # Progress update
            if progress_callback:
                progress_callback(
                    i, total,
                    f"Searching {combo.departure.strftime('%b %d')} → {combo.return_date.strftime('%b %d')}"
                )
            
            try:
                # Search flights for this date combination
                flights = self.client.get_cheapest_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=combo.departure,
                    return_date=combo.return_date,
                    adults=adults,
                    max_results=max_results_per_date,
                    currency=currency
                )
                
                # Create result
                if flights:
                    result = SearchResult(
                        departure_date=combo.departure,
                        return_date=combo.return_date,
                        days_at_destination=combo.days_at_destination,
                        total_duration=combo.total_duration,
                        searched_at=datetime.now(),
                        flights_found=len(flights),
                        cheapest_price=flights[0]['price'],
                        currency=flights[0]['currency'],
                        cheapest_flight=flights[0],
                        all_flights=flights,
                        success=True
                    )
                else:
                    # No flights found
                    result = SearchResult(
                        departure_date=combo.departure,
                        return_date=combo.return_date,
                        days_at_destination=combo.days_at_destination,
                        total_duration=combo.total_duration,
                        searched_at=datetime.now(),
                        flights_found=0,
                        cheapest_price=None,
                        currency=currency,
                        cheapest_flight=None,
                        all_flights=[],
                        success=True,
                        error="No flights found for this date"
                    )
                
                results.append(result)
                
                # Small delay for visual feedback
                time.sleep(0.1)
                
            except Exception as e:
                # Handle errors gracefully
                error_msg = str(e)
                print(f"❌ Error searching {combo.departure} → {combo.return_date}: {error_msg}")
                
                result = SearchResult(
                    departure_date=combo.departure,
                    return_date=combo.return_date,
                    days_at_destination=combo.days_at_destination,
                    total_duration=combo.total_duration,
                    searched_at=datetime.now(),
                    flights_found=0,
                    cheapest_price=None,
                    currency=currency,
                    cheapest_flight=None,
                    all_flights=[],
                    success=False,
                    error=error_msg
                )
                
                results.append(result)
        
        # Sort by price (None values at end)
        results.sort(key=lambda x: (x.cheapest_price is None, x.cheapest_price or float('inf')))
        
        print(f"\n✅ Search complete! Found flights for {sum(1 for r in results if r.success and r.flights_found > 0)}/{total} combinations\n")
        
        return results
    
    def get_best_deals(
        self,
        results: List[SearchResult],
        top_n: int = 5
    ) -> List[SearchResult]:
        """
        Get the best deals from search results.
        
        Args:
            results: List of SearchResult objects
            top_n: Number of best deals to return
            
        Returns:
            List of top N cheapest SearchResult objects
        """
        # Filter out errors and no-flight results
        valid_results = [r for r in results if r.success and r.cheapest_price is not None]
        
        # Sort by price
        valid_results.sort(key=lambda x: x.cheapest_price)
        
        return valid_results[:top_n]
    
    def get_statistics(self, results: List[SearchResult]) -> Dict:
        """
        Calculate statistics from search results.
        
        Returns:
            Dictionary with statistics about the search results
        """
        valid_results = [r for r in results if r.success and r.cheapest_price is not None]
        
        if not valid_results:
            return {
                'total_searches': len(results),
                'successful_searches': 0,
                'failed_searches': len(results),
                'no_flights_found': 0,
                'avg_price': None,
                'min_price': None,
                'max_price': None,
                'price_range': None
            }
        
        prices = [r.cheapest_price for r in valid_results]
        
        return {
            'total_searches': len(results),
            'successful_searches': len(valid_results),
            'failed_searches': sum(1 for r in results if not r.success),
            'no_flights_found': sum(1 for r in results if r.success and r.flights_found == 0),
            'avg_price': sum(prices) / len(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'price_range': max(prices) - min(prices),
            'currency': valid_results[0].currency if valid_results else None
        }
