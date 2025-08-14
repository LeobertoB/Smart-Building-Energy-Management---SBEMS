"""
Base sensor class for all building sensors.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import numpy as np


class SensorStatus(Enum):
    """Sensor operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    CALIBRATING = "calibrating"


@dataclass
class SensorReading:
    """Represents a single sensor reading."""
    timestamp: datetime
    value: float
    unit: str
    quality: float = 1.0  # 0.0 to 1.0, where 1.0 is perfect quality
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseSensor(ABC):
    """
    Abstract base class for all building sensors.
    """
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        zone_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """Initialize base sensor."""
        self.id = sensor_id or str(uuid.uuid4())
        self.position = position  # (x, y, z) coordinates
        self.zone_id = zone_id
        self.name = name or f"{self.sensor_type}_{self.id[:8]}"
        self.status = SensorStatus.ACTIVE
        self.created_at = datetime.now()
        self.last_reading_time: Optional[datetime] = None
        self.readings_history: List[SensorReading] = []
        self.max_history_size = 1000  # Maximum readings to keep in memory
        
        # Sensor configuration
        self.sampling_rate = 60  # seconds between readings
        self.accuracy = 0.95  # Sensor accuracy (0.0 to 1.0)
        self.drift_rate = 0.001  # How much the sensor drifts over time
        self.failure_probability = 0.0001  # Probability of failure per reading
        
        # Current values
        self._current_value: Optional[float] = None
        self._calibration_offset = 0.0
    
    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """Return the sensor type identifier."""
        pass
    
    @property
    @abstractmethod
    def unit(self) -> str:
        """Return the measurement unit."""
        pass
    
    @property
    @abstractmethod
    def normal_range(self) -> Tuple[float, float]:
        """Return the normal operating range (min, max)."""
        pass
    
    def is_active(self) -> bool:
        """Check if sensor is active and operational."""
        return self.status == SensorStatus.ACTIVE
    
    def get_current_reading(self) -> float:
        """Get the current sensor reading value."""
        if self._current_value is None:
            self._current_value = self._generate_initial_reading()
        return self._current_value + self._calibration_offset
    
    def take_reading(self) -> SensorReading:
        """Take a new sensor reading."""
        if not self.is_active():
            raise RuntimeError(f"Sensor {self.id} is not active (status: {self.status})")
        
        # Simulate sensor failure
        if np.random.random() < self.failure_probability:
            self.status = SensorStatus.ERROR
            raise RuntimeError(f"Sensor {self.id} has failed")
        
        # Get the actual reading
        value = self._read_sensor_value()
        
        # Apply sensor accuracy and drift
        noise = np.random.normal(0, (1 - self.accuracy) * abs(value) * 0.1)
        drift = self.drift_rate * (datetime.now() - self.created_at).total_seconds()
        
        final_value = value + noise + drift + self._calibration_offset
        
        # Create reading object
        reading = SensorReading(
            timestamp=datetime.now(),
            value=final_value,
            unit=self.unit,
            quality=self.accuracy,
            metadata={
                "sensor_id": self.id,
                "sensor_type": self.sensor_type,
                "zone_id": self.zone_id,
                "position": self.position,
            }
        )
        
        # Store reading
        self.readings_history.append(reading)
        self.last_reading_time = reading.timestamp
        self._current_value = final_value
        
        # Limit history size
        if len(self.readings_history) > self.max_history_size:
            self.readings_history.pop(0)
        
        return reading
    
    @abstractmethod
    def _read_sensor_value(self) -> float:
        """Read the actual sensor value. Must be implemented by subclasses."""
        pass
    
    def _generate_initial_reading(self) -> float:
        """Generate an initial reading for the sensor."""
        min_val, max_val = self.normal_range
        return np.random.uniform(min_val, max_val)
    
    def get_recent_readings(self, count: int = 10) -> List[SensorReading]:
        """Get the most recent sensor readings."""
        return self.readings_history[-count:]
    
    def get_readings_in_range(self, start_time: datetime, end_time: datetime) -> List[SensorReading]:
        """Get sensor readings within a time range."""
        return [
            reading for reading in self.readings_history
            if start_time <= reading.timestamp <= end_time
        ]
    
    def get_statistics(self, hours: int = 24) -> Dict[str, float]:
        """Get statistical summary of recent readings."""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_readings = [
            r for r in self.readings_history 
            if r.timestamp >= cutoff_time
        ]
        
        if not recent_readings:
            return {}
        
        values = [r.value for r in recent_readings]
        
        return {
            "count": len(values),
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "current": values[-1] if values else None,
        }
    
    def calibrate(self, reference_value: float) -> None:
        """Calibrate the sensor against a reference value."""
        current_reading = self.get_current_reading()
        self._calibration_offset = reference_value - current_reading
        self.status = SensorStatus.CALIBRATING
        
        # Simulate calibration time
        import time
        time.sleep(0.1)
        
        self.status = SensorStatus.ACTIVE
    
    def set_maintenance_mode(self, maintenance: bool = True) -> None:
        """Set sensor to maintenance mode."""
        if maintenance:
            self.status = SensorStatus.MAINTENANCE
        else:
            self.status = SensorStatus.ACTIVE
    
    def reset(self) -> None:
        """Reset sensor to initial state."""
        self.status = SensorStatus.ACTIVE
        self._calibration_offset = 0.0
        self._current_value = None
        self.readings_history.clear()
        self.last_reading_time = None
    
    def get_sensor_info(self) -> Dict[str, Any]:
        """Get comprehensive sensor information."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.sensor_type,
            "status": self.status.value,
            "position": self.position,
            "zone_id": self.zone_id,
            "unit": self.unit,
            "normal_range": self.normal_range,
            "accuracy": self.accuracy,
            "sampling_rate": self.sampling_rate,
            "created_at": self.created_at.isoformat(),
            "last_reading_time": self.last_reading_time.isoformat() if self.last_reading_time else None,
            "readings_count": len(self.readings_history),
            "current_value": self.get_current_reading() if self.is_active() else None,
        }
    
    def simulate_reading(self, timestep: int) -> None:
        """Simulate a sensor reading for a given timestep (used in simulations)."""
        if self.is_active():
            try:
                self.take_reading()
            except RuntimeError:
                # Sensor failed, handle gracefully
                pass
