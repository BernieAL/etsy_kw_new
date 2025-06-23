# Quick Deployment Guide

## Environment Variables Setup

### 🚀 **Recommended: Create .env on Server**

1. **SSH to your VPS:**
   ```bash
   ssh root@YOUR_VPS_IP
   cd /opt/etsy-monitor
   ```

2. **Create .env file:**
   ```bash
   nano .env
   ```

3. **Add your configuration:**
   ```bash
   VPS_IP=YOUR_ACTUAL_VPS_IP
   VPS_USER=root
   DATABASE_PATH=/app/data/etsy_monitor.db
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. **Save (Ctrl+X, Y, Enter)**

### 🔄 **Alternative: Copy from Local**

1. **Create .env locally:**
   ```bash
   cp env.example .env
   nano .env  # Edit with your values
   ```

2. **Deploy with script:**
   ```bash
   ./deploy.sh remote
   ```
   *(The script will automatically copy .env to server)*

## Deployment Commands

```bash
# First time deployment
./deploy.sh remote

# Update existing deployment
./deploy.sh update

# Check status
ssh root@YOUR_VPS_IP 'sudo systemctl status etsy-monitor'
```

## Verification

```bash
# Test API
curl http://YOUR_VPS_IP/health

# Check logs
ssh root@YOUR_VPS_IP 'sudo journalctl -u etsy-monitor -f'
```

## Troubleshooting

- **No .env file:** Create one on server or locally
- **Permission denied:** `chmod 600 /opt/etsy-monitor/.env`
- **API not responding:** Check Docker containers and logs 