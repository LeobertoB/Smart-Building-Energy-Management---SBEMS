#!/bin/bash

# SBEMS Deployment Script
# This script automates the deployment of the Smart Building Energy Management System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.9"
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        error "Python 3.9+ is required. Current version: $python_version"
        exit 1
    fi
    
    # Check pip
    if ! command_exists pip3; then
        error "pip3 is required but not installed."
        exit 1
    fi
    
    # Check Git
    if ! command_exists git; then
        warn "Git is not installed. Version control features will be limited."
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        info "Docker found - containerized deployment available"
    else
        warn "Docker not found - containerized deployment not available"
    fi
    
    log "System requirements check completed ✓"
}

# Function to setup virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "Virtual environment created"
    else
        info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    log "Virtual environment setup completed ✓"
}

# Function to install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log "Dependencies installed successfully ✓"
    else
        error "requirements.txt not found"
        exit 1
    fi
}

# Function to setup configuration
setup_config() {
    log "Setting up configuration..."
    
    # Create config directory if it doesn't exist
    mkdir -p config
    
    # Create default configuration if it doesn't exist
    if [ ! -f "config/config.yaml" ]; then
        cat > config/config.yaml << EOF
# SBEMS Configuration
system:
  name: "Default Building"
  location: "Demo Location"
  timezone: "UTC"

monitoring:
  interval: 5  # seconds
  data_retention_days: 30
  max_sensors_per_zone: 20

sensors:
  hvac:
    enabled: true
    min_temp: 18.0
    max_temp: 26.0
  lighting:
    enabled: true
    auto_dimming: true
  occupancy:
    enabled: true
    max_capacity: 100
  energy:
    enabled: true
    peak_hours: [9, 17]

anomaly_detection:
  contamination: 0.1
  min_samples: 100
  alert_threshold: 0.8

logging:
  level: "INFO"
  file: "logs/sbems.log"
  max_size_mb: 10
  backup_count: 5

database:
  type: "sqlite"  # sqlite, postgresql
  path: "data/sbems.db"
  # host: "localhost"
  # port: 5432
  # name: "sbems_db"
  # user: "sbems"
  # password: "password"
EOF
        log "Default configuration created"
    else
        info "Configuration file already exists"
    fi
    
    # Create necessary directories
    mkdir -p logs data exports
    
    log "Configuration setup completed ✓"
}

# Function to run tests
run_tests() {
    log "Running system tests..."
    
    # Basic import test
    python3 -c "
import sys
sys.path.append('.')
try:
    from sbems.core.building import Building
    from sbems.core.monitoring_system import MonitoringSystem
    from sbems.analytics.anomaly_detector import AnomalyDetector
    print('✓ Core modules import successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    # Run unit tests if available
    if [ -d "tests" ]; then
        python3 -m pytest tests/ -v || warn "Some tests failed"
    fi
    
    log "Tests completed ✓"
}

# Function to start the system
start_system() {
    log "Starting SBEMS..."
    
    info "You can now run the system with:"
    echo "  Demo mode:        python3 main.py --demo --duration 2"
    echo "  Interactive mode: python3 main.py --interactive"
    echo "  Monitor mode:     python3 main.py --monitor --duration 300"
    echo ""
    echo "Configuration file: config/config.yaml"
    echo "Logs directory:     logs/"
    echo "Data directory:     data/"
    echo ""
}

# Function for Docker deployment
docker_deploy() {
    log "Starting Docker deployment..."
    
    if ! command_exists docker; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Build and start containers
    docker-compose up --build -d
    
    log "Docker deployment completed ✓"
    info "Services available at:"
    echo "  SBEMS Application: http://localhost:5000"
    echo "  Grafana Dashboard: http://localhost:3000 (admin/admin)"
    echo "  Prometheus:        http://localhost:9090"
}

# Function to show help
show_help() {
    echo "SBEMS Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h        Show this help message"
    echo "  --docker, -d      Deploy using Docker Compose"
    echo "  --test-only, -t   Only run tests, don't start system"
    echo "  --no-venv         Skip virtual environment setup"
    echo "  --skip-tests      Skip running tests"
    echo ""
    echo "Examples:"
    echo "  $0                 # Standard deployment"
    echo "  $0 --docker        # Docker deployment"
    echo "  $0 --test-only     # Run tests only"
}

# Main deployment function
main() {
    echo "=========================================="
    echo "Smart Building Energy Management System"
    echo "Deployment Script"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    DOCKER_DEPLOY=false
    TEST_ONLY=false
    USE_VENV=true
    RUN_TESTS=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --docker|-d)
                DOCKER_DEPLOY=true
                shift
                ;;
            --test-only|-t)
                TEST_ONLY=true
                shift
                ;;
            --no-venv)
                USE_VENV=false
                shift
                ;;
            --skip-tests)
                RUN_TESTS=false
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -d "sbems" ]; then
        error "Please run this script from the SBEMS project root directory"
        exit 1
    fi
    
    # Docker deployment
    if [ "$DOCKER_DEPLOY" = true ]; then
        check_requirements
        docker_deploy
        exit 0
    fi
    
    # Standard deployment
    check_requirements
    
    if [ "$USE_VENV" = true ]; then
        setup_venv
    fi
    
    install_dependencies
    setup_config
    
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    if [ "$TEST_ONLY" = false ]; then
        start_system
    fi
    
    log "Deployment completed successfully! 🚀"
}

# Run main function
main "$@"
