#!/bin/bash

# Cleanup script for old Fashion Recommendation System deployment
# This script safely removes the previous deployment without affecting other projects

echo "🧹 Starting cleanup of old Fashion Recommendation System deployment..."

# Check what's currently running
echo "📊 Checking current status..."

# Check if our services are running
echo "Checking systemd services..."
systemctl status fashion-flask.service --no-pager 2>/dev/null || echo "Flask service not found"
systemctl status fashion-streamlit.service --no-pager 2>/dev/null || echo "Streamlit service not found"

# Check if our processes are running
echo "Checking running processes..."
ps aux | grep -E "(fashion|app_simple|main_simple)" | grep -v grep || echo "No fashion-related processes found"

# Check ports
echo "Checking port usage..."
netstat -tulpn | grep -E ":(5001|5002|8501)" || echo "No processes on our ports"

# Check if our directory exists
if [ -d "/opt/fashion-recommender" ]; then
    echo "📁 Found existing project directory: /opt/fashion-recommender"
    echo "Directory contents:"
    ls -la /opt/fashion-recommender/
else
    echo "📁 No existing project directory found"
fi

# Check Nginx configuration
echo "🌐 Checking Nginx configuration..."
if [ -f "/etc/nginx/sites-enabled/fashion.dreamware.lk" ]; then
    echo "Found Nginx site configuration for fashion.dreamware.lk"
    echo "Current configuration:"
    cat /etc/nginx/sites-enabled/fashion.dreamware.lk
else
    echo "No Nginx configuration found for fashion.dreamware.lk"
fi

echo ""
echo "⚠️  CLEANUP ACTIONS (will be performed):"
echo "1. Stop and disable our systemd services"
echo "2. Remove our systemd service files"
echo "3. Remove our Nginx site configuration"
echo "4. Remove our project directory"
echo "5. Kill any remaining processes on our ports"
echo ""

read -p "Do you want to proceed with cleanup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo "🛑 Stopping services..."

# Stop and disable our services
systemctl stop fashion-flask.service 2>/dev/null || echo "Flask service not running"
systemctl stop fashion-streamlit.service 2>/dev/null || echo "Streamlit service not running"
systemctl disable fashion-flask.service 2>/dev/null || echo "Flask service not enabled"
systemctl disable fashion-streamlit.service 2>/dev/null || echo "Streamlit service not enabled"

# Kill any remaining processes on our ports
echo "🔫 Killing processes on our ports..."
for port in 5001 5002 8501; do
    PID=$(netstat -tulpn | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
    if [ ! -z "$PID" ] && [ "$PID" != "-" ]; then
        echo "Killing process $PID on port $port"
        kill $PID 2>/dev/null || echo "Process already stopped"
    fi
done

# Wait a moment
sleep 2

# Remove systemd service files
echo "🗑️  Removing systemd service files..."
rm -f /etc/systemd/system/fashion-flask.service
rm -f /etc/systemd/system/fashion-streamlit.service
systemctl daemon-reload

# Remove Nginx configuration
echo "🌐 Removing Nginx configuration..."
rm -f /etc/nginx/sites-enabled/fashion.dreamware.lk
rm -f /etc/nginx/sites-available/fashion.dreamware.lk

# Test and reload Nginx
nginx -t && systemctl reload nginx || echo "Nginx reload failed"

# Remove project directory
echo "📁 Removing project directory..."
if [ -d "/opt/fashion-recommender" ]; then
    rm -rf /opt/fashion-recommender
    echo "Project directory removed"
else
    echo "Project directory not found"
fi

# Final status check
echo ""
echo "✅ Cleanup completed! Final status:"
echo "Services:"
systemctl status fashion-flask.service --no-pager 2>/dev/null || echo "Flask service: Not found"
systemctl status fashion-streamlit.service --no-pager 2>/dev/null || echo "Streamlit service: Not found"

echo "Ports:"
netstat -tulpn | grep -E ":(5001|5002|8501)" || echo "No processes on our ports"

echo "Directory:"
ls -la /opt/fashion-recommender 2>/dev/null || echo "Project directory: Not found"

echo "Nginx sites:"
ls -la /etc/nginx/sites-enabled/ | grep fashion || echo "No fashion Nginx sites found"

echo ""
echo "🎉 Cleanup completed successfully!"
echo "You can now deploy the new configuration safely."
