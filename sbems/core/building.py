"""
Building model representing a smart building with sensors and zones.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from loguru import logger

from ..sensors.base_sensor import BaseSensor
from ..sensors.hvac_sensor import HVACSensor
from ..sensors.lighting_sensor import LightingSensor
from ..sensors.occupancy_sensor import OccupancySensor
from ..sensors.energy_meter import EnergyMeter


@dataclass
class Zone:
    """Represents a zone or room in the building."""
    id: str
    name: str
    area: float  # Square meters
    floor: int
    zone_type: str  # office, meeting_room, hallway, etc.
    max_occupancy: int
    position: Tuple[float, float, float]  # x, y, z coordinates
    sensors: List[BaseSensor] = field(default_factory=list)
    
    def add_sensor(self, sensor: BaseSensor) -> None:
        """Add a sensor to this zone."""
        sensor.zone_id = self.id
        self.sensors.append(sensor)
        logger.debug(f"Added {sensor.sensor_type} sensor to zone {self.name}")
    
    def get_sensors_by_type(self, sensor_type: str) -> List[BaseSensor]:
        """Get all sensors of a specific type in this zone."""
        return [s for s in self.sensors if s.sensor_type == sensor_type]
    
    def get_current_occupancy(self) -> int:
        """Get current occupancy from occupancy sensors."""
        occupancy_sensors = self.get_sensors_by_type("occupancy")
        if occupancy_sensors:
            return max(int(sensor.get_current_reading()) for sensor in occupancy_sensors)
        return 0
    
    def get_energy_consumption(self) -> float:
        """Get current total energy consumption for this zone."""
        energy_meters = self.get_sensors_by_type("energy_meter")
        return sum(sensor.get_current_reading() for sensor in energy_meters)


@dataclass
class BuildingInfo:
    """Building metadata and configuration."""
    name: str
    address: str
    total_area: float  # Square meters
    floors: int
    building_type: str  # office, residential, mixed, etc.
    year_built: int
    energy_rating: str  # A, B, C, D, E, F, G
    timezone: str = "UTC"


class Building:
    """
    Main building class that manages zones, sensors, and overall building state.
    """
    
    def __init__(self, building_info: BuildingInfo):
        """Initialize building with basic information."""
        self.info = building_info
        self.zones: Dict[str, Zone] = {}
        self.sensors: Dict[str, BaseSensor] = {}
        self.created_at = datetime.now()
        
        logger.info(f"Initialized building: {building_info.name}")
    
    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the building."""
        self.zones[zone.id] = zone
        logger.info(f"Added zone {zone.name} to building {self.info.name}")
    
    def add_sensor(self, sensor: BaseSensor, zone_id: Optional[str] = None) -> None:
        """Add a sensor to the building and optionally to a specific zone."""
        self.sensors[sensor.id] = sensor
        
        if zone_id and zone_id in self.zones:
            self.zones[zone_id].add_sensor(sensor)
        
        logger.debug(f"Added sensor {sensor.id} ({sensor.sensor_type}) to building")
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get a zone by ID."""
        return self.zones.get(zone_id)
    
    def get_sensor(self, sensor_id: str) -> Optional[BaseSensor]:
        """Get a sensor by ID."""
        return self.sensors.get(sensor_id)
    
    def get_sensors_by_type(self, sensor_type: str) -> List[BaseSensor]:
        """Get all sensors of a specific type in the building."""
        return [s for s in self.sensors.values() if s.sensor_type == sensor_type]
    
    def get_zones_by_type(self, zone_type: str) -> List[Zone]:
        """Get all zones of a specific type."""
        return [z for z in self.zones.values() if z.zone_type == zone_type]
    
    def get_zones_by_floor(self, floor: int) -> List[Zone]:
        """Get all zones on a specific floor."""
        return [z for z in self.zones.values() if z.floor == floor]
    
    def get_total_occupancy(self) -> int:
        """Get total current occupancy of the building."""
        return sum(zone.get_current_occupancy() for zone in self.zones.values())
    
    def get_total_energy_consumption(self) -> float:
        """Get total current energy consumption of the building."""
        return sum(zone.get_energy_consumption() for zone in self.zones.values())
    
    def get_building_summary(self) -> Dict:
        """Get a comprehensive summary of the building state."""
        active_sensors = [s for s in self.sensors.values() if s.is_active()]
        
        return {
            "building_info": {
                "name": self.info.name,
                "total_area": self.info.total_area,
                "floors": self.info.floors,
                "building_type": self.info.building_type,
            },
            "zones": {
                "total_zones": len(self.zones),
                "by_type": self._count_by_attribute("zone_type"),
                "by_floor": self._count_by_attribute("floor"),
            },
            "sensors": {
                "total_sensors": len(self.sensors),
                "active_sensors": len(active_sensors),
                "by_type": self._count_sensors_by_type(),
            },
            "current_state": {
                "total_occupancy": self.get_total_occupancy(),
                "total_energy_consumption": self.get_total_energy_consumption(),
                "timestamp": datetime.now().isoformat(),
            }
        }
    
    def _count_by_attribute(self, attribute: str) -> Dict[str, int]:
        """Helper method to count zones by a specific attribute."""
        counts = {}
        for zone in self.zones.values():
            value = getattr(zone, attribute)
            counts[str(value)] = counts.get(str(value), 0) + 1
        return counts
    
    def _count_sensors_by_type(self) -> Dict[str, int]:
        """Helper method to count sensors by type."""
        counts = {}
        for sensor in self.sensors.values():
            sensor_type = sensor.sensor_type
            counts[sensor_type] = counts.get(sensor_type, 0) + 1
        return counts
    
    def simulate_step(self, timestep: int) -> None:
        """Advance simulation by one step for all sensors."""
        for sensor in self.sensors.values():
            if hasattr(sensor, 'simulate_reading'):
                sensor.simulate_reading(timestep)
    
    def get_sensor_network_graph(self):
        """Get network graph representation of sensor connectivity."""
        try:
            import networkx as nx
            
            G = nx.Graph()
            
            # Add sensors as nodes
            for sensor in self.sensors.values():
                G.add_node(sensor.id, 
                          sensor_type=sensor.sensor_type,
                          zone_id=getattr(sensor, 'zone_id', None),
                          position=sensor.position)
            
            # Add edges based on proximity (simplified)
            sensor_list = list(self.sensors.values())
            for i, sensor1 in enumerate(sensor_list):
                for sensor2 in sensor_list[i+1:]:
                    # Connect sensors in the same zone or within range
                    if (getattr(sensor1, 'zone_id', None) == getattr(sensor2, 'zone_id', None) or
                        self._calculate_distance(sensor1.position, sensor2.position) < 20):
                        G.add_edge(sensor1.id, sensor2.id)
            
            return G
            
        except ImportError:
            logger.warning("NetworkX not available for graph generation")
            return None
    
    @staticmethod
    def _calculate_distance(pos1: Tuple[float, float, float], 
                          pos2: Tuple[float, float, float]) -> float:
        """Calculate 3D distance between two positions."""
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
