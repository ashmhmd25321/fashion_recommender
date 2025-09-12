#!/bin/bash

# Fashion Recommender Local Setup Script
echo "🚀 Setting up Fashion Recommender locally..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p static/uploads static/images instance

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_warning "Please update .env file with your configuration"
fi

print_status "Setup completed! 🎉"
print_warning "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run Flask app: python app_simple.py"
echo "3. Run Streamlit app: streamlit run main_simple.py"
echo "4. Access at http://localhost:5001 and http://localhost:8501"
