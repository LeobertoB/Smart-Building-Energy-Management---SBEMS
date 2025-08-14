"""
Test the Smart Building Energy Management System functionality.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sbems.core.building import Building, Zone, BuildingInfo
from sbems.core.monitoring_system import MonitoringSystem, MonitoringConfig
from sbems.sensors.hvac_sensor import HVACSensor
from sbems.sensors.lighting_sensor import LightingSensor
from sbems.sensors.occupancy_sensor import OccupancySensor
from sbems.sensors.energy_meter import EnergyMeter


def test_basic_functionality():
    """Test basic SBEMS functionality without external dependencies."""
    print("🧪 Testing Smart Building Energy Management System")
    print("=" * 50)
    
    # Test 1: Create Building
    print("1. Creating test building...")
    building_info = BuildingInfo(
        name="Test Building",
        address="123 Test St",
        total_area=1000.0,
        floors=2,
        building_type="office",
        year_built=2023,
        energy_rating="A"
    )
    
    building = Building(building_info)
    assert building.info.name == "Test Building"
    print("   ✅ Building created successfully")
    
    # Test 2: Add Zone
    print("2. Adding test zone...")
    zone = Zone("test_zone", "Test Office", 100.0, 1, "office", 10, (10.0, 10.0, 0.0))
    building.add_zone(zone)
    assert len(building.zones) == 1
    print("   ✅ Zone added successfully")
    
    # Test 3: Add Sensors
    print("3. Adding sensors...")
    sensors = [
        HVACSensor(hvac_type="temperature", sensor_id="hvac_001", position=(5.0, 5.0, 2.5)),
        LightingSensor(lighting_type="illuminance", sensor_id="light_001", position=(5.0, 7.0, 2.8)),
        OccupancySensor(occupancy_type="people_count", max_occupancy=10, sensor_id="occ_001", position=(7.0, 5.0, 2.2)),
        EnergyMeter(meter_type="power", circuit_capacity=1000.0, sensor_id="energy_001", position=(3.0, 3.0, 0.0))
    ]
    
    for sensor in sensors:
        building.add_sensor(sensor, "test_zone")
    
    assert len(building.sensors) == 4
    print(f"   ✅ {len(sensors)} sensors added successfully")
    
    # Test 4: Sensor Readings
    print("4. Testing sensor readings...")
    for sensor_id, sensor in building.sensors.items():
        try:
            reading = sensor.take_reading()
            assert reading.value is not None
            assert reading.unit is not None
            print(f"   📊 {sensor.sensor_type}: {reading.value:.2f} {reading.unit}")
        except Exception as e:
            print(f"   ❌ Error reading sensor {sensor_id}: {e}")
            return False
    
    print("   ✅ All sensors readable")
    
    # Test 5: Building Summary
    print("5. Testing building summary...")
    summary = building.get_building_summary()
    assert summary["zones"]["total_zones"] == 1
    assert summary["sensors"]["total_sensors"] == 4
    print(f"   📈 Building has {summary['zones']['total_zones']} zones and {summary['sensors']['total_sensors']} sensors")
    print("   ✅ Building summary generated")
    
    # Test 6: Monitoring System (without anomaly detection to avoid sklearn dependency)
    print("6. Testing monitoring system...")
    config = MonitoringConfig(
        sampling_interval=1,
        anomaly_check_interval=5,
        auto_start=False,  # Manual control
        save_history=True
    )
    
    monitoring = MonitoringSystem(building, config)
    assert not monitoring.is_running
    print("   ✅ Monitoring system created")
    
    # Test 7: Manual monitoring steps
    print("7. Testing manual monitoring steps...")
    for i in range(3):
        monitoring.simulate_step()
        time.sleep(0.1)  # Small delay
    
    status = monitoring.get_current_status()
    assert status["total_readings"] > 0
    print(f"   📊 Collected {status['total_readings']} readings")
    print("   ✅ Manual monitoring steps completed")
    
    # Test 8: Data Export
    print("8. Testing data export...")
    export_file = "test_export.json"
    try:
        monitoring.export_data(export_file)
        
        # Check if file was created
        if Path(export_file).exists():
            print(f"   💾 Data exported to {export_file}")
            Path(export_file).unlink()  # Clean up
            print("   ✅ Export test completed")
        else:
            print("   ❌ Export file not created")
            return False
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        return False
    
    print("\n🎉 All tests passed! SBEMS is working correctly.")
    return True


def test_sensor_types():
    """Test different sensor types and their readings."""
    print("\n🔬 Testing Individual Sensor Types")
    print("=" * 40)
    
    # Test HVAC sensors
    print("Testing HVAC Sensors:")
    hvac_types = ["temperature", "humidity", "air_quality", "pressure"]
    for hvac_type in hvac_types:
        sensor = HVACSensor(hvac_type=hvac_type, sensor_id=f"hvac_{hvac_type}")
        reading = sensor.take_reading()
        print(f"  {hvac_type}: {reading.value:.2f} {reading.unit}")
    
    # Test Lighting sensors
    print("\nTesting Lighting Sensors:")
    lighting_types = ["illuminance", "energy", "dimmer_level"]
    for lighting_type in lighting_types:
        sensor = LightingSensor(lighting_type=lighting_type, sensor_id=f"light_{lighting_type}")
        reading = sensor.take_reading()
        print(f"  {lighting_type}: {reading.value:.2f} {reading.unit}")
    
    # Test Occupancy sensors
    print("\nTesting Occupancy Sensors:")
    occupancy_types = ["people_count", "motion", "presence"]
    for occupancy_type in occupancy_types:
        sensor = OccupancySensor(occupancy_type=occupancy_type, sensor_id=f"occ_{occupancy_type}")
        reading = sensor.take_reading()
        print(f"  {occupancy_type}: {reading.value:.2f} {reading.unit}")
    
    # Test Energy meters
    print("\nTesting Energy Meters:")
    energy_types = ["power", "voltage", "current", "power_factor"]
    for energy_type in energy_types:
        sensor = EnergyMeter(meter_type=energy_type, sensor_id=f"energy_{energy_type}")
        reading = sensor.take_reading()
        print(f"  {energy_type}: {reading.value:.2f} {reading.unit}")
    
    print("\n✅ All sensor types working correctly")


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        
        if success:
            test_sensor_types()
            print("\n🚀 SBEMS is ready for deployment!")
            print("\nNext steps:")
            print("1. Install dependencies: pip install -r requirements.txt")
            print("2. Run demo: python main.py --demo")
            print("3. Try interactive mode: python main.py --interactive")
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
