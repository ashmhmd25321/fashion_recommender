# 🚀 Deployment Guide - Fashion Recommender

This guide will help you deploy your Fashion Recommendation System to your VPS hosting with domain `dreamware.lk`.

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ (or similar Linux distribution)
- Domain `dreamware.lk` configured to point to your VPS
- SSH access to your VPS
- GitHub account

## 🌐 Domain Configuration

Your application will be accessible at:
- **Main Application**: `http://fashion.dreamware.lk`
- **Recommendation Interface**: `http://fashion.dreamware.lk/recommendations/`

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your VPS

1. **Connect to your VPS**
   ```bash
   ssh your-username@your-vps-ip
   ```

2. **Update system packages**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install required packages**
   ```bash
   sudo apt install -y git curl wget nginx
   ```

### Step 2: Set Up GitHub Repository

1. **Create a new repository on GitHub**
   - Go to GitHub and create a new repository
   - Name it `fashion-recommender` (or any name you prefer)
   - Make it public or private as needed

2. **Push your code to GitHub**
   ```bash
   # In your local project directory
   git init
   git add .
   git commit -m "Initial commit: Fashion Recommender System"
   git branch -M main
   git remote add origin https://github.com/yourusername/fashion-recommender.git
   git push -u origin main
   ```

### Step 3: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add the following secrets:**
   - `VPS_HOST`: Your VPS IP address
   - `VPS_USERNAME`: Your VPS username
   - `VPS_PORT`: SSH port (usually 22)
   - `VPS_SSH_KEY`: Your private SSH key content

### Step 4: Deploy to VPS

1. **Clone repository on VPS**
   ```bash
   cd /opt
   sudo git clone https://github.com/yourusername/fashion-recommender.git
   sudo chown -R $USER:$USER fashion-recommender
   cd fashion-recommender
   ```

2. **Run deployment script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Update the `.env` file with your configuration:
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key-change-this
   DATABASE_URL=sqlite:///fashion.db
   ```

### Step 5: Configure DNS

1. **Add DNS records to your domain**
   - Go to your domain registrar (where you bought dreamware.lk)
   - Add an A record: `fashion.dreamware.lk` → `YOUR_VPS_IP`
   - Add a CNAME record: `www.fashion.dreamware.lk` → `fashion.dreamware.lk`

2. **Wait for DNS propagation** (usually 5-30 minutes)

### Step 6: Start the Application

1. **Start the services**
   ```bash
   sudo systemctl start fashion-recommender
   sudo systemctl status fashion-recommender
   ```

2. **Check if everything is running**
   ```bash
   docker-compose ps
   curl http://localhost:5001/health
   ```

### Step 7: Configure SSL (Optional but Recommended)

1. **Install Certbot**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   ```

2. **Get SSL certificate**
   ```bash
   sudo certbot --nginx -d fashion.dreamware.lk
   ```

3. **Test automatic renewal**
   ```bash
   sudo certbot renew --dry-run
   ```

## 🔧 Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

2. **Configure Nginx manually**
   ```bash
   sudo nano /etc/nginx/sites-available/fashion-recommender
   # Copy the nginx.conf content
   sudo ln -s /etc/nginx/sites-available/fashion-recommender /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow will automatically:
- Run tests on every push
- Deploy to VPS when pushing to main branch
- Build and restart Docker containers
- Verify deployment health

## 📊 Monitoring

### Check Application Status
```bash
# Check Docker containers
docker-compose ps

# Check application logs
docker-compose logs -f

# Check Nginx status
sudo systemctl status nginx

# Check application health
curl http://fashion.dreamware.lk/health
```

### View Logs
```bash
# Application logs
docker-compose logs fashion-recommender

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 Security Considerations

1. **Change default admin password**
   - Login with admin/admin123
   - Change password immediately

2. **Update secret key**
   - Generate a strong secret key
   - Update in .env file

3. **Configure firewall**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

4. **Regular updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker-compose pull
   docker-compose up -d
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Application not starting**
   ```bash
   docker-compose logs
   docker-compose down
   docker-compose up -d --build
   ```

2. **Nginx not working**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Domain not resolving**
   - Check DNS settings
   - Wait for propagation
   - Test with `nslookup fashion.dreamware.lk`

4. **Port conflicts**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :5001
   ```

### Reset Everything
```bash
# Stop all services
docker-compose down
sudo systemctl stop fashion-recommender

# Remove containers and images
docker-compose down --rmi all --volumes --remove-orphans

# Restart from scratch
docker-compose up -d --build
```

## 📈 Performance Optimization

1. **Enable Nginx caching**
2. **Use CDN for static assets**
3. **Implement database indexing**
4. **Monitor resource usage**

## 🎉 Success!

Once deployed, your Fashion Recommender will be available at:
- **Main App**: http://fashion.dreamware.lk
- **Recommendations**: http://fashion.dreamware.lk/recommendations/

## 📞 Support

If you encounter any issues:
1. Check the logs
2. Verify DNS settings
3. Ensure all services are running
4. Check firewall settings

---

**Happy Deploying! 🚀**
