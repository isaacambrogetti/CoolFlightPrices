"""
Date Range Search Module

Generate and manage date combinations for flexible flight searches.
"""

from datetime import date, timedelta
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class DateCombination:
    """Represents a valid departure/return date combination"""
    
    departure: date
    return_date: date
    
    @property
    def days_at_destination(self) -> int:
        """
        Calculate full days at destination.
        Arrival day and departure day don't count as full days.
        """
        return (self.return_date - self.departure).days - 1
    
    @property
    def total_duration(self) -> int:
        """Total trip duration in days"""
        return (self.return_date - self.departure).days
    
    def __str__(self):
        return (f"{self.departure.strftime('%b %d')} → {self.return_date.strftime('%b %d')} "
                f"({self.total_duration} days, {self.days_at_destination} days there)")


def generate_date_combinations(
    departure_start: date,
    departure_end: date,
    return_start: date,
    return_end: date,
    min_days_at_destination: int = 0,
    max_combinations: int = None
) -> List[DateCombination]:
    """
    Generate all valid date combinations within specified ranges.
    
    Args:
        departure_start: Earliest possible departure date
        departure_end: Latest possible departure date
        return_start: Earliest possible return date
        return_end: Latest possible return date
        min_days_at_destination: Minimum full days required at destination
        max_combinations: Maximum number of combinations to generate (None = no limit)
        
    Returns:
        List of DateCombination objects sorted by departure date then return date
        
    Example:
        >>> from datetime import date
        >>> combos = generate_date_combinations(
        ...     departure_start=date(2025, 11, 10),
        ...     departure_end=date(2025, 11, 12),
        ...     return_start=date(2025, 11, 15),
        ...     return_end=date(2025, 11, 17),
        ...     min_days_at_destination=2
        ... )
        >>> len(combos)
        9
    """
    combinations = []
    
    # Validate inputs
    if departure_start > departure_end:
        raise ValueError("Departure start date must be before or equal to end date")
    if return_start > return_end:
        raise ValueError("Return start date must be before or equal to end date")
    if return_start < departure_start:
        raise ValueError("Return date range must be after departure date range")
    
    current_dep = departure_start
    while current_dep <= departure_end:
        current_ret = return_start
        
        while current_ret <= return_end:
            # Skip if return is before or same as departure
            if current_ret <= current_dep:
                current_ret += timedelta(days=1)
                continue
            
            # Calculate days at destination
            # Days between - 1 (arrival and departure days don't count)
            days_at_dest = (current_ret - current_dep).days - 1
            
            # Check minimum stay requirement
            if days_at_dest >= min_days_at_destination:
                combinations.append(DateCombination(
                    departure=current_dep,
                    return_date=current_ret
                ))
                
                # Check max combinations limit
                if max_combinations and len(combinations) >= max_combinations:
                    return combinations
            
            current_ret += timedelta(days=1)
        current_dep += timedelta(days=1)
    
    return combinations


def estimate_api_calls(
    departure_start: date,
    departure_end: date,
    return_start: date,
    return_end: date,
    min_days_at_destination: int = 0
) -> dict:
    """
    Estimate number of API calls and provide statistics.
    
    Returns:
        Dictionary with:
        - 'total_combinations': Total valid date combinations
        - 'departure_days': Number of departure date options
        - 'return_days': Number of return date options
        - 'max_possible': Maximum possible combinations (without filtering)
    """
    departure_days = (departure_end - departure_start).days + 1
    return_days = (return_end - return_start).days + 1
    max_possible = departure_days * return_days
    
    # Generate to count valid ones
    combinations = generate_date_combinations(
        departure_start, departure_end,
        return_start, return_end,
        min_days_at_destination
    )
    
    return {
        'total_combinations': len(combinations),
        'departure_days': departure_days,
        'return_days': return_days,
        'max_possible': max_possible,
        'filtered_out': max_possible - len(combinations)
    }


def smart_sample_dates(
    departure_start: date,
    departure_end: date,
    return_start: date,
    return_end: date,
    target_combinations: int = 20,
    min_days_at_destination: int = 0
) -> List[DateCombination]:
    """
    Intelligently sample date combinations when there are too many.
    
    Strategy:
    - Always include first and last dates in each range
    - Sample evenly distributed dates in between
    - Respect minimum stay requirement
    
    Args:
        departure_start, departure_end: Departure date range
        return_start, return_end: Return date range
        target_combinations: Desired number of combinations (~20 is good)
        min_days_at_destination: Minimum days at destination
        
    Returns:
        List of sampled DateCombination objects
    """
    # Calculate step sizes to get approximately target combinations
    departure_days = (departure_end - departure_start).days + 1
    return_days = (return_end - return_start).days + 1
    
    # Calculate step size (sample every N days)
    import math
    total_possible = departure_days * return_days
    
    if total_possible <= target_combinations:
        # Just return all combinations
        return generate_date_combinations(
            departure_start, departure_end,
            return_start, return_end,
            min_days_at_destination
        )
    
    # Calculate optimal step size
    step_size = max(1, int(math.sqrt(total_possible / target_combinations)))
    
    # Sample dates
    sampled_departures = []
    current = departure_start
    while current <= departure_end:
        sampled_departures.append(current)
        current += timedelta(days=step_size)
    # Always include last date
    if sampled_departures[-1] != departure_end:
        sampled_departures.append(departure_end)
    
    sampled_returns = []
    current = return_start
    while current <= return_end:
        sampled_returns.append(current)
        current += timedelta(days=step_size)
    # Always include last date
    if sampled_returns[-1] != return_end:
        sampled_returns.append(return_end)
    
    # Generate combinations from sampled dates
    combinations = []
    for dep in sampled_departures:
        for ret in sampled_returns:
            if ret > dep:
                days_at_dest = (ret - dep).days - 1
                if days_at_dest >= min_days_at_destination:
                    combinations.append(DateCombination(
                        departure=dep,
                        return_date=ret
                    ))
    
    return combinations
