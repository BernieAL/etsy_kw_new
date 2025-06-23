# 🚀 Production Deployment Guide

## **Overview**

The Etsy Monitoring Tool is designed to run as a **cost-effective web application** with automated background processing. Here's how it's deployed and runs in production.

## **🏗️ Architecture**

### **Production Stack:**
```
┌─────────────────────────────────────────────────────────────┐
│                    $5-10/month VPS                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Nginx     │  │   FastAPI   │  │   Worker    │        │
│  │   (Proxy)   │  │   (Web)     │  │   Process   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐                        │
│  │   Frontend  │  │   SQLite    │                        │
│  │   (Static)  │  │   Database  │                        │
│  └─────────────┘  └─────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### **Components:**
1. **Nginx** - Reverse proxy and static file serving
2. **FastAPI** - REST API for web interface
3. **Worker** - Background process for monitoring execution
4. **SQLite** - Database for rules and historical data
5. **Docker** - Containerization for consistency

## **🔄 How It Runs**

### **1. Background Worker Process**
```bash
# The worker runs continuously and checks for due rules every 5 minutes
python worker.py --check-interval 300
```

**What it does:**
- Checks database for monitoring rules
- Identifies rules due for execution based on intervals
- Executes scrapers sequentially for each rule
- Generates notifications for detected changes
- Updates next run times

### **2. Web API**
```bash
# FastAPI server handles web requests
python api/monitoring_api.py
```

**What it does:**
- Provides REST API for rule management
- Handles user authentication (future)
- Serves monitoring results and notifications
- Allows manual rule execution

### **3. Scheduling System**
```python
# Intervals supported:
intervals = {
    '30min': timedelta(minutes=30),
    '5hr': timedelta(hours=5),
    '12hr': timedelta(hours=12),
    '24hr': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'biweekly': timedelta(weeks=2)
}
```

## **📋 Deployment Options**

### **Option 1: Single VPS (Recommended)**
**Cost:** $5-10/month
**Provider:** DigitalOcean, Linode, Vultr

**Steps:**
1. Create VPS with Ubuntu 20.04+
2. Install Docker and Docker Compose
3. Deploy using `deploy.sh`
4. Configure domain and SSL

### **Option 2: Serverless (Future)**
**Cost:** $5-15/month (pay-per-use)
**Provider:** Railway, Render, Heroku

### **Option 3: Shared Hosting**
**Cost:** $3-10/month
**Provider:** Traditional web hosts

## **🚀 Quick Deployment**

### **1. Prepare Deployment Files**
```bash
./deploy.sh local
```

### **2. Update Configuration**
Edit `deploy.sh` and update:
- `VPS_IP` - Your VPS IP address
- `VPS_USER` - SSH username (usually 'ubuntu')
- Domain name in nginx config

### **3. Deploy to VPS**
```bash
./deploy.sh remote
```

### **4. Verify Deployment**
```bash
# Check worker status
sudo systemctl status etsy-monitor

# Check API
curl http://your-vps-ip:8000/health

# View logs
sudo journalctl -u etsy-monitor -f
```

## **🔧 Manual Deployment Steps**

### **1. VPS Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
```

### **2. Application Deployment**
```bash
# Create app directory
sudo mkdir -p /opt/etsy-monitor
sudo chown $USER:$USER /opt/etsy-monitor

# Copy application files
scp -r backend/* user@vps-ip:/opt/etsy-monitor/
scp docker-compose.prod.yml user@vps-ip:/opt/etsy-monitor/docker-compose.yml

# Start services
cd /opt/etsy-monitor
docker compose up -d
```

### **3. Systemd Service**
```bash
# Create service file
sudo tee /etc/systemd/system/etsy-monitor.service << EOF
[Unit]
Description=Etsy Monitoring Worker
After=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/etsy-monitor
ExecStart=/usr/local/bin/docker-compose up worker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable etsy-monitor
sudo systemctl start etsy-monitor
```

## **📊 Monitoring & Maintenance**

### **Health Checks**
```bash
# Check worker status
sudo systemctl status etsy-monitor

# Check API health
curl http://localhost:8000/health

# Check Docker containers
docker compose ps

# View logs
sudo journalctl -u etsy-monitor -f
docker compose logs -f
```

### **Database Management**
```bash
# Backup database
cp /opt/etsy-monitor/data/etsy_monitor.db backup_$(date +%Y%m%d).db

# Check database size
ls -lh /opt/etsy-monitor/data/etsy_monitor.db

# Clean old data (if needed)
docker compose exec api python -c "
from monitoring_system import EtsyMonitor
monitor = EtsyMonitor()
# Add cleanup logic here
"
```

### **Scaling Considerations**
- **100 users:** Current setup should handle fine
- **1000 users:** Consider upgrading to $20 VPS
- **10,000 users:** Consider microservices architecture

## **🔒 Security Considerations**

### **Production Security**
1. **Firewall:** Only expose ports 80, 443, 22
2. **SSL:** Use Let's Encrypt for HTTPS
3. **Updates:** Regular system and Docker updates
4. **Backups:** Daily database backups
5. **Monitoring:** Set up alerts for service failures

### **Rate Limiting**
```python
# In FastAPI app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## **💰 Cost Breakdown**

### **Monthly Costs:**
- **VPS:** $5-10
- **Domain:** $10/year ($0.83/month)
- **Total:** $5.83-10.83/month

### **Scaling Costs:**
- **100 users:** $10-20/month
- **1000 users:** $20-50/month
- **10,000 users:** $100-200/month

## **🚨 Troubleshooting**

### **Common Issues:**

1. **Worker not running:**
   ```bash
   sudo systemctl restart etsy-monitor
   sudo journalctl -u etsy-monitor -f
   ```

2. **API not responding:**
   ```bash
   docker compose restart api
   docker compose logs api
   ```

3. **Database issues:**
   ```bash
   # Check permissions
   ls -la /opt/etsy-monitor/data/
   
   # Recreate database (if corrupted)
   rm /opt/etsy-monitor/data/etsy_monitor.db
   docker compose restart
   ```

4. **Memory issues:**
   ```bash
   # Check memory usage
   free -h
   
   # Restart services
   docker compose restart
   sudo systemctl restart etsy-monitor
   ```

## **📈 Performance Optimization**

### **Resource Usage:**
- **CPU:** Minimal (mostly idle)
- **RAM:** ~512MB-1GB
- **Storage:** ~100MB + database growth
- **Network:** Low bandwidth usage

### **Optimization Tips:**
1. **Database cleanup:** Remove old data periodically
2. **Log rotation:** Configure log rotation for worker logs
3. **Caching:** Add Redis for caching (future enhancement)
4. **CDN:** Use CDN for static assets (future)

## **🔄 Updates & Maintenance**

### **Application Updates:**
```bash
# Pull latest code
cd /opt/etsy-monitor
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### **System Updates:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker
sudo curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

This deployment strategy provides a **cost-effective, scalable, and maintainable** solution for running your Etsy monitoring tool in production! 