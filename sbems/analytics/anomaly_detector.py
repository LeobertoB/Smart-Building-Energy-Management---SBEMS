"""
Advanced anomaly detection system based on Isolation Forest with energy-specific enhancements.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import warnings
from loguru import logger

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import networkx as nx

warnings.filterwarnings('ignore')


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    ENERGY_SPIKE = "energy_spike"
    EQUIPMENT_FAILURE = "equipment_failure"
    EFFICIENCY_DROP = "efficiency_drop"
    NETWORK_ISOLATION = "network_isolation"
    SEASONAL_DEVIATION = "seasonal_deviation"
    OCCUPANCY_MISMATCH = "occupancy_mismatch"
    UNKNOWN = "unknown"


class SeverityLevel(Enum):
    """Severity levels for anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    sensor_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    value: float
    expected_range: Tuple[float, float]
    description: str
    recommendations: List[str]
    metadata: Dict[str, Any]


class AnomalyDetector:
    """
    Advanced anomaly detection system for smart building energy management.
    
    This is an enhanced version of the original SensorNetworkMonitor that includes:
    - Multiple ML algorithms for different anomaly types
    - Energy-specific detection rules
    - Predictive maintenance capabilities
    - Network topology analysis
    - Seasonal and temporal pattern recognition
    """
    
    def __init__(
        self,
        window_size: int = 50,
        contamination: float = 0.05,
        min_samples_for_detection: int = 20,
        network_analysis: bool = True
    ):
        """
        Initialize the anomaly detection system.
        
        Args:
            window_size: Number of recent readings to consider
            contamination: Expected proportion of outliers
            min_samples_for_detection: Minimum samples needed before detection
            network_analysis: Whether to perform network topology analysis
        """
        self.window_size = window_size
        self.contamination = contamination
        self.min_samples_for_detection = min_samples_for_detection
        self.network_analysis = network_analysis
        
        # Detection models
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
        # Data storage
        self.sensor_data: Dict[str, List[Dict]] = {}
        self.detected_anomalies: List[Anomaly] = []
        self.network_graph: Optional[nx.Graph] = None
        
        # Energy-specific thresholds
        self.energy_spike_threshold = 2.0  # Standard deviations
        self.efficiency_drop_threshold = 0.3  # 30% efficiency drop
        self.occupancy_energy_ratio_threshold = 0.5  # Energy per person ratio
        
        logger.info("Initialized Advanced Anomaly Detection System")
    
    def add_sensor_reading(
        self,
        sensor_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
        sensor_type: str = "unknown",
        zone_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a new sensor reading to the detection system."""
        if timestamp is None:
            timestamp = datetime.now()
        
        reading = {
            "timestamp": timestamp,
            "value": value,
            "sensor_type": sensor_type,
            "zone_id": zone_id,
            "metadata": metadata or {}
        }
        
        if sensor_id not in self.sensor_data:
            self.sensor_data[sensor_id] = []
        
        self.sensor_data[sensor_id].append(reading)
        
        # Limit history size
        if len(self.sensor_data[sensor_id]) > self.window_size:
            self.sensor_data[sensor_id].pop(0)
    
    def detect_anomalies(self, sensor_ids: Optional[List[str]] = None) -> List[Anomaly]:
        """
        Detect anomalies across all sensors or specified sensors.
        
        Args:
            sensor_ids: List of sensor IDs to analyze (None = all sensors)
            
        Returns:
            List of detected anomalies
        """
        if sensor_ids is None:
            sensor_ids = list(self.sensor_data.keys())
        
        detected_anomalies = []
        
        for sensor_id in sensor_ids:
            if len(self.sensor_data[sensor_id]) < self.min_samples_for_detection:
                continue
            
            # Run different detection methods
            anomalies = []
            
            # 1. Isolation Forest (general anomaly detection)
            isolation_anomalies = self._detect_isolation_forest_anomalies(sensor_id)
            anomalies.extend(isolation_anomalies)
            
            # 2. Energy-specific detection
            energy_anomalies = self._detect_energy_anomalies(sensor_id)
            anomalies.extend(energy_anomalies)
            
            # 3. Temporal pattern detection
            temporal_anomalies = self._detect_temporal_anomalies(sensor_id)
            anomalies.extend(temporal_anomalies)
            
            # 4. Cross-sensor correlation analysis
            correlation_anomalies = self._detect_correlation_anomalies(sensor_id)
            anomalies.extend(correlation_anomalies)
            
            detected_anomalies.extend(anomalies)
        
        # 5. Network topology analysis (if enabled)
        if self.network_analysis and self.network_graph:
            network_anomalies = self._detect_network_anomalies()
            detected_anomalies.extend(network_anomalies)
        
        # Store detected anomalies
        self.detected_anomalies.extend(detected_anomalies)
        
        # Sort by severity and timestamp
        detected_anomalies.sort(key=lambda x: (x.severity.value, x.timestamp), reverse=True)
        
        logger.info(f"Detected {len(detected_anomalies)} anomalies")
        return detected_anomalies
    
    def _detect_isolation_forest_anomalies(self, sensor_id: str) -> List[Anomaly]:
        """Detect anomalies using Isolation Forest algorithm."""
        readings = self.sensor_data[sensor_id]
        values = np.array([r["value"] for r in readings]).reshape(-1, 1)
        
        # Fit and predict
        predictions = self.isolation_forest.fit_predict(values)
        anomaly_scores = self.isolation_forest.decision_function(values)
        
        anomalies = []
        for i, (prediction, score, reading) in enumerate(zip(predictions, anomaly_scores, readings)):
            if prediction == -1:  # Anomaly detected
                confidence = min(1.0, abs(score) / 0.5)  # Normalize score to confidence
                severity = self._calculate_severity(confidence, reading["value"], readings)
                
                anomaly = Anomaly(
                    sensor_id=sensor_id,
                    anomaly_type=AnomalyType.UNKNOWN,
                    severity=severity,
                    confidence=confidence,
                    timestamp=reading["timestamp"],
                    value=reading["value"],
                    expected_range=self._calculate_expected_range(readings),
                    description=f"Isolation Forest detected anomaly (score: {score:.3f})",
                    recommendations=["Investigate sensor reading", "Check equipment status"],
                    metadata={"algorithm": "isolation_forest", "score": score}
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_energy_anomalies(self, sensor_id: str) -> List[Anomaly]:
        """Detect energy-specific anomalies."""
        readings = self.sensor_data[sensor_id]
        latest_reading = readings[-1]
        
        # Only analyze energy-related sensors
        if not self._is_energy_sensor(latest_reading["sensor_type"]):
            return []
        
        anomalies = []
        values = [r["value"] for r in readings]
        
        # Energy spike detection
        if len(values) >= 10:
            recent_mean = np.mean(values[-10:])
            historical_mean = np.mean(values[:-10]) if len(values) > 10 else recent_mean
            historical_std = np.std(values[:-10]) if len(values) > 10 else np.std(values)
            
            if historical_std > 0:
                z_score = (recent_mean - historical_mean) / historical_std
                
                if abs(z_score) > self.energy_spike_threshold:
                    severity = SeverityLevel.HIGH if abs(z_score) > 3.0 else SeverityLevel.MEDIUM
                    
                    anomaly = Anomaly(
                        sensor_id=sensor_id,
                        anomaly_type=AnomalyType.ENERGY_SPIKE,
                        severity=severity,
                        confidence=min(1.0, abs(z_score) / 3.0),
                        timestamp=latest_reading["timestamp"],
                        value=latest_reading["value"],
                        expected_range=(historical_mean - 2*historical_std, historical_mean + 2*historical_std),
                        description=f"Energy spike detected (z-score: {z_score:.2f})",
                        recommendations=[
                            "Check for equipment malfunction",
                            "Verify load connections",
                            "Investigate unusual usage patterns"
                        ],
                        metadata={"z_score": z_score, "historical_mean": historical_mean}
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_temporal_anomalies(self, sensor_id: str) -> List[Anomaly]:
        """Detect anomalies based on temporal patterns."""
        readings = self.sensor_data[sensor_id]
        
        if len(readings) < 24:  # Need at least 24 readings for temporal analysis
            return []
        
        anomalies = []
        
        # Convert to DataFrame for easier time-based analysis
        df = pd.DataFrame(readings)
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.weekday
        
        # Detect anomalies in hourly patterns
        hourly_patterns = df.groupby('hour')['value'].agg(['mean', 'std']).fillna(0)
        
        latest_reading = readings[-1]
        current_hour = latest_reading["timestamp"].hour
        
        if current_hour in hourly_patterns.index:
            expected_mean = hourly_patterns.loc[current_hour, 'mean']
            expected_std = hourly_patterns.loc[current_hour, 'std']
            
            if expected_std > 0:
                deviation = abs(latest_reading["value"] - expected_mean) / expected_std
                
                if deviation > 2.5:  # Significant deviation from hourly pattern
                    severity = SeverityLevel.HIGH if deviation > 4.0 else SeverityLevel.MEDIUM
                    
                    anomaly = Anomaly(
                        sensor_id=sensor_id,
                        anomaly_type=AnomalyType.SEASONAL_DEVIATION,
                        severity=severity,
                        confidence=min(1.0, deviation / 4.0),
                        timestamp=latest_reading["timestamp"],
                        value=latest_reading["value"],
                        expected_range=(expected_mean - 2*expected_std, expected_mean + 2*expected_std),
                        description=f"Unusual value for time of day (deviation: {deviation:.2f}σ)",
                        recommendations=[
                            "Compare with historical patterns",
                            "Check for schedule changes",
                            "Verify sensor calibration"
                        ],
                        metadata={"hourly_deviation": deviation, "expected_mean": expected_mean}
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_correlation_anomalies(self, sensor_id: str) -> List[Anomaly]:
        """Detect anomalies based on correlations with other sensors."""
        if len(self.sensor_data) < 2:
            return []
        
        anomalies = []
        target_readings = self.sensor_data[sensor_id]
        target_zone = target_readings[-1].get("zone_id")
        
        # Find correlated sensors (same zone or similar type)
        correlated_sensors = []
        for other_id, other_readings in self.sensor_data.items():
            if other_id == sensor_id or len(other_readings) < self.min_samples_for_detection:
                continue
            
            # Check if sensors are related
            other_zone = other_readings[-1].get("zone_id")
            if target_zone and other_zone == target_zone:
                correlated_sensors.append(other_id)
        
        if not correlated_sensors:
            return []
        
        # Analyze correlation patterns
        for other_id in correlated_sensors:
            anomaly = self._analyze_sensor_correlation(sensor_id, other_id)
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies
    
    def _analyze_sensor_correlation(self, sensor1_id: str, sensor2_id: str) -> Optional[Anomaly]:
        """Analyze correlation between two sensors."""
        readings1 = self.sensor_data[sensor1_id]
        readings2 = self.sensor_data[sensor2_id]
        
        # Align timestamps and get common readings
        common_readings = self._align_sensor_readings(readings1, readings2)
        
        if len(common_readings) < 10:
            return None
        
        values1 = [r[0] for r in common_readings]
        values2 = [r[1] for r in common_readings]
        
        # Calculate correlation
        correlation = np.corrcoef(values1, values2)[0, 1]
        
        if np.isnan(correlation):
            return None
        
        # Detect sudden correlation breakdown
        recent_corr = np.corrcoef(values1[-10:], values2[-10:])[0, 1]
        
        if not np.isnan(recent_corr) and abs(correlation - recent_corr) > 0.5:
            latest_reading = readings1[-1]
            
            return Anomaly(
                sensor_id=sensor1_id,
                anomaly_type=AnomalyType.NETWORK_ISOLATION,
                severity=SeverityLevel.MEDIUM,
                confidence=abs(correlation - recent_corr),
                timestamp=latest_reading["timestamp"],
                value=latest_reading["value"],
                expected_range=self._calculate_expected_range(readings1),
                description=f"Correlation breakdown with sensor {sensor2_id}",
                recommendations=[
                    "Check sensor connectivity",
                    "Verify both sensors are operational",
                    "Investigate environmental changes"
                ],
                metadata={
                    "historical_correlation": correlation,
                    "recent_correlation": recent_corr,
                    "correlated_sensor": sensor2_id
                }
            )
        
        return None
    
    def _detect_network_anomalies(self) -> List[Anomaly]:
        """Detect network-level anomalies using graph analysis."""
        if not self.network_graph:
            return []
        
        anomalies = []
        
        # Analyze network connectivity
        isolated_nodes = []
        for node in self.network_graph.nodes():
            if self.network_graph.degree(node) == 0:
                isolated_nodes.append(node)
        
        # Create anomalies for isolated sensors
        for sensor_id in isolated_nodes:
            if sensor_id in self.sensor_data and self.sensor_data[sensor_id]:
                latest_reading = self.sensor_data[sensor_id][-1]
                
                anomaly = Anomaly(
                    sensor_id=sensor_id,
                    anomaly_type=AnomalyType.NETWORK_ISOLATION,
                    severity=SeverityLevel.HIGH,
                    confidence=1.0,
                    timestamp=latest_reading["timestamp"],
                    value=latest_reading["value"],
                    expected_range=self._calculate_expected_range(self.sensor_data[sensor_id]),
                    description="Sensor isolated from network",
                    recommendations=[
                        "Check network connectivity",
                        "Verify sensor power supply",
                        "Inspect physical connections"
                    ],
                    metadata={"network_degree": 0}
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def update_network_graph(self, building) -> None:
        """Update the network graph from a building object."""
        if hasattr(building, 'get_sensor_network_graph'):
            self.network_graph = building.get_sensor_network_graph()
            logger.debug("Updated sensor network graph")
    
    def _align_sensor_readings(self, readings1: List[Dict], readings2: List[Dict]) -> List[Tuple[float, float]]:
        """Align readings from two sensors by timestamp."""
        aligned = []
        
        # Create timestamp-indexed dictionaries
        dict1 = {r["timestamp"]: r["value"] for r in readings1}
        dict2 = {r["timestamp"]: r["value"] for r in readings2}
        
        # Find common timestamps (within 1 minute tolerance)
        for ts1, val1 in dict1.items():
            for ts2, val2 in dict2.items():
                if abs((ts1 - ts2).total_seconds()) <= 60:  # 1 minute tolerance
                    aligned.append((val1, val2))
                    break
        
        return aligned
    
    def _is_energy_sensor(self, sensor_type: str) -> bool:
        """Check if sensor type is energy-related."""
        energy_types = ["energy_power", "energy_voltage", "energy_current", "energy_total"]
        return sensor_type in energy_types
    
    def _calculate_severity(self, confidence: float, value: float, readings: List[Dict]) -> SeverityLevel:
        """Calculate severity level based on confidence and value deviation."""
        if confidence > 0.8:
            return SeverityLevel.CRITICAL
        elif confidence > 0.6:
            return SeverityLevel.HIGH
        elif confidence > 0.4:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def _calculate_expected_range(self, readings: List[Dict]) -> Tuple[float, float]:
        """Calculate expected range based on historical data."""
        values = [r["value"] for r in readings]
        mean = np.mean(values)
        std = np.std(values)
        return (mean - 2*std, mean + 2*std)
    
    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of anomalies in the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_anomalies = [
            a for a in self.detected_anomalies
            if a.timestamp >= cutoff_time
        ]
        
        summary = {
            "total_anomalies": len(recent_anomalies),
            "by_severity": {
                level.value: len([a for a in recent_anomalies if a.severity == level])
                for level in SeverityLevel
            },
            "by_type": {
                atype.value: len([a for a in recent_anomalies if a.anomaly_type == atype])
                for atype in AnomalyType
            },
            "most_recent": recent_anomalies[0].timestamp.isoformat() if recent_anomalies else None,
            "critical_sensors": list(set([
                a.sensor_id for a in recent_anomalies 
                if a.severity == SeverityLevel.CRITICAL
            ]))
        }
        
        return summary
    
    def clear_old_anomalies(self, days: int = 7) -> int:
        """Clear anomalies older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=days)
        initial_count = len(self.detected_anomalies)
        
        self.detected_anomalies = [
            a for a in self.detected_anomalies
            if a.timestamp >= cutoff_time
        ]
        
        removed_count = initial_count - len(self.detected_anomalies)
        logger.info(f"Removed {removed_count} old anomalies")
        return removed_count
