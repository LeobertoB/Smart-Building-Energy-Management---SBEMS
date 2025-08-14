"""
HVAC (Heating, Ventilation, Air Conditioning) sensor implementation.
"""

import numpy as np
from typing import Tuple
from .base_sensor import BaseSensor


class HVACSensor(BaseSensor):
    """
    HVAC sensor for monitoring temperature, humidity, and air quality.
    """
    
    def __init__(self, hvac_type: str = "temperature", **kwargs):
        """
        Initialize HVAC sensor.
        
        Args:
            hvac_type: Type of HVAC measurement (temperature, humidity, air_quality, pressure)
        """
        self.hvac_type = hvac_type
        super().__init__(**kwargs)
        
        # HVAC-specific configuration
        self.target_temperature = 22.0  # Celsius
        self.seasonal_variation = 5.0  # Seasonal temperature variation
        self.daily_variation = 3.0  # Daily temperature variation
        self.occupancy_effect = 2.0  # Temperature rise per person
        
    @property
    def sensor_type(self) -> str:
        return f"hvac_{self.hvac_type}"
    
    @property
    def unit(self) -> str:
        units = {
            "temperature": "°C",
            "humidity": "%",
            "air_quality": "AQI",
            "pressure": "Pa"
        }
        return units.get(self.hvac_type, "units")
    
    @property
    def normal_range(self) -> Tuple[float, float]:
        ranges = {
            "temperature": (18.0, 26.0),
            "humidity": (30.0, 70.0),
            "air_quality": (0.0, 100.0),
            "pressure": (98000.0, 102000.0)
        }
        return ranges.get(self.hvac_type, (0.0, 100.0))
    
    def _read_sensor_value(self) -> float:
        """Read HVAC sensor value with realistic simulation."""
        if self.hvac_type == "temperature":
            return self._simulate_temperature()
        elif self.hvac_type == "humidity":
            return self._simulate_humidity()
        elif self.hvac_type == "air_quality":
            return self._simulate_air_quality()
        elif self.hvac_type == "pressure":
            return self._simulate_pressure()
        else:
            return np.random.uniform(*self.normal_range)
    
    def _simulate_temperature(self) -> float:
        """Simulate realistic temperature readings."""
        from datetime import datetime
        import math
        
        current_time = datetime.now()
        
        # Base temperature
        base_temp = self.target_temperature
        
        # Daily variation (peak at 2 PM)
        hour_angle = 2 * math.pi * (current_time.hour - 14) / 24
        daily_variation = self.daily_variation * math.sin(hour_angle)
        
        # Seasonal variation (simplified)
        day_of_year = current_time.timetuple().tm_yday
        seasonal_angle = 2 * math.pi * (day_of_year - 80) / 365  # Peak in summer
        seasonal_variation = self.seasonal_variation * math.sin(seasonal_angle)
        
        # Occupancy effect (simplified)
        occupancy_effect = np.random.uniform(0, self.occupancy_effect)
        
        # Random noise
        noise = np.random.normal(0, 0.5)
        
        # Combine all effects
        temperature = base_temp + daily_variation + seasonal_variation + occupancy_effect + noise
        
        # Ensure within reasonable bounds
        return np.clip(temperature, 10.0, 35.0)
    
    def _simulate_humidity(self) -> float:
        """Simulate realistic humidity readings."""
        # Base humidity varies with temperature
        current_temp = self._simulate_temperature()
        
        # Higher temperature generally means lower relative humidity
        base_humidity = 60 - (current_temp - 20) * 2
        
        # Add some variation
        variation = np.random.normal(0, 5)
        
        humidity = base_humidity + variation
        
        # Ensure within valid range
        return np.clip(humidity, 0.0, 100.0)
    
    def _simulate_air_quality(self) -> float:
        """Simulate air quality index (0-100, lower is better)."""
        from datetime import datetime
        
        current_time = datetime.now()
        
        # Base air quality (better during night)
        if 6 <= current_time.hour <= 22:  # Daytime
            base_aqi = 30 + np.random.uniform(0, 20)  # Higher during day
        else:  # Nighttime
            base_aqi = 15 + np.random.uniform(0, 15)  # Lower during night
        
        # Occupancy effect (more people = worse air quality)
        occupancy_effect = np.random.uniform(0, 15)
        
        # Random variation
        noise = np.random.normal(0, 5)
        
        aqi = base_aqi + occupancy_effect + noise
        
        return np.clip(aqi, 0.0, 100.0)
    
    def _simulate_pressure(self) -> float:
        """Simulate atmospheric pressure."""
        # Standard atmospheric pressure with small variations
        base_pressure = 101325  # Pascal
        
        # Small random variations
        variation = np.random.normal(0, 500)
        
        pressure = base_pressure + variation
        
        return np.clip(pressure, 95000.0, 105000.0)
    
    def set_target_temperature(self, temperature: float) -> None:
        """Set the target temperature for the HVAC system."""
        self.target_temperature = temperature
    
    def is_in_normal_range(self) -> bool:
        """Check if current reading is within normal operating range."""
        current_value = self.get_current_reading()
        min_val, max_val = self.normal_range
        return min_val <= current_value <= max_val
