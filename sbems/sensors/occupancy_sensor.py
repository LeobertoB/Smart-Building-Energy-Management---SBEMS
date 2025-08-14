"""
Occupancy sensor implementation for monitoring people count and movement.
"""

import numpy as np
from typing import Tuple
from .base_sensor import BaseSensor


class OccupancySensor(BaseSensor):
    """
    Occupancy sensor for monitoring people count, movement, and presence.
    """
    
    def __init__(self, occupancy_type: str = "people_count", max_occupancy: int = 20, **kwargs):
        """
        Initialize occupancy sensor.
        
        Args:
            occupancy_type: Type of occupancy measurement (people_count, motion, presence)
            max_occupancy: Maximum expected occupancy for this area
        """
        self.occupancy_type = occupancy_type
        self.max_occupancy = max_occupancy
        super().__init__(**kwargs)
        
        # Occupancy-specific configuration
        self.motion_sensitivity = 0.8  # Motion detection sensitivity
        self.presence_timeout = 300  # Seconds before presence times out
        self.last_motion_time = None
        
    @property
    def sensor_type(self) -> str:
        return f"occupancy_{self.occupancy_type}"
    
    @property
    def unit(self) -> str:
        units = {
            "people_count": "people",
            "motion": "boolean",
            "presence": "boolean"
        }
        return units.get(self.occupancy_type, "units")
    
    @property
    def normal_range(self) -> Tuple[float, float]:
        ranges = {
            "people_count": (0.0, float(self.max_occupancy)),
            "motion": (0.0, 1.0),
            "presence": (0.0, 1.0)
        }
        return ranges.get(self.occupancy_type, (0.0, 100.0))
    
    def _read_sensor_value(self) -> float:
        """Read occupancy sensor value with realistic simulation."""
        if self.occupancy_type == "people_count":
            return self._simulate_people_count()
        elif self.occupancy_type == "motion":
            return self._simulate_motion_detection()
        elif self.occupancy_type == "presence":
            return self._simulate_presence_detection()
        else:
            return np.random.uniform(*self.normal_range)
    
    def _simulate_people_count(self) -> float:
        """Simulate realistic people count based on time and day."""
        from datetime import datetime
        
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Base occupancy patterns
        if weekday < 5:  # Weekday
            occupancy_pattern = self._get_weekday_pattern(hour)
        else:  # Weekend
            occupancy_pattern = self._get_weekend_pattern(hour)
        
        # Calculate expected occupancy
        expected_occupancy = self.max_occupancy * occupancy_pattern
        
        # Add random variation
        variation = np.random.normal(0, expected_occupancy * 0.2)
        actual_occupancy = expected_occupancy + variation
        
        # Ensure non-negative integer
        return max(0, round(actual_occupancy))
    
    def _get_weekday_pattern(self, hour: int) -> float:
        """Get occupancy pattern for weekdays (0.0 to 1.0)."""
        patterns = {
            # Early morning (6-9)
            6: 0.1, 7: 0.3, 8: 0.7, 9: 0.9,
            # Morning work (9-12)
            10: 0.95, 11: 0.9, 12: 0.7,  # Lunch dip
            # Afternoon work (13-17)
            13: 0.85, 14: 0.9, 15: 0.95, 16: 0.9, 17: 0.8,
            # Evening (18-22)
            18: 0.4, 19: 0.2, 20: 0.1, 21: 0.05, 22: 0.02,
        }
        
        # Default pattern for unlisted hours
        if hour < 6 or hour > 22:
            return 0.01  # Very low occupancy
        
        return patterns.get(hour, 0.5)
    
    def _get_weekend_pattern(self, hour: int) -> float:
        """Get occupancy pattern for weekends (0.0 to 1.0)."""
        patterns = {
            # Late morning start
            9: 0.1, 10: 0.3, 11: 0.4, 12: 0.5,
            # Afternoon activity
            13: 0.4, 14: 0.6, 15: 0.5, 16: 0.4,
            # Evening wind down
            17: 0.3, 18: 0.2, 19: 0.15, 20: 0.1,
        }
        
        if hour < 9 or hour > 20:
            return 0.05  # Low weekend occupancy
        
        return patterns.get(hour, 0.2)
    
    def _simulate_motion_detection(self) -> float:
        """Simulate motion detection (0 = no motion, 1 = motion detected)."""
        from datetime import datetime
        
        # Get current people count to influence motion detection
        people_count = self._simulate_people_count()
        
        # Higher people count = higher motion probability
        if people_count == 0:
            motion_probability = 0.01  # Very low false positive rate
        elif people_count <= 2:
            motion_probability = 0.3  # Moderate motion with few people
        else:
            motion_probability = 0.8  # High motion with many people
        
        # Random motion events
        random_motion = np.random.random() < motion_probability
        
        # Apply sensitivity
        if random_motion and np.random.random() < self.motion_sensitivity:
            self.last_motion_time = datetime.now()
            return 1.0
        else:
            return 0.0
    
    def _simulate_presence_detection(self) -> float:
        """Simulate presence detection (0 = no presence, 1 = presence detected)."""
        from datetime import datetime
        
        current_time = datetime.now()
        
        # Check if there was recent motion
        if (self.last_motion_time and 
            (current_time - self.last_motion_time).total_seconds() < self.presence_timeout):
            return 1.0
        
        # Otherwise, base presence on people count
        people_count = self._simulate_people_count()
        
        if people_count > 0:
            # High probability of presence detection when people are present
            return 1.0 if np.random.random() < 0.95 else 0.0
        else:
            # Low false positive rate when no one is present
            return 1.0 if np.random.random() < 0.02 else 0.0
    
    def get_occupancy_level(self) -> str:
        """Get occupancy level category."""
        if self.occupancy_type == "people_count":
            count = self.get_current_reading()
            ratio = count / self.max_occupancy
            
            if ratio == 0:
                return "empty"
            elif ratio <= 0.25:
                return "low"
            elif ratio <= 0.5:
                return "moderate"
            elif ratio <= 0.75:
                return "high"
            else:
                return "full"
        return "unknown"
    
    def is_occupied(self) -> bool:
        """Check if the area is currently occupied."""
        if self.occupancy_type == "people_count":
            return self.get_current_reading() > 0
        elif self.occupancy_type in ["motion", "presence"]:
            return self.get_current_reading() > 0.5
        return False
    
    def get_utilization_rate(self) -> float:
        """Get current utilization rate (0.0 to 1.0)."""
        if self.occupancy_type == "people_count":
            current_count = self.get_current_reading()
            return min(1.0, current_count / self.max_occupancy)
        return 0.0
