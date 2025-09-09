#!/bin/bash

# AI-Based Rockfall Prediction System Setup Script
echo "🚀 Setting up AI-Based Rockfall Prediction System..."
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p backend/data/DroneImages/FilteredData/{Images,Masks,BinaryMasks}
mkdir -p backend/models
mkdir -p backend/logs
mkdir -p frontend/public
mkdir -p docs

# Set up environment files
echo "⚙️  Setting up environment files..."

# Backend .env
if [ ! -f backend/.env ]; then
    cat > backend/.env << EOF
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=rockfall_prediction

# MapMyIndia API
MAPMYINDIA_ACCESS_TOKEN=your_access_token_here
MAPMYINDIA_API_BASE_URL=https://apis.mapmyindia.com/advancedmaps/v1

# SendGrid API
SENDGRID_API_KEY=your_sendgrid_api_key_here

# SMS77.io API
SMS77IO_RAPIDAPI_KEY=your_rapidapi_key_here
SMS77IO_HOST=sms77io.p.rapidapi.com

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
EOF
    echo "   ✅ Created backend/.env"
else
    echo "   ℹ️  backend/.env already exists"
fi

# Frontend .env
if [ ! -f frontend/.env ]; then
    cat > frontend/.env << EOF
VITE_CLERK_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
VITE_API_BASE_URL=http://localhost:8000
EOF
    echo "   ✅ Created frontend/.env"
else
    echo "   ℹ️  frontend/.env already exists"
fi

# Generate sample data
echo "🔧 Generating sample data..."
cd backend
python scripts/generate_sample_data.py
cd ..

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose build
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "   ✅ Backend API is running"
else
    echo "   ❌ Backend API is not responding"
fi

if curl -f http://localhost:3000 &> /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is not responding"
fi

# Train the AI model
echo "🧠 Training AI model..."
cd backend
python scripts/train_model.py
cd ..

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================="
echo ""
echo "🌐 Access your application:"
echo "   • Frontend Dashboard: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Next steps:"
echo "   1. Replace backend/.env with your actual API keys"
echo "   2. Add your drone images to backend/data/DroneImages/FilteredData/"
echo "   3. Replace Sub_Division_IMD.json with your actual environmental data"
echo "   4. Configure alert recipients in the dashboard"
echo ""
echo "📚 Documentation: README.md"
echo "🐛 Issues: https://github.com/your-repo/issues"