"""
Smart Building Energy Management System (SBEMS)

A comprehensive system for monitoring, analyzing, and optimizing energy consumption
in commercial and residential buildings using advanced machine learning techniques.

Author: Your Name
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"

# Import main classes when available
try:
    from sbems.core.building import Building
    from sbems.core.monitoring_system import MonitoringSystem
    from sbems.analytics.anomaly_detector import AnomalyDetector
    
    __all__ = [
        "Building",
        "MonitoringSystem", 
        "AnomalyDetector",
    ]
except ImportError:
    # Dependencies not yet installed
    pass
