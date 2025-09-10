#!/bin/bash

# AI-based Rockfall Prediction System Deployment Script
# Author: Omar H. Hashmi
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="ai-rockfall-system"
DOCKER_IMAGE_NAME="rockfall-prediction"
DOCKER_TAG="latest"

# Check if required tools are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+="python3"
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        missing_deps+="pip"
    fi
    
    # Check Docker (optional but recommended)
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Docker deployment will not be available."
    fi
    
    # Check Docker Compose (optional)
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose not found. Multi-container deployment will not be available."
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    log_success "All required dependencies are installed."
}

# Create project structure
create_project_structure() {
    log_info "Creating project structure..."
    
    # Create directories
    mkdir -p data/{sensors,DroneImages/FilteredData/{Images,Masks,BinaryMasks}}
    mkdir -p ml/artifacts
    mkdir -p logs
    mkdir -p backup
    mkdir -p ssl
    
    log_success "Project structure created."
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
        log_success "Python dependencies installed."
    else
        log_error "requirements.txt not found!"
        exit 1
    fi
}

# Generate sample data
generate_sample_data() {
    log_info "Generating sample data..."
    
    if [ -f "scripts/seed_sensors.py" ]; then
        python scripts/seed_sensors.py --duration 168 --frequency 60
        log_success "Sample data generated."
    else
        log_warning "Seed script not found. Skipping data generation."
    fi
}

# Train the model
train_model() {
    log_info "Training the machine learning model..."
    
    if [ -f "ml/train.py" ]; then
        cd ml
        python train.py
        cd ..
        log_success "Model training completed."
    else
        log_error "Training script not found!"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Created .env from .env.example. Please configure your API keys and settings."
        else
            log_error ".env.example not found!"
            exit 1
        fi
    else
        log_info ".env file already exists."
    fi
}

# Docker deployment
docker_deploy() {
    log_info "Building Docker image..."
    
    if command -v docker &> /dev/null; then
        # Build Docker image
        docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} .
        log_success "Docker image built successfully."
        
        # Start with Docker Compose if available
        if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
            log_info "Starting services with Docker Compose..."
            docker-compose up -d
            log_success "Services started with Docker Compose."
            
            # Show service status
            echo ""
            log_info "Service URLs:"
            echo "  🎨 Frontend: http://localhost:8501"
            echo "  🔧 API: http://localhost:8000"
            echo "  📚 API Docs: http://localhost:8000/docs"
            echo "  🗄️ MongoDB: mongodb://localhost:27017"
            
        else
            log_warning "Docker Compose not available. Use individual Docker commands."
        fi
    else
        log_warning "Docker not available. Skipping Docker deployment."
    fi
}

# Native deployment
native_deploy() {
    log_info "Starting native deployment..."
    
    # Start MongoDB if not running
    if ! pgrep mongod > /dev/null; then
        log_warning "MongoDB not running. Please start MongoDB manually:"
        echo "  Docker: docker run -d -p 27017:27017 --name mongodb mongo:5.0"
        echo "  Native: sudo systemctl start mongod"
    fi
    
    # Start API in background
    log_info "Starting FastAPI backend..."
    nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
    API_PID=$!
    echo $API_PID > .api.pid
    
    # Wait a moment for API to start
    sleep 5
    
    # Check if API is running
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        log_success "API started successfully (PID: $API_PID)"
    else
        log_error "Failed to start API"
        exit 1
    fi
    
    # Start Streamlit frontend
    log_info "Starting Streamlit frontend..."
    nohup streamlit run streamlit_app/app.py --server.address 0.0.0.0 --server.port 8501 > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend.pid
    
    # Wait a moment for frontend to start
    sleep 10
    
    # Check if frontend is running
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        log_success "Frontend started successfully (PID: $FRONTEND_PID)"
    else
        log_error "Failed to start frontend"
        exit 1
    fi
    
    echo ""
    log_success "🎉 Native deployment completed!"
    echo ""
    log_info "Service URLs:"
    echo "  🎨 Frontend: http://localhost:8501"
    echo "  🔧 API: http://localhost:8000"
    echo "  📚 API Docs: http://localhost:8000/docs"
    echo ""
    log_info "To stop services:"
    echo "  kill \$(cat .api.pid) \$(cat .frontend.pid)"
    echo "  rm .api.pid .frontend.pid"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    # Stop Docker Compose services
    if [ -f "docker-compose.yml" ] && command -v docker-compose &> /dev/null; then
        docker-compose down
        log_success "Docker Compose services stopped."
    fi
    
    # Stop native services
    if [ -f ".api.pid" ]; then
        kill $(cat .api.pid) 2>/dev/null || true
        rm .api.pid
        log_success "API service stopped."
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
        log_success "Frontend service stopped."
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    local api_healthy=false
    local frontend_healthy=false
    
    # Check API
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        api_healthy=true
        log_success "✅ API is healthy"
    else
        log_error "❌ API is not responding"
    fi
    
    # Check Frontend
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        frontend_healthy=true
        log_success "✅ Frontend is healthy"
    else
        log_error "❌ Frontend is not responding"
    fi
    
    if $api_healthy && $frontend_healthy; then
        log_success "🎉 All services are healthy!"
        return 0
    else
        log_error "❌ Some services are not healthy"
        return 1
    fi
}

# Show usage
show_usage() {
    echo "🪨 AI-based Rockfall Prediction System Deployment Script"
    echo "======================================================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup          Complete setup (dependencies, data, model training)"
    echo "  docker         Deploy using Docker Compose"
    echo "  native         Deploy natively (requires manual MongoDB setup)"
    echo "  stop           Stop all running services"
    echo "  health         Check service health"
    echo "  clean          Clean generated files and stop services"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup      # First-time setup"
    echo "  $0 docker     # Deploy with Docker"
    echo "  $0 native     # Deploy natively"
    echo "  $0 health     # Check if services are running"
    echo "  $0 stop       # Stop all services"
    echo ""
}

# Clean up
cleanup() {
    log_info "Cleaning up..."
    
    # Stop services
    stop_services
    
    # Clean Python cache
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    
    # Clean logs
    rm -rf logs/*.log
    
    log_success "Cleanup completed."
}

# Main deployment function
main() {
    local command=${1:-help}
    
    case $command in
        setup)
            log_info "🚀 Starting complete setup..."
            check_dependencies
            create_project_structure
            setup_python_env
            setup_environment
            generate_sample_data
            train_model
            log_success "🎉 Setup completed! Run '$0 docker' or '$0 native' to deploy."
            ;;
        docker)
            log_info "🐳 Starting Docker deployment..."
            check_dependencies
            setup_environment
            docker_deploy
            ;;
        native)
            log_info "🖥️ Starting native deployment..."
            check_dependencies
            setup_environment
            native_deploy
            ;;
        stop)
            stop_services
            ;;
        health)
            health_check
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'log_warning "Deployment interrupted. Run: $0 stop"; exit 1' INT TERM

# Run main function
main "$@"