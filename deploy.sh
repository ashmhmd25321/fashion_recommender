#!/bin/bash

# Fashion Recommender Deployment Script
# This script sets up the application on your VPS

set -e

echo "🚀 Starting Fashion Recommender deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# Create project directory
PROJECT_DIR="/opt/fashion-recommender"
print_status "Creating project directory at $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_warning "Please log out and log back in for Docker group changes to take effect"
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Install Nginx if not installed
if ! command -v nginx &> /dev/null; then
    print_status "Installing Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Create Nginx configuration
print_status "Setting up Nginx configuration..."
sudo tee /etc/nginx/sites-available/fashion-recommender > /dev/null <<EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    upstream flask_app {
        server 127.0.0.1:5001;
    }
    
    upstream streamlit_app {
        server 127.0.0.1:8501;
    }
    
    server {
        listen 80;
        server_name fashion.dreamware.lk;
        
        client_max_body_size 20M;
        
        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        location /recommendations/ {
            proxy_pass http://streamlit_app/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        location /static/ {
            proxy_pass http://flask_app;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/fashion-recommender /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
print_status "Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Create systemd service for the application
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/fashion-recommender.service > /dev/null <<EOF
[Unit]
Description=Fashion Recommender Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable fashion-recommender

print_status "Deployment setup completed!"
print_warning "Next steps:"
echo "1. Clone your repository to $PROJECT_DIR"
echo "2. Copy your .env file with proper configuration"
echo "3. Run: sudo systemctl start fashion-recommender"
echo "4. Configure your domain DNS to point to this server"
echo "5. Your application will be available at: http://fashion.dreamware.lk"
echo "6. Streamlit interface will be at: http://fashion.dreamware.lk/recommendations/"

print_status "Setup complete! 🎉"
