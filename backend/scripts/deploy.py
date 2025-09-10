#!/usr/bin/env python3
"""
Production deployment script for rockfall prediction system
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Deploy rockfall prediction system')
    parser.add_argument('--environment', choices=['staging', 'production'], default='staging',
                       help='Deployment environment')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip running tests before deployment')
    parser.add_argument('--skip-build', action='store_true',
                       help='Skip building Docker images')
    
    args = parser.parse_args()
    
    print("🚀 Starting deployment process...")
    print(f"📅 Deployment started at: {datetime.now()}")
    print(f"🎯 Target environment: {args.environment}")
    print("-" * 60)
    
    # Step 1: Run tests (unless skipped)
    if not args.skip_tests:
        run_command("cd backend && python -m pytest tests/ -v", "Running backend tests")
        run_command("cd frontend && npm test -- --watchAll=false", "Running frontend tests")
    
    # Step 2: Build Docker images (unless skipped)
    if not args.skip_build:
        run_command("docker-compose build --no-cache", "Building Docker images")
    
    # Step 3: Environment-specific deployment
    if args.environment == 'staging':
        run_command("docker-compose -f docker-compose.yml up -d", "Deploying to staging")
    else:
        run_command("docker-compose -f docker-compose.prod.yml up -d", "Deploying to production")
    
    # Step 4: Health checks
    print("🔍 Running health checks...")
    run_command("sleep 30", "Waiting for services to start")
    run_command("curl -f http://localhost:8000/health || exit 1", "Checking backend health")
    run_command("curl -f http://localhost:5173 || exit 1", "Checking frontend health")
    
    # Step 5: Database migrations and model training
    run_command("cd backend && python scripts/train_model.py", "Training AI models")
    
    print("\n🎉 Deployment completed successfully!")
    print(f"🌐 Application URLs:")
    print(f"   • Frontend: http://localhost:3000")
    print(f"   • Backend API: http://localhost:8000")
    print(f"   • API Docs: http://localhost:8000/docs")
    print(f"\n✅ Deployment finished at: {datetime.now()}")

if __name__ == "__main__":
    main()