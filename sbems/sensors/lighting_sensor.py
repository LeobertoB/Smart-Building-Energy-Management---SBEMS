"""
Lighting sensor implementation for monitoring light levels and energy consumption.
"""

import numpy as np
from typing import Tuple
from .base_sensor import BaseSensor


class LightingSensor(BaseSensor):
    """
    Lighting sensor for monitoring illuminance and lighting energy consumption.
    """
    
    def __init__(self, lighting_type: str = "illuminance", **kwargs):
        """
        Initialize lighting sensor.
        
        Args:
            lighting_type: Type of lighting measurement (illuminance, energy, dimmer_level)
        """
        self.lighting_type = lighting_type
        super().__init__(**kwargs)
        
        # Lighting-specific configuration
        self.max_illuminance = 1000  # lux
        self.min_illuminance = 50   # lux
        self.natural_light_factor = 0.7  # How much natural light affects readings
        self.artificial_light_power = 20  # Watts per fixture
        
    @property
    def sensor_type(self) -> str:
        return f"lighting_{self.lighting_type}"
    
    @property
    def unit(self) -> str:
        units = {
            "illuminance": "lux",
            "energy": "W",
            "dimmer_level": "%"
        }
        return units.get(self.lighting_type, "units")
    
    @property
    def normal_range(self) -> Tuple[float, float]:
        ranges = {
            "illuminance": (50.0, 1000.0),
            "energy": (0.0, 100.0),
            "dimmer_level": (0.0, 100.0)
        }
        return ranges.get(self.lighting_type, (0.0, 100.0))
    
    def _read_sensor_value(self) -> float:
        """Read lighting sensor value with realistic simulation."""
        if self.lighting_type == "illuminance":
            return self._simulate_illuminance()
        elif self.lighting_type == "energy":
            return self._simulate_energy_consumption()
        elif self.lighting_type == "dimmer_level":
            return self._simulate_dimmer_level()
        else:
            return np.random.uniform(*self.normal_range)
    
    def _simulate_illuminance(self) -> float:
        """Simulate realistic illuminance readings."""
        from datetime import datetime
        import math
        
        current_time = datetime.now()
        
        # Natural light contribution based on time of day
        natural_light = self._calculate_natural_light(current_time)
        
        # Artificial light contribution (depends on occupancy and time)
        artificial_light = self._calculate_artificial_light(current_time)
        
        # Combine natural and artificial light
        total_illuminance = natural_light + artificial_light
        
        # Add some random variation
        noise = np.random.normal(0, total_illuminance * 0.05)
        
        illuminance = total_illuminance + noise
        
        return np.clip(illuminance, 0.0, 2000.0)
    
    def _calculate_natural_light(self, current_time) -> float:
        """Calculate natural light contribution based on time of day."""
        import math
        
        hour = current_time.hour
        
        if 6 <= hour <= 18:  # Daytime
            # Peak natural light at noon
            hour_angle = 2 * math.pi * (hour - 12) / 12
            natural_light_factor = (math.cos(hour_angle) + 1) / 2
            max_natural_light = 800  # Maximum natural light in lux
            natural_light = max_natural_light * natural_light_factor
        else:  # Nighttime
            natural_light = 0
        
        # Weather effects (simplified)
        weather_factor = np.random.uniform(0.3, 1.0)  # Cloudy vs sunny
        
        return natural_light * weather_factor * self.natural_light_factor
    
    def _calculate_artificial_light(self, current_time) -> float:
        """Calculate artificial light contribution."""
        hour = current_time.hour
        
        # Office hours: more artificial light
        if 8 <= hour <= 18:
            # High artificial light during office hours
            base_artificial = 400
            # Random variation based on occupancy
            occupancy_factor = np.random.uniform(0.5, 1.0)
        elif 18 < hour <= 22:
            # Moderate artificial light in evening
            base_artificial = 200
            occupancy_factor = np.random.uniform(0.3, 0.8)
        else:
            # Low artificial light at night
            base_artificial = 50
            occupancy_factor = np.random.uniform(0.1, 0.3)
        
        return base_artificial * occupancy_factor
    
    def _simulate_energy_consumption(self) -> float:
        """Simulate lighting energy consumption."""
        from datetime import datetime
        
        current_time = datetime.now()
        hour = current_time.hour
        
        # Base energy consumption based on time of day
        if 8 <= hour <= 18:  # Office hours
            base_consumption = self.artificial_light_power * 0.8
            variation_factor = np.random.uniform(0.7, 1.0)
        elif 18 < hour <= 22:  # Evening
            base_consumption = self.artificial_light_power * 0.5
            variation_factor = np.random.uniform(0.4, 0.8)
        else:  # Night
            base_consumption = self.artificial_light_power * 0.2
            variation_factor = np.random.uniform(0.1, 0.4)
        
        # Occupancy effect
        occupancy_factor = np.random.uniform(0.5, 1.2)
        
        # Natural light dimming effect
        natural_light = self._calculate_natural_light(current_time)
        dimming_factor = max(0.2, 1.0 - (natural_light / 800))
        
        energy = base_consumption * variation_factor * occupancy_factor * dimming_factor
        
        return np.clip(energy, 0.0, self.artificial_light_power * 1.5)
    
    def _simulate_dimmer_level(self) -> float:
        """Simulate dimmer level (0-100%)."""
        from datetime import datetime
        
        current_time = datetime.now()
        
        # Natural light affects dimmer level
        natural_light = self._calculate_natural_light(current_time)
        
        # Higher natural light = lower dimmer level
        base_dimmer = max(20, 100 - (natural_light / 10))
        
        # Time-based adjustments
        hour = current_time.hour
        if 8 <= hour <= 18:  # Office hours
            time_adjustment = np.random.uniform(-10, 10)
        else:
            time_adjustment = np.random.uniform(-20, 0)
        
        dimmer_level = base_dimmer + time_adjustment
        
        return np.clip(dimmer_level, 0.0, 100.0)
    
    def is_energy_efficient(self) -> bool:
        """Check if lighting is operating efficiently."""
        if self.lighting_type == "energy":
            current_consumption = self.get_current_reading()
            # Consider efficient if consuming less than 70% of max power
            return current_consumption < (self.artificial_light_power * 0.7)
        return True
    
    def get_brightness_category(self) -> str:
        """Get brightness category based on current illuminance."""
        if self.lighting_type == "illuminance":
            illuminance = self.get_current_reading()
            if illuminance < 100:
                return "dim"
            elif illuminance < 300:
                return "moderate"
            elif illuminance < 600:
                return "bright"
            else:
                return "very_bright"
        return "unknown"
