"""
Main entry point for the Smart Building Energy Management System.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Tuple
import random

from loguru import logger

from sbems.core.building import Building, Zone, BuildingInfo
from sbems.core.monitoring_system import MonitoringSystem, MonitoringConfig
from sbems.sensors.hvac_sensor import HVACSensor
from sbems.sensors.lighting_sensor import LightingSensor
from sbems.sensors.occupancy_sensor import OccupancySensor
from sbems.sensors.energy_meter import EnergyMeter


def create_demo_building() -> Building:
    """Create a comprehensive demo building with realistic sensors."""
    
    # Building information
    building_info = BuildingInfo(
        name="TechCorp Headquarters",
        address="123 Innovation Drive, Tech City, TC 12345",
        total_area=5000.0,  # 5000 square meters
        floors=3,
        building_type="office",
        year_built=2020,
        energy_rating="B",
        timezone="UTC"
    )
    
    building = Building(building_info)
    logger.info(f"Created building: {building_info.name}")
    
    # Define zones
    zones = [
        # Floor 1
        Zone("zone_001", "Main Lobby", 200.0, 1, "lobby", 50, (25.0, 25.0, 0.0)),
        Zone("zone_002", "Conference Room A", 100.0, 1, "meeting_room", 20, (10.0, 10.0, 0.0)),
        Zone("zone_003", "Open Office 1A", 300.0, 1, "office", 40, (30.0, 30.0, 0.0)),
        Zone("zone_004", "Kitchen", 80.0, 1, "kitchen", 15, (15.0, 15.0, 0.0)),
        Zone("zone_005", "Server Room", 50.0, 1, "server_room", 5, (10.0, 10.0, 0.0)),
        
        # Floor 2
        Zone("zone_006", "Open Office 2A", 400.0, 2, "office", 50, (40.0, 40.0, 3.0)),
        Zone("zone_007", "Open Office 2B", 400.0, 2, "office", 50, (40.0, 60.0, 3.0)),
        Zone("zone_008", "Conference Room B", 120.0, 2, "meeting_room", 25, (20.0, 20.0, 3.0)),
        Zone("zone_009", "Break Room", 60.0, 2, "break_room", 10, (12.0, 12.0, 3.0)),
        
        # Floor 3
        Zone("zone_010", "Executive Offices", 300.0, 3, "office", 20, (30.0, 30.0, 6.0)),
        Zone("zone_011", "Board Room", 150.0, 3, "meeting_room", 30, (25.0, 25.0, 6.0)),
        Zone("zone_012", "Storage", 100.0, 3, "storage", 5, (15.0, 15.0, 6.0)),
    ]
    
    # Add zones to building
    for zone in zones:
        building.add_zone(zone)
    
    # Add sensors to zones
    sensor_counter = 1
    
    for zone in zones:
        logger.info(f"Adding sensors to zone: {zone.name}")
        
        # Add HVAC sensors (temperature, humidity, air quality)
        hvac_sensors = [
            HVACSensor(
                hvac_type="temperature",
                sensor_id=f"hvac_temp_{sensor_counter:03d}",
                position=(zone.position[0] + random.uniform(-5, 5), 
                         zone.position[1] + random.uniform(-5, 5), 
                         zone.position[2] + 2.5),
                name=f"Temperature - {zone.name}"
            ),
            HVACSensor(
                hvac_type="humidity",
                sensor_id=f"hvac_humid_{sensor_counter:03d}",
                position=(zone.position[0] + random.uniform(-5, 5), 
                         zone.position[1] + random.uniform(-5, 5), 
                         zone.position[2] + 2.5),
                name=f"Humidity - {zone.name}"
            ),
            HVACSensor(
                hvac_type="air_quality",
                sensor_id=f"hvac_aqi_{sensor_counter:03d}",
                position=(zone.position[0] + random.uniform(-5, 5), 
                         zone.position[1] + random.uniform(-5, 5), 
                         zone.position[2] + 2.5),
                name=f"Air Quality - {zone.name}"
            )
        ]
        
        # Add lighting sensors
        lighting_sensors = [
            LightingSensor(
                lighting_type="illuminance",
                sensor_id=f"light_lux_{sensor_counter:03d}",
                position=(zone.position[0], zone.position[1], zone.position[2] + 2.8),
                name=f"Illuminance - {zone.name}"
            ),
            LightingSensor(
                lighting_type="energy",
                sensor_id=f"light_energy_{sensor_counter:03d}",
                position=(zone.position[0], zone.position[1], zone.position[2] + 3.0),
                name=f"Lighting Energy - {zone.name}"
            )
        ]
        
        # Add occupancy sensors
        occupancy_sensors = [
            OccupancySensor(
                occupancy_type="people_count",
                max_occupancy=zone.max_occupancy,
                sensor_id=f"occupancy_count_{sensor_counter:03d}",
                position=(zone.position[0], zone.position[1], zone.position[2] + 2.2),
                name=f"People Count - {zone.name}"
            ),
            OccupancySensor(
                occupancy_type="motion",
                max_occupancy=zone.max_occupancy,
                sensor_id=f"occupancy_motion_{sensor_counter:03d}",
                position=(zone.position[0] + 2, zone.position[1] + 2, zone.position[2] + 2.5),
                name=f"Motion Detection - {zone.name}"
            )
        ]
        
        # Add energy meters
        circuit_capacity = zone.area * 20  # 20W per square meter baseline
        if zone.zone_type == "server_room":
            circuit_capacity *= 10  # Server rooms use much more power
        elif zone.zone_type == "kitchen":
            circuit_capacity *= 3  # Kitchens use more power
        
        energy_sensors = [
            EnergyMeter(
                meter_type="power",
                circuit_capacity=circuit_capacity,
                sensor_id=f"energy_power_{sensor_counter:03d}",
                position=(zone.position[0] - 2, zone.position[1] - 2, zone.position[2]),
                name=f"Power Meter - {zone.name}"
            ),
            EnergyMeter(
                meter_type="voltage",
                circuit_capacity=circuit_capacity,
                sensor_id=f"energy_voltage_{sensor_counter:03d}",
                position=(zone.position[0] - 2, zone.position[1] - 2, zone.position[2] + 0.5),
                name=f"Voltage Meter - {zone.name}"
            )
        ]
        
        # Add all sensors to the zone and building
        all_sensors = hvac_sensors + lighting_sensors + occupancy_sensors + energy_sensors
        
        for sensor in all_sensors:
            building.add_sensor(sensor, zone.id)
        
        sensor_counter += 1
    
    logger.info(f"Created demo building with {len(building.sensors)} sensors across {len(building.zones)} zones")
    return building


def run_demo(duration_minutes: int = 10, sampling_interval: int = 30) -> None:
    """Run a demonstration of the monitoring system."""
    
    logger.info("🏢 Starting Smart Building Energy Management System Demo")
    logger.info("=" * 60)
    
    # Create demo building
    building = create_demo_building()
    
    # Print building summary
    summary = building.get_building_summary()
    logger.info("Building Summary:")
    logger.info(f"  Name: {summary['building_info']['name']}")
    logger.info(f"  Total Area: {summary['building_info']['total_area']} m²")
    logger.info(f"  Floors: {summary['building_info']['floors']}")
    logger.info(f"  Zones: {summary['zones']['total_zones']}")
    logger.info(f"  Sensors: {summary['sensors']['total_sensors']}")
    logger.info("")
    
    # Configure monitoring
    config = MonitoringConfig(
        sampling_interval=sampling_interval,
        anomaly_check_interval=sampling_interval * 2,
        auto_start=True,
        save_history=True,
        enable_alerts=True,
        alert_threshold="medium"
    )
    
    # Initialize monitoring system
    monitoring = MonitoringSystem(building, config)
    
    try:
        # Start monitoring
        monitoring.start_monitoring()
        logger.info(f"🚀 Monitoring started (running for {duration_minutes} minutes)")
        logger.info(f"📊 Sampling every {sampling_interval} seconds")
        logger.info("=" * 60)
        
        # Run for specified duration
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        step_count = 0
        while time.time() < end_time:
            time.sleep(10)  # Check every 10 seconds
            
            step_count += 1
            
            # Print status every minute
            if step_count % 6 == 0:  # Every 60 seconds (6 * 10s)
                status = monitoring.get_current_status()
                dashboard_data = monitoring.get_dashboard_data()
                
                logger.info(f"⚡ Status Update (Runtime: {status['runtime_seconds']:.0f}s)")
                logger.info(f"   📈 Readings: {status['total_readings']}")
                logger.info(f"   🚨 Anomalies: {status['total_anomalies']}")
                logger.info(f"   👥 Occupancy: {dashboard_data['building']['occupancy']} people")
                logger.info(f"   ⚡ Energy: {dashboard_data['building']['energy_consumption']:.1f} W")
                logger.info(f"   🔍 Sensor Health: {dashboard_data['sensors']['health_percentage']:.1f}%")
                
                recent_alerts = monitoring.get_recent_alerts(hours=1)
                if recent_alerts:
                    logger.warning(f"   🚨 Recent Alerts: {len(recent_alerts)}")
                    for alert in recent_alerts[-3:]:  # Show last 3 alerts
                        logger.warning(f"      [{alert['severity'].upper()}] {alert['description']}")
                
                logger.info("")
        
        logger.info("🏁 Demo completed!")
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    
    finally:
        # Stop monitoring and export data
        monitoring.stop_monitoring()
        
        # Export demo data
        export_path = f"demo_export_{int(time.time())}.json"
        monitoring.export_data(export_path)
        logger.info(f"📄 Demo data exported to: {export_path}")
        
        # Print final summary
        final_status = monitoring.get_current_status()
        logger.info("")
        logger.info("📊 Final Summary:")
        logger.info(f"   Runtime: {final_status['runtime_seconds']:.0f} seconds")
        logger.info(f"   Total Readings: {final_status['total_readings']}")
        logger.info(f"   Total Anomalies: {final_status['total_anomalies']}")
        logger.info(f"   Sensors Monitored: {final_status['sensor_count']}")
        logger.info("")
        logger.info("🎉 Thank you for trying SBEMS!")


def run_interactive_mode() -> None:
    """Run in interactive mode for exploration."""
    logger.info("🔧 Interactive Mode - Smart Building Energy Management System")
    logger.info("Type 'help' for available commands")
    
    building = create_demo_building()
    config = MonitoringConfig(sampling_interval=5, auto_start=False)
    monitoring = MonitoringSystem(building, config)
    
    commands = {
        "start": "Start monitoring",
        "stop": "Stop monitoring", 
        "status": "Show current status",
        "sensors": "List all sensors",
        "readings": "Show recent readings",
        "alerts": "Show recent alerts",
        "step": "Take one monitoring step",
        "export": "Export data to file",
        "help": "Show this help",
        "quit": "Exit interactive mode"
    }
    
    while True:
        try:
            command = input("\nSBEMS> ").strip().lower()
            
            if command == "help":
                logger.info("Available commands:")
                for cmd, desc in commands.items():
                    logger.info(f"  {cmd:<10} - {desc}")
            
            elif command == "start":
                monitoring.start_monitoring()
                logger.info("Monitoring started")
            
            elif command == "stop":
                monitoring.stop_monitoring()
                logger.info("Monitoring stopped")
            
            elif command == "status":
                status = monitoring.get_current_status()
                dashboard = monitoring.get_dashboard_data()
                logger.info("Current Status:")
                for key, value in status.items():
                    logger.info(f"  {key}: {value}")
                logger.info(f"Building Occupancy: {dashboard['building']['occupancy']}")
                logger.info(f"Energy Consumption: {dashboard['building']['energy_consumption']:.1f} W")
            
            elif command == "sensors":
                logger.info(f"Total Sensors: {len(building.sensors)}")
                for sensor_id, sensor in list(building.sensors.items())[:10]:  # Show first 10
                    logger.info(f"  {sensor_id}: {sensor.sensor_type} ({sensor.name})")
                if len(building.sensors) > 10:
                    logger.info(f"  ... and {len(building.sensors) - 10} more")
            
            elif command == "readings":
                readings = monitoring.get_recent_readings(hours=1)
                logger.info(f"Recent readings (last hour): {len(readings)}")
                if readings:
                    latest = readings[-1]
                    logger.info(f"Latest reading timestamp: {latest['timestamp']}")
                    logger.info(f"Active sensors in latest reading: {len(latest['readings'])}")
            
            elif command == "alerts":
                alerts = monitoring.get_recent_alerts(hours=24)
                logger.info(f"Recent alerts (last 24h): {len(alerts)}")
                for alert in alerts[-5:]:  # Show last 5
                    logger.info(f"  [{alert['severity'].upper()}] {alert['sensor_id']}: {alert['description']}")
            
            elif command == "step":
                monitoring.simulate_step()
                logger.info("Monitoring step completed")
            
            elif command == "export":
                filename = f"interactive_export_{int(time.time())}.json"
                monitoring.export_data(filename)
                logger.info(f"Data exported to: {filename}")
            
            elif command in ["quit", "exit", "q"]:
                break
            
            elif command == "":
                continue
            
            else:
                logger.warning(f"Unknown command: {command}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    
    # Cleanup
    monitoring.stop_monitoring()
    logger.info("Goodbye!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Building Energy Management System (SBEMS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo                    # Run 10-minute demo
  python main.py --demo --duration 5      # Run 5-minute demo  
  python main.py --interactive             # Interactive mode
  python main.py --demo --interval 15     # Demo with 15s sampling
        """
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true", 
        help="Run demonstration mode"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--duration", 
        type=int, 
        default=10, 
        help="Demo duration in minutes (default: 10)"
    )
    
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30, 
        help="Sampling interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout, 
        level=args.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )
    
    # Run appropriate mode
    if args.demo:
        run_demo(duration_minutes=args.duration, sampling_interval=args.interval)
    elif args.interactive:
        run_interactive_mode()
    else:
        # Show help if no mode selected
        parser.print_help()
        logger.info("\nPlease specify --demo or --interactive mode")


if __name__ == "__main__":
    main()
