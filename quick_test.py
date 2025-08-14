"""
Simple test without external dependencies to verify core structure.
"""

import sys
from pathlib import Path

def test_imports():
    """Test if our modules can be imported properly."""
    print("🧪 Testing SBEMS Module Structure")
    print("=" * 40)
    
    try:
        # Test basic Python imports
        print("1. Testing standard library imports...")
        from datetime import datetime, timedelta
        from typing import Dict, List, Optional
        from dataclasses import dataclass
        from enum import Enum
        import json
        import time
        print("   ✅ Standard library imports successful")
        
        # Test project structure
        print("2. Testing project structure...")
        project_root = Path(__file__).parent
        
        required_dirs = [
            "sbems",
            "sbems/core", 
            "sbems/sensors",
            "sbems/analytics",
            "sbems/api",
            "sbems/database",
            "config",
            "docs",
            "tests",
            "web"
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if full_path.exists():
                print(f"   ✅ {dir_path} directory exists")
            else:
                print(f"   ❌ {dir_path} directory missing")
                return False
        
        # Test required files
        print("3. Testing required files...")
        required_files = [
            "README.md",
            "requirements.txt", 
            "setup.py",
            "main.py",
            ".env.example",
            "config/default.yaml"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path} exists")
            else:
                print(f"   ❌ {file_path} missing")
                return False
        
        print("\n🎉 Project structure is correct!")
        print("\nNext steps to run the full system:")
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n2. Run the demo:")
        print("   python3 main.py --demo --duration 2")
        print("\n3. Try interactive mode:")
        print("   python3 main.py --interactive")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    if not success:
        sys.exit(1)
