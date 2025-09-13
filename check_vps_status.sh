#!/bin/bash

# Quick VPS status check for Fashion Recommendation System
# Run this to see what's currently deployed

echo "🔍 Checking VPS status for Fashion Recommendation System..."
echo "=================================================="

# Check systemd services
echo "📋 Systemd Services:"
echo "-------------------"
systemctl status fashion-flask.service --no-pager 2>/dev/null || echo "❌ Flask service: Not found"
echo ""
systemctl status fashion-streamlit.service --no-pager 2>/dev/null || echo "❌ Streamlit service: Not found"
echo ""

# Check running processes
echo "🔄 Running Processes:"
echo "--------------------"
ps aux | grep -E "(fashion|app_simple|main_simple)" | grep -v grep || echo "❌ No fashion-related processes found"
echo ""

# Check port usage
echo "🌐 Port Usage:"
echo "-------------"
netstat -tulpn | grep -E ":(5001|5002|8501)" || echo "❌ No processes on our ports"
echo ""

# Check project directory
echo "📁 Project Directory:"
echo "--------------------"
if [ -d "/opt/fashion-recommender" ]; then
    echo "✅ Found: /opt/fashion-recommender"
    echo "Contents:"
    ls -la /opt/fashion-recommender/ | head -10
    echo "..."
else
    echo "❌ Not found: /opt/fashion-recommender"
fi
echo ""

# Check Nginx configuration
echo "🌐 Nginx Configuration:"
echo "----------------------"
if [ -f "/etc/nginx/sites-enabled/fashion.dreamware.lk" ]; then
    echo "✅ Found: fashion.dreamware.lk site"
    echo "Configuration preview:"
    head -20 /etc/nginx/sites-enabled/fashion.dreamware.lk
    echo "..."
else
    echo "❌ Not found: fashion.dreamware.lk site"
fi
echo ""

# Check all Nginx sites
echo "🌐 All Nginx Sites:"
echo "------------------"
ls -la /etc/nginx/sites-enabled/ | grep -v default || echo "No custom sites found"
echo ""

# Check firewall status
echo "🔥 Firewall Status:"
echo "------------------"
ufw status || echo "UFW not configured"
echo ""

# Check disk usage
echo "💾 Disk Usage:"
echo "-------------"
df -h /opt/ 2>/dev/null || echo "Cannot check /opt disk usage"
echo ""

echo "=================================================="
echo "✅ Status check completed!"
