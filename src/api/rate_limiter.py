"""
Rate limiting utilities for API calls
"""

import time
from collections import deque
from datetime import datetime, timedelta
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for API calls
    
    Ensures we don't exceed API rate limits
    """
    
    def __init__(self, calls_per_minute: int = 10, calls_per_hour: Optional[int] = None):
        """
        Initialize rate limiter
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
            calls_per_hour: Maximum calls allowed per hour (optional)
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        
        self.minute_calls = deque()
        self.hour_calls = deque()
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        now = datetime.now()
        
        # Clean old calls
        self._clean_old_calls(now)
        
        # Check minute limit
        if len(self.minute_calls) >= self.calls_per_minute:
            oldest_call = self.minute_calls[0]
            wait_time = 60 - (now - oldest_call).total_seconds()
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self._clean_old_calls(datetime.now())
        
        # Check hour limit
        if self.calls_per_hour and len(self.hour_calls) >= self.calls_per_hour:
            oldest_call = self.hour_calls[0]
            wait_time = 3600 - (now - oldest_call).total_seconds()
            if wait_time > 0:
                print(f"Hourly rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self._clean_old_calls(datetime.now())
        
        # Record this call
        now = datetime.now()
        self.minute_calls.append(now)
        if self.calls_per_hour:
            self.hour_calls.append(now)
    
    def _clean_old_calls(self, now: datetime):
        """Remove calls older than the time windows"""
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        while self.minute_calls and self.minute_calls[0] < minute_ago:
            self.minute_calls.popleft()
        
        while self.hour_calls and self.hour_calls[0] < hour_ago:
            self.hour_calls.popleft()
