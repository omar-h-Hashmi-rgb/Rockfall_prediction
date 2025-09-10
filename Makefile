# Makefile for AI-based Rockfall Prediction System

.PHONY: help install setup train start-api start-frontend start docker-build docker-up docker-down k8s-deploy test clean

# Default target
help:
	@echo "🪨 AI-based Rockfall Prediction System"
	@echo "======================================="
	@echo ""
	@echo "Available commands:"
	@echo "  help           - Show this help message"
	@echo "  install        - Install Python dependencies"
	@echo "  setup          - Complete setup (install + data + train)"
	@echo "  generate-data  - Generate synthetic sensor data"
	@echo "  train          - Train the ML model"
	@echo "  start-api      - Start the FastAPI backend"
	@echo "  start-frontend - Start the Streamlit frontend"
	@echo "  start          - Start both API and frontend"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start with Docker Compose"
	@echo "  docker-down    - Stop Docker Compose"
	@echo "  k8s-deploy     - Deploy to Kubernetes"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean generated files"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Generate sample data
generate-data:
	@echo "🎲 Generating synthetic sensor data..."
	python scripts/seed_sensors.py --duration 168 --frequency 60
	@echo "✅ Sample data generated!"

# Train the model
train:
	@echo "🧠 Training the ML model..."
	cd ml && python train.py
	@echo "✅ Model training completed!"

# Complete setup
setup: install generate-data train
	@echo "🎉 Setup completed successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Configure your .env file"
	@echo "  2. Start MongoDB: docker run -d -p 27017:27017 mongo:5.0"
	@echo "  3. Run: make start"

# Start API server
start-api:
	@echo "🚀 Starting FastAPI backend..."
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend
start-frontend:
	@echo "🎨 Starting Streamlit frontend..."
	streamlit run streamlit_app/app.py --server.address 0.0.0.0 --server.port 8501

# Start both services (requires tmux)
start:
	@echo "🚀 Starting both API and frontend..."
	@if command -v tmux > /dev/null; then \
		tmux new-session -d -s rockfall-api 'make start-api'; \
		tmux new-session -d -s rockfall-frontend 'make start-frontend'; \
		echo "✅ Services started in tmux sessions:"; \
		echo "  - API: tmux attach -t rockfall-api"; \
		echo "  - Frontend: tmux attach -t rockfall-frontend"; \
		echo "  - Stop: tmux kill-session -t rockfall-api && tmux kill-session -t rockfall-frontend"; \
	else \
		echo "❌ tmux not found. Please install tmux or start services manually:"; \
		echo "  Terminal 1: make start-api"; \
		echo "  Terminal 2: make start-frontend"; \
	fi

# Docker commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker build -t rockfall-prediction .
	@echo "✅ Docker image built!"

docker-up:
	@echo "🐳 Starting services with Docker Compose..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "  - Frontend: http://localhost:8501"
	@echo "  - API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"

docker-down:
	@echo "🐳 Stopping Docker Compose services..."
	docker-compose down
	@echo "✅ Services stopped!"

docker-logs:
	@echo "📋 Showing Docker Compose logs..."
	docker-compose logs -f

# Kubernetes deployment
k8s-deploy:
	@echo "☸️ Deploying to Kubernetes..."
	kubectl apply -f kubernetes/namespace.yaml
	kubectl apply -f kubernetes/secrets.yaml
	kubectl apply -f kubernetes/configmap.yaml
	kubectl apply -f kubernetes/mongodb-deployment.yaml
	kubectl apply -f kubernetes/api-deployment.yaml
	kubectl apply -f kubernetes/frontend-deployment.yaml
	kubectl apply -f kubernetes/ingress.yaml
	@echo "✅ Deployed to Kubernetes!"
	@echo "Check status: kubectl get pods -n rockfall-system"

k8s-status:
	@echo "☸️ Kubernetes deployment status..."
	kubectl get all -n rockfall-system

k8s-logs:
	@echo "📋 Showing Kubernetes logs..."
	kubectl logs -f deployment/rockfall-api -n rockfall-system

k8s-clean:
	@echo "🧹 Cleaning Kubernetes deployment..."
	kubectl delete namespace rockfall-system
	@echo "✅ Kubernetes deployment cleaned!"

# Testing
test:
	@echo "🧪 Running tests..."
	@if [ -d "tests" ]; then \
		python -m pytest tests/ -v; \
	else \
		echo "⚠️ No tests directory found. Creating basic API test..."; \
		python -c "import requests; r = requests.get('http://localhost:8000/api/health'); print('✅ API Health:', r.status_code == 200)"; \
	fi

# Development utilities
dev-setup:
	@echo "🛠️ Setting up development environment..."
	pip install black flake8 pytest
	@echo "✅ Development tools installed!"

format:
	@echo "✨ Formatting code with black..."
	black .
	@echo "✅ Code formatted!"

lint:
	@echo "🔍 Linting code with flake8..."
	flake8 . --max-line-length=100 --ignore=E203,W503
	@echo "✅ Linting completed!"

# Monitoring and logs
logs:
	@echo "📋 Showing application logs..."
	@if [ -d "logs" ]; then \
		tail -f logs/*.log; \
	else \
		echo "⚠️ No logs directory found"; \
	fi

monitor:
	@echo "📊 Monitoring system resources..."
	@if command -v htop > /dev/null; then \
		htop; \
	else \
		top; \
	fi

# Database operations
db-backup:
	@echo "💾 Backing up MongoDB..."
	@if command -v mongodump > /dev/null; then \
		mongodump --uri="mongodb://localhost:27017/rockfall_db" --out=backup/; \
		echo "✅ Database backup completed!"; \
	else \
		echo "❌ mongodump not found. Install MongoDB tools."; \
	fi

db-restore:
	@echo "📥 Restoring MongoDB..."
	@if command -v mongorestore > /dev/null; then \
		mongorestore --uri="mongodb://localhost:27017/rockfall_db" backup/rockfall_db/; \
		echo "✅ Database restore completed!"; \
	else \
		echo "❌ mongorestore not found. Install MongoDB tools."; \
	fi

# Cleanup
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	@echo "✅ Cleanup completed!"

clean-data:
	@echo "🗑️ Cleaning generated data..."
	rm -f data/sensors/*.csv
	rm -f data/Sub_Division_IMD.json
	@echo "✅ Data cleanup completed!"

clean-models:
	@echo "🗑️ Cleaning ML artifacts..."
	rm -rf ml/artifacts/*.pkl
	rm -rf ml/artifacts/*.json
	rm -rf ml/artifacts/*.csv
	@echo "✅ Model cleanup completed!"

# Environment checks
check-env:
	@echo "🔍 Checking environment..."
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Node available: $(shell command -v node > /dev/null && echo 'Yes' || echo 'No')"
	@echo "Docker available: $(shell command -v docker > /dev/null && echo 'Yes' || echo 'No')"
	@echo "Kubectl available: $(shell command -v kubectl > /dev/null && echo 'Yes' || echo 'No')"
	@echo "MongoDB tools: $(shell command -v mongodump > /dev/null && echo 'Yes' || echo 'No')"

# Production deployment
prod-deploy:
	@echo "🚀 Production deployment..."
	@echo "⚠️ This should be customized for your production environment"
	@echo "Recommended steps:"
	@echo "  1. Set production environment variables"
	@echo "  2. Use proper SSL certificates"
	@echo "  3. Configure monitoring and logging"
	@echo "  4. Set up backup strategies"
	@echo "  5. Configure CI/CD pipelines"

# Show system information
info:
	@echo "🪨 AI-based Rockfall Prediction System Information"
	@echo "=================================================="
	@echo "Version: 1.0.0"
	@echo "Author: Omar H. Hashmi"
	@echo "License: MIT"
	@echo ""
	@echo "Components:"
	@echo "  - FastAPI Backend (Python)"
	@echo "  - Streamlit Frontend (Python)"
	@echo "  - MongoDB Database"
	@echo "  - Machine Learning (scikit-learn)"
	@echo "  - Docker & Kubernetes Support"
	@echo ""
	@echo "External Services:"
	@echo "  - MapMyIndia (Mapping)"
	@echo "  - SendGrid (Email Alerts)"
	@echo "  - SMS77 (SMS Alerts)"
	@echo ""
	@echo "For help: make help"