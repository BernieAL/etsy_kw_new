# 🚀 VPS Deployment Checklist

## **Pre-Deployment Checklist**

### **✅ VPS Setup**
- [ ] **VPS Provider:** DigitalOcean/Linode/Vultr ($5/month)
- [ ] **OS:** Ubuntu 20.04 or 22.04
- [ ] **Specs:** 1GB RAM, 25GB storage minimum
- [ ] **SSH Access:** Key-based authentication configured
- [ ] **IP Address:** Note down your VPS IP address

### **✅ Local Setup**
- [ ] **SSH Key:** Your SSH key is added to VPS
- [ ] **Domain:** Optional - if you have a domain name
- [ ] **Firewall:** VPS firewall allows ports 22, 80, 443

## **🚀 Deployment Steps**

### **Step 1: Update Configuration**
```bash
# Edit deploy.sh and update these values:
VPS_IP="YOUR_ACTUAL_VPS_IP"        # e.g., "192.168.1.100"
VPS_USER="ubuntu"                  # Usually "ubuntu"
DOMAIN_NAME="your-domain.com"      # Or leave as IP
```

### **Step 2: Test Local Setup**
```bash
# Prepare local deployment files
./deploy.sh local
```

### **Step 3: Deploy to VPS**
```bash
# Deploy everything to your VPS
./deploy.sh remote
```

### **Step 4: Verify Deployment**
```bash
# Check if everything is running
ssh ubuntu@YOUR_VPS_IP "sudo systemctl status etsy-monitor"
ssh ubuntu@YOUR_VPS_IP "curl http://localhost:8000/health"
```

## **🔧 Post-Deployment Verification**

### **✅ Service Status**
- [ ] **Worker Service:** `sudo systemctl status etsy-monitor`
- [ ] **API Health:** `curl http://YOUR_VPS_IP:8000/health`
- [ ] **Docker Containers:** `docker compose ps`
- [ ] **Nginx:** `sudo systemctl status nginx`

### **✅ Test Functionality**
- [ ] **Create Test Rule:** Use API or CLI
- [ ] **Run Monitoring:** Execute test monitoring cycle
- [ ] **Check Logs:** Verify no errors in logs

## **📊 Monitoring Commands**

### **Check Status**
```bash
# Worker service
ssh ubuntu@YOUR_VPS_IP "sudo systemctl status etsy-monitor"

# API health
ssh ubuntu@YOUR_VPS_IP "curl http://localhost:8000/health"

# Docker containers
ssh ubuntu@YOUR_VPS_IP "cd /opt/etsy-monitor && docker compose ps"
```

### **View Logs**
```bash
# Worker logs
ssh ubuntu@YOUR_VPS_IP "sudo journalctl -u etsy-monitor -f"

# Docker logs
ssh ubuntu@YOUR_VPS_IP "cd /opt/etsy-monitor && docker compose logs -f"

# Nginx logs
ssh ubuntu@YOUR_VPS_IP "sudo tail -f /var/log/nginx/access.log"
```

### **Restart Services**
```bash
# Restart worker
ssh ubuntu@YOUR_VPS_IP "sudo systemctl restart etsy-monitor"

# Restart Docker services
ssh ubuntu@YOUR_VPS_IP "cd /opt/etsy-monitor && docker compose restart"

# Restart nginx
ssh ubuntu@YOUR_VPS_IP "sudo systemctl restart nginx"
```

## **🔒 Security Setup (Optional)**

### **SSL Certificate (Let's Encrypt)**
```bash
# Install certbot
ssh ubuntu@YOUR_VPS_IP "sudo apt install certbot python3-certbot-nginx -y"

# Get SSL certificate (if you have a domain)
ssh ubuntu@YOUR_VPS_IP "sudo certbot --nginx -d your-domain.com"
```

### **Firewall Configuration**
```bash
# Allow only necessary ports
ssh ubuntu@YOUR_VPS_IP "sudo ufw allow 22"
ssh ubuntu@YOUR_VPS_IP "sudo ufw allow 80"
ssh ubuntu@YOUR_VPS_IP "sudo ufw allow 443"
ssh ubuntu@YOUR_VPS_IP "sudo ufw enable"
```

## **📈 Scaling Considerations**

### **Resource Monitoring**
```bash
# Check resource usage
ssh ubuntu@YOUR_VPS_IP "htop"
ssh ubuntu@YOUR_VPS_IP "df -h"
ssh ubuntu@YOUR_VPS_IP "free -h"
```

### **Database Backup**
```bash
# Backup database
ssh ubuntu@YOUR_VPS_IP "cp /opt/etsy-monitor/data/etsy_monitor.db /opt/etsy-monitor/data/backup_$(date +%Y%m%d).db"
```

## **🚨 Troubleshooting**

### **Common Issues**

1. **Worker not starting:**
   ```bash
   ssh ubuntu@YOUR_VPS_IP "sudo journalctl -u etsy-monitor -n 50"
   ```

2. **API not responding:**
   ```bash
   ssh ubuntu@YOUR_VPS_IP "cd /opt/etsy-monitor && docker compose logs api"
   ```

3. **Permission issues:**
   ```bash
   ssh ubuntu@YOUR_VPS_IP "sudo chown -R ubuntu:ubuntu /opt/etsy-monitor"
   ```

4. **Port conflicts:**
   ```bash
   ssh ubuntu@YOUR_VPS_IP "sudo netstat -tlnp | grep :8000"
   ```

## **💰 Cost Tracking**

### **Monthly Costs**
- **VPS:** $5-10/month
- **Domain:** $10/year ($0.83/month)
- **Total:** $5.83-10.83/month

### **Scaling Costs**
- **100 users:** $10-20/month
- **1000 users:** $20-50/month

## **🔄 Updates**

### **Application Updates**
```bash
# Update application
./deploy.sh update
```

### **System Updates**
```bash
# Update system packages
ssh ubuntu@YOUR_VPS_IP "sudo apt update && sudo apt upgrade -y"
```

---

**🎉 Once you've completed this checklist, your Etsy Monitoring Tool will be running in production!** 