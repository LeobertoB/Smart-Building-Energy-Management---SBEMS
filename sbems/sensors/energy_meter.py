"""
Energy meter sensor implementation for monitoring electrical consumption.
"""

import numpy as np
from typing import Tuple
from .base_sensor import BaseSensor


class EnergyMeter(BaseSensor):
    """
    Energy meter sensor for monitoring electrical power consumption and related metrics.
    """
    
    def __init__(self, meter_type: str = "power", circuit_capacity: float = 1000.0, **kwargs):
        """
        Initialize energy meter sensor.
        
        Args:
            meter_type: Type of energy measurement (power, voltage, current, energy_total)
            circuit_capacity: Maximum capacity of the circuit in watts
        """
        self.meter_type = meter_type
        self.circuit_capacity = circuit_capacity
        super().__init__(**kwargs)
        
        # Energy meter specific configuration
        self.base_load = circuit_capacity * 0.1  # 10% base load
        self.peak_load_multiplier = 0.8  # Maximum load as fraction of capacity
        self.power_factor = 0.9  # Power factor for reactive power calculations
        self.voltage_nominal = 230.0  # Nominal voltage in volts
        
        # Energy tracking
        self.total_energy_consumed = 0.0  # kWh
        self.last_reading_time = None
        
    @property
    def sensor_type(self) -> str:
        return f"energy_{self.meter_type}"
    
    @property
    def unit(self) -> str:
        units = {
            "power": "W",
            "voltage": "V", 
            "current": "A",
            "energy_total": "kWh",
            "power_factor": "pf"
        }
        return units.get(self.meter_type, "units")
    
    @property
    def normal_range(self) -> Tuple[float, float]:
        ranges = {
            "power": (self.base_load, self.circuit_capacity * self.peak_load_multiplier),
            "voltage": (220.0, 240.0),
            "current": (0.0, self.circuit_capacity / self.voltage_nominal),
            "energy_total": (0.0, 10000.0),  # Arbitrary large number
            "power_factor": (0.7, 1.0)
        }
        return ranges.get(self.meter_type, (0.0, 100.0))
    
    def _read_sensor_value(self) -> float:
        """Read energy meter value with realistic simulation."""
        if self.meter_type == "power":
            return self._simulate_power_consumption()
        elif self.meter_type == "voltage":
            return self._simulate_voltage()
        elif self.meter_type == "current":
            return self._simulate_current()
        elif self.meter_type == "energy_total":
            return self._simulate_total_energy()
        elif self.meter_type == "power_factor":
            return self._simulate_power_factor()
        else:
            return np.random.uniform(*self.normal_range)
    
    def _simulate_power_consumption(self) -> float:
        """Simulate realistic power consumption patterns."""
        from datetime import datetime
        
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()
        
        # Base load pattern
        if weekday < 5:  # Weekday
            load_pattern = self._get_weekday_load_pattern(hour)
        else:  # Weekend
            load_pattern = self._get_weekend_load_pattern(hour)
        
        # Calculate expected power consumption
        expected_power = self.base_load + (self.circuit_capacity - self.base_load) * load_pattern
        
        # Add random variation (±15%)
        variation = np.random.normal(0, expected_power * 0.15)
        actual_power = expected_power + variation
        
        # Ensure within circuit capacity
        return np.clip(actual_power, 0, self.circuit_capacity)
    
    def _get_weekday_load_pattern(self, hour: int) -> float:
        """Get power load pattern for weekdays (0.0 to 1.0)."""
        patterns = {
            # Early morning startup
            6: 0.3, 7: 0.5, 8: 0.7,
            # Morning work period
            9: 0.8, 10: 0.85, 11: 0.9, 12: 0.7,  # Lunch reduction
            # Afternoon work period
            13: 0.85, 14: 0.9, 15: 0.95, 16: 0.9, 17: 0.8,
            # Evening reduction
            18: 0.5, 19: 0.3, 20: 0.2, 21: 0.15, 22: 0.1,
        }
        
        # Night time very low consumption
        if hour < 6 or hour > 22:
            return 0.05
        
        return patterns.get(hour, 0.4)
    
    def _get_weekend_load_pattern(self, hour: int) -> float:
        """Get power load pattern for weekends (0.0 to 1.0)."""
        patterns = {
            # Late morning start
            9: 0.2, 10: 0.3, 11: 0.4, 12: 0.5,
            # Afternoon moderate use
            13: 0.4, 14: 0.5, 15: 0.4, 16: 0.3,
            # Evening low use
            17: 0.25, 18: 0.2, 19: 0.15, 20: 0.1,
        }
        
        if hour < 9 or hour > 20:
            return 0.05
        
        return patterns.get(hour, 0.2)
    
    def _simulate_voltage(self) -> float:
        """Simulate voltage readings with realistic variations."""
        # Nominal voltage with small variations
        base_voltage = self.voltage_nominal
        
        # Time-based variations (grid load effects)
        from datetime import datetime
        hour = datetime.now().hour
        
        # Higher load times have slightly lower voltage
        if 8 <= hour <= 18:  # Peak hours
            voltage_drop = np.random.uniform(2, 8)
        else:  # Off-peak hours
            voltage_drop = np.random.uniform(0, 3)
        
        # Random noise
        noise = np.random.normal(0, 1)
        
        voltage = base_voltage - voltage_drop + noise
        
        return np.clip(voltage, 200.0, 250.0)
    
    def _simulate_current(self) -> float:
        """Simulate current based on power consumption and voltage."""
        power = self._simulate_power_consumption()
        voltage = self._simulate_voltage()
        
        # Current = Power / Voltage (simplified, not considering power factor here)
        current = power / voltage
        
        # Add small measurement error
        error = np.random.normal(0, current * 0.02)
        
        return max(0, current + error)
    
    def _simulate_total_energy(self) -> float:
        """Simulate cumulative energy consumption."""
        from datetime import datetime, timedelta
        
        current_time = datetime.now()
        
        if self.last_reading_time is None:
            self.last_reading_time = current_time
            return self.total_energy_consumed
        
        # Calculate time difference in hours
        time_diff = (current_time - self.last_reading_time).total_seconds() / 3600
        
        # Get current power consumption
        current_power = self._simulate_power_consumption()
        
        # Add energy consumed since last reading (kWh)
        energy_increment = (current_power * time_diff) / 1000
        self.total_energy_consumed += energy_increment
        
        self.last_reading_time = current_time
        
        return self.total_energy_consumed
    
    def _simulate_power_factor(self) -> float:
        """Simulate power factor readings."""
        # Power factor varies with load
        current_power = self._simulate_power_consumption()
        load_ratio = current_power / self.circuit_capacity
        
        # Lower loads typically have worse power factor
        if load_ratio < 0.2:
            base_pf = 0.75
        elif load_ratio < 0.5:
            base_pf = 0.85
        else:
            base_pf = 0.92
        
        # Add small variation
        variation = np.random.normal(0, 0.03)
        pf = base_pf + variation
        
        return np.clip(pf, 0.5, 1.0)
    
    def get_load_percentage(self) -> float:
        """Get current load as percentage of circuit capacity."""
        if self.meter_type == "power":
            current_power = self.get_current_reading()
            return (current_power / self.circuit_capacity) * 100
        return 0.0
    
    def is_overloaded(self, threshold: float = 0.9) -> bool:
        """Check if circuit is approaching overload."""
        load_percentage = self.get_load_percentage()
        return load_percentage > (threshold * 100)
    
    def get_efficiency_rating(self) -> str:
        """Get efficiency rating based on power factor and load."""
        if self.meter_type == "power_factor":
            pf = self.get_current_reading()
            if pf >= 0.95:
                return "excellent"
            elif pf >= 0.9:
                return "good"
            elif pf >= 0.8:
                return "fair"
            else:
                return "poor"
        return "unknown"
    
    def calculate_cost(self, rate_per_kwh: float = 0.12) -> float:
        """Calculate energy cost based on total consumption."""
        if self.meter_type == "energy_total":
            total_energy = self.get_current_reading()
            return total_energy * rate_per_kwh
        return 0.0
    
    def reset_energy_counter(self) -> None:
        """Reset the total energy counter."""
        if self.meter_type == "energy_total":
            self.total_energy_consumed = 0.0
