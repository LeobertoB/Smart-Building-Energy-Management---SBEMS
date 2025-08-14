"""
Main monitoring system that coordinates building sensors and anomaly detection.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from threading import Thread, Event
from dataclasses import dataclass
import json
from loguru import logger

from .building import Building, Zone, BuildingInfo
from ..sensors.base_sensor import BaseSensor
from ..sensors.hvac_sensor import HVACSensor
from ..sensors.lighting_sensor import LightingSensor
from ..sensors.occupancy_sensor import OccupancySensor
from ..sensors.energy_meter import EnergyMeter
from ..analytics.anomaly_detector import AnomalyDetector, Anomaly


@dataclass
class MonitoringConfig:
    """Configuration for the monitoring system."""
    sampling_interval: int = 60  # seconds between readings
    anomaly_check_interval: int = 300  # seconds between anomaly checks
    auto_start: bool = True
    save_history: bool = True
    max_history_size: int = 10000
    enable_alerts: bool = True
    alert_threshold: str = "medium"  # low, medium, high, critical


class MonitoringSystem:
    """
    Main monitoring system that coordinates all building sensors and analytics.
    
    This is the enhanced version of your original SensorNetworkMonitor that provides:
    - Professional building management
    - Real-time monitoring with configurable intervals
    - Advanced anomaly detection
    - Historical data management
    - Alert system
    - Multi-threaded operation
    """
    
    def __init__(self, building: Building, config: Optional[MonitoringConfig] = None):
        """
        Initialize the monitoring system.
        
        Args:
            building: Building object to monitor
            config: Monitoring configuration
        """
        self.building = building
        self.config = config or MonitoringConfig()
        self.anomaly_detector = AnomalyDetector()
        
        # Monitoring state
        self.is_running = False
        self.monitoring_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Data storage
        self.reading_history: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.start_time: Optional[datetime] = None
        self.total_readings = 0
        self.total_anomalies = 0
        
        logger.info(f"Initialized monitoring system for building: {building.info.name}")
    
    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self.is_running:
            logger.warning("Monitoring system is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        self.stop_event.clear()
        
        if self.config.auto_start:
            self.monitoring_thread = Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
        logger.info("Started monitoring system")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        if not self.is_running:
            logger.warning("Monitoring system is not running")
            return
        
        self.is_running = False
        self.stop_event.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Stopped monitoring system")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in a separate thread."""
        logger.info("Starting monitoring loop")
        
        last_anomaly_check = datetime.now()
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Take readings from all sensors
                self._collect_sensor_readings()
                
                # Check for anomalies periodically
                current_time = datetime.now()
                if (current_time - last_anomaly_check).total_seconds() >= self.config.anomaly_check_interval:
                    self._perform_anomaly_detection()
                    last_anomaly_check = current_time
                
                # Wait for next sampling interval
                self.stop_event.wait(self.config.sampling_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_sensor_readings(self) -> None:
        """Collect readings from all sensors in the building."""
        timestamp = datetime.now()
        readings = {}
        
        for sensor_id, sensor in self.building.sensors.items():
            try:
                if sensor.is_active():
                    reading = sensor.take_reading()
                    readings[sensor_id] = {
                        "value": reading.value,
                        "unit": reading.unit,
                        "quality": reading.quality,
                        "sensor_type": sensor.sensor_type,
                        "zone_id": getattr(sensor, 'zone_id', None)
                    }
                    
                    # Add to anomaly detector
                    self.anomaly_detector.add_sensor_reading(
                        sensor_id=sensor_id,
                        value=reading.value,
                        timestamp=timestamp,
                        sensor_type=sensor.sensor_type,
                        zone_id=getattr(sensor, 'zone_id', None),
                        metadata=reading.metadata
                    )
                    
                    self.total_readings += 1
                    
            except Exception as e:
                logger.warning(f"Failed to read sensor {sensor_id}: {e}")
                readings[sensor_id] = {"error": str(e)}
        
        # Store reading snapshot
        if self.config.save_history:
            reading_snapshot = {
                "timestamp": timestamp.isoformat(),
                "readings": readings,
                "building_summary": self._get_building_state_summary()
            }
            
            self.reading_history.append(reading_snapshot)
            
            # Limit history size
            if len(self.reading_history) > self.config.max_history_size:
                self.reading_history.pop(0)
    
    def _perform_anomaly_detection(self) -> None:
        """Perform anomaly detection and handle alerts."""
        logger.debug("Performing anomaly detection")
        
        # Update network graph for network analysis
        self.anomaly_detector.update_network_graph(self.building)
        
        # Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies()
        
        if anomalies:
            self.total_anomalies += len(anomalies)
            logger.info(f"Detected {len(anomalies)} anomalies")
            
            # Process alerts
            if self.config.enable_alerts:
                self._process_alerts(anomalies)
    
    def _process_alerts(self, anomalies: List[Anomaly]) -> None:
        """Process and store alerts for detected anomalies."""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        threshold_level = severity_order.get(self.config.alert_threshold, 1)
        
        for anomaly in anomalies:
            anomaly_level = severity_order.get(anomaly.severity.value, 0)
            
            if anomaly_level >= threshold_level:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "sensor_id": anomaly.sensor_id,
                    "anomaly_type": anomaly.anomaly_type.value,
                    "severity": anomaly.severity.value,
                    "confidence": anomaly.confidence,
                    "description": anomaly.description,
                    "recommendations": anomaly.recommendations,
                    "value": anomaly.value,
                    "expected_range": anomaly.expected_range
                }
                
                self.alert_history.append(alert)
                
                # Log alert
                logger.warning(
                    f"ALERT [{anomaly.severity.value.upper()}] "
                    f"Sensor {anomaly.sensor_id}: {anomaly.description}"
                )
    
    def _get_building_state_summary(self) -> Dict[str, Any]:
        """Get current building state summary."""
        return {
            "total_occupancy": self.building.get_total_occupancy(),
            "total_energy_consumption": self.building.get_total_energy_consumption(),
            "active_sensors": len([s for s in self.building.sensors.values() if s.is_active()]),
            "total_sensors": len(self.building.sensors)
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring system status."""
        runtime = None
        if self.start_time:
            runtime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "runtime_seconds": runtime,
            "total_readings": self.total_readings,
            "total_anomalies": self.total_anomalies,
            "building_name": self.building.info.name,
            "sensor_count": len(self.building.sensors),
            "zone_count": len(self.building.zones),
            "recent_alerts": len([
                a for a in self.alert_history 
                if datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=24)
            ])
        }
    
    def get_recent_readings(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get recent readings within specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            reading for reading in self.reading_history
            if datetime.fromisoformat(reading["timestamp"]) >= cutoff_time
        ]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) >= cutoff_time
        ]
    
    def get_sensor_statistics(self, sensor_id: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific sensor."""
        sensor = self.building.get_sensor(sensor_id)
        if not sensor:
            return None
        
        stats = sensor.get_statistics(hours)
        
        # Add anomaly information
        recent_anomalies = [
            a for a in self.anomaly_detector.detected_anomalies
            if a.sensor_id == sensor_id and 
               a.timestamp > datetime.now() - timedelta(hours=hours)
        ]
        
        stats.update({
            "sensor_info": sensor.get_sensor_info(),
            "recent_anomalies": len(recent_anomalies),
            "last_anomaly": recent_anomalies[-1].timestamp.isoformat() if recent_anomalies else None
        })
        
        return stats
    
    def export_data(self, filepath: str, hours: Optional[int] = None) -> None:
        """Export monitoring data to a JSON file."""
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            readings = [
                r for r in self.reading_history
                if datetime.fromisoformat(r["timestamp"]) >= cutoff_time
            ]
            alerts = [
                a for a in self.alert_history
                if datetime.fromisoformat(a["timestamp"]) >= cutoff_time
            ]
        else:
            readings = self.reading_history
            alerts = self.alert_history
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "building_info": {
                "name": self.building.info.name,
                "address": self.building.info.address,
                "total_area": self.building.info.total_area,
                "floors": self.building.info.floors
            },
            "monitoring_status": self.get_current_status(),
            "readings": readings,
            "alerts": alerts,
            "sensor_summary": {
                sensor_id: sensor.get_sensor_info()
                for sensor_id, sensor in self.building.sensors.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported monitoring data to {filepath}")
    
    def clear_history(self) -> None:
        """Clear all stored history data."""
        self.reading_history.clear()
        self.alert_history.clear()
        self.anomaly_detector.detected_anomalies.clear()
        logger.info("Cleared all history data")
    
    def add_sensor_to_building(self, sensor: BaseSensor, zone_id: Optional[str] = None) -> None:
        """Add a new sensor to the building during runtime."""
        self.building.add_sensor(sensor, zone_id)
        logger.info(f"Added sensor {sensor.id} to monitoring system")
    
    def remove_sensor_from_building(self, sensor_id: str) -> bool:
        """Remove a sensor from monitoring."""
        if sensor_id in self.building.sensors:
            del self.building.sensors[sensor_id]
            logger.info(f"Removed sensor {sensor_id} from monitoring system")
            return True
        return False
    
    def simulate_step(self) -> None:
        """Manually trigger one monitoring step (useful for testing)."""
        if not self.is_running:
            self.start_time = datetime.now()
        
        self._collect_sensor_readings()
        self._perform_anomaly_detection()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for dashboard display."""
        current_time = datetime.now()
        
        # Get recent data
        recent_readings = self.get_recent_readings(hours=1)
        recent_alerts = self.get_recent_alerts(hours=24)
        
        # Calculate metrics
        energy_consumption = self.building.get_total_energy_consumption()
        occupancy = self.building.get_total_occupancy()
        
        # Sensor health
        active_sensors = [s for s in self.building.sensors.values() if s.is_active()]
        total_sensors = len(self.building.sensors)
        
        return {
            "timestamp": current_time.isoformat(),
            "building": {
                "name": self.building.info.name,
                "occupancy": occupancy,
                "energy_consumption": energy_consumption,
                "zones": len(self.building.zones),
            },
            "sensors": {
                "total": total_sensors,
                "active": len(active_sensors),
                "health_percentage": (len(active_sensors) / total_sensors * 100) if total_sensors > 0 else 0
            },
            "alerts": {
                "total_24h": len(recent_alerts),
                "critical": len([a for a in recent_alerts if a["severity"] == "critical"]),
                "high": len([a for a in recent_alerts if a["severity"] == "high"]),
                "recent": recent_alerts[:5]  # Last 5 alerts
            },
            "monitoring": self.get_current_status(),
            "anomaly_summary": self.anomaly_detector.get_anomaly_summary(hours=24)
        }
