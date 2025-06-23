#!/bin/bash
# Production Deployment Script for Etsy Monitoring Tool

set -e  # Exit on any error

echo "🚀 Deploying Etsy Monitoring Tool to Production"

# Load environment variables if .env file exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Configuration - can be overridden by environment variables
VPS_IP="${VPS_IP:-YOUR_VPS_IP_HERE}"              # e.g., "192.168.1.100" or "your-domain.com"
VPS_USER="${VPS_USER:-root}"                     # Usually "root" for DigitalOcean, "ubuntu" for some distros

# Application settings
SERVICE_NAME="etsy-monitor"
APP_DIR="/opt/etsy-monitor"
DOMAIN_NAME="${DOMAIN_NAME:-$VPS_IP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# =============================================================================
# SSH CONNECTION TESTING
# =============================================================================

test_ssh_connection() {
    print_step "Testing SSH connection to $VPS_USER@$VPS_IP..."
    
    # Test basic SSH connection
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_IP "echo 'SSH connection successful'" 2>/dev/null; then
        print_error "SSH connection failed to $VPS_USER@$VPS_IP"
        echo ""
        print_warning "Troubleshooting steps:"
        print_warning "1. Verify your VPS IP address is correct"
        print_warning "2. Check if SSH key is properly set up:"
        print_warning "   - Run: ssh-copy-id $VPS_USER@$VPS_IP"
        print_warning "   - Or manually copy your public key to ~/.ssh/authorized_keys"
        print_warning "3. Try different users:"
        print_warning "   - DigitalOcean Ubuntu: usually 'root' or 'ubuntu'"
        print_warning "   - DigitalOcean CentOS: usually 'root'"
        print_warning "4. Check DigitalOcean console for any firewall rules"
        print_warning "5. Verify the droplet is running in DigitalOcean dashboard"
        echo ""
        print_warning "To test with password (if key auth fails):"
        print_warning "   ssh $VPS_USER@$VPS_IP"
        echo ""
        
        # Try alternative users
        for alt_user in "ubuntu" "debian" "admin"; do
            if [ "$alt_user" != "$VPS_USER" ]; then
                print_status "Trying alternative user: $alt_user"
                if ssh -o ConnectTimeout=5 -o BatchMode=yes $alt_user@$VPS_IP "echo 'SSH connection successful'" 2>/dev/null; then
                    print_status "✅ Found working user: $alt_user"
                    VPS_USER="$alt_user"
                    return 0
                fi
            fi
        done
        
        exit 1
    fi
    
    print_status "✅ SSH connection successful"
}

setup_digitalocean_firewall() {
    print_step "Setting up DigitalOcean firewall rules..."
    
    # Configure UFW firewall
    ssh $VPS_USER@$VPS_IP "sudo ufw --force reset"
    ssh $VPS_USER@$VPS_IP "sudo ufw default deny incoming"
    ssh $VPS_USER@$VPS_IP "sudo ufw default allow outgoing"
    ssh $VPS_USER@$VPS_IP "sudo ufw allow ssh"
    ssh $VPS_USER@$VPS_IP "sudo ufw allow 80/tcp"
    ssh $VPS_USER@$VPS_IP "sudo ufw allow 443/tcp"
    ssh $VPS_USER@$VPS_IP "sudo ufw --force enable"
    
    print_status "Firewall configured"
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

setup_vps() {
    print_step "Setting up VPS environment..."
    
    # Update system
    ssh $VPS_USER@$VPS_IP "sudo apt update && sudo apt upgrade -y"
    
    # Install Docker
    ssh $VPS_USER@$VPS_IP "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    ssh $VPS_USER@$VPS_IP "sudo usermod -aG docker $VPS_USER"
    
    # Install Docker Compose
    ssh $VPS_USER@$VPS_IP "sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    ssh $VPS_USER@$VPS_IP "sudo chmod +x /usr/local/bin/docker-compose"
    
    # Install Nginx
    ssh $VPS_USER@$VPS_IP "sudo apt install nginx curl -y"
    
    # Install Python and pip (for worker)
    ssh $VPS_USER@$VPS_IP "sudo apt install python3 python3-pip python3-venv -y"
    
    # Setup firewall
    setup_digitalocean_firewall
    
    print_status "VPS environment setup completed"
}

deploy_application() {
    print_step "Deploying application files..."
    
    # Create remote directory structure
    ssh $VPS_USER@$VPS_IP "sudo mkdir -p $APP_DIR/{app,logs,data}"
    ssh $VPS_USER@$VPS_IP "sudo chown $VPS_USER:$VPS_USER $APP_DIR -R"
    
    # Copy application files
    print_status "Copying backend files..."
    scp -r backend/* $VPS_USER@$VPS_IP:$APP_DIR/app/
    
    print_status "Copying configuration files..."
    scp docker-compose.prod.yml $VPS_USER@$VPS_IP:$APP_DIR/docker-compose.yml
    scp run_*.sh $VPS_USER@$VPS_IP:$APP_DIR/
    
    # Make scripts executable
    ssh $VPS_USER@$VPS_IP "chmod +x $APP_DIR/run_*.sh"
    
    print_status "Application files deployed"
}

setup_services() {
    print_step "Setting up system services..."
    
    # Create systemd service file for worker
    cat > etsy-monitor.service << EOF
[Unit]
Description=Etsy Monitoring Worker
After=network.target

[Service]
Type=simple
User=$VPS_USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/app/worker.py --check-interval 300
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONPATH=$APP_DIR/app

[Install]
WantedBy=multi-user.target
EOF
    
    # Copy service file and enable it
    scp etsy-monitor.service $VPS_USER@$VPS_IP:$APP_DIR/
    ssh $VPS_USER@$VPS_IP "sudo cp $APP_DIR/etsy-monitor.service /etc/systemd/system/"
    ssh $VPS_USER@$VPS_IP "sudo systemctl daemon-reload"
    ssh $VPS_USER@$VPS_IP "sudo systemctl enable $SERVICE_NAME"
    
    # Create nginx configuration
    cat > nginx.conf << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $APP_DIR/app/static/;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF
    
    # Copy nginx config
    scp nginx.conf $VPS_USER@$VPS_IP:$APP_DIR/
    ssh $VPS_USER@$VPS_IP "sudo cp $APP_DIR/nginx.conf /etc/nginx/sites-available/$SERVICE_NAME"
    ssh $VPS_USER@$VPS_IP "sudo ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/"
    ssh $VPS_USER@$VPS_IP "sudo rm -f /etc/nginx/sites-enabled/default"
    
    print_status "System services configured"
}

start_services() {
    print_step "Starting services..."
    
    # Install Python dependencies
    ssh $VPS_USER@$VPS_IP "cd $APP_DIR/app && pip3 install -r requirements.txt"
    
    # Start Docker services
    ssh $VPS_USER@$VPS_IP "cd $APP_DIR && docker compose up -d"
    
    # Start worker service
    ssh $VPS_USER@$VPS_IP "sudo systemctl start $SERVICE_NAME"
    
    # Restart nginx
    ssh $VPS_USER@$VPS_IP "sudo systemctl restart nginx"
    
    print_status "Services started"
}

verify_deployment() {
    print_step "Verifying deployment..."
    
    # Wait a moment for services to start
    sleep 10
    
    # Check worker status
    print_status "Checking worker service..."
    ssh $VPS_USER@$VPS_IP "sudo systemctl status $SERVICE_NAME --no-pager -l"
    
    # Check API health
    print_status "Checking API health..."
    ssh $VPS_USER@$VPS_IP "curl -f http://localhost:8000/health || echo 'API not responding'"
    
    # Check Docker containers
    print_status "Checking Docker containers..."
    ssh $VPS_USER@$VPS_IP "cd $APP_DIR && docker compose ps"
    
    # Check nginx
    print_status "Checking nginx..."
    ssh $VPS_USER@$VPS_IP "sudo systemctl status nginx --no-pager -l"
    
    print_status "Deployment verification completed"
}

# =============================================================================
# MAIN DEPLOYMENT FLOW
# =============================================================================

if [ "$1" = "local" ]; then
    print_status "Running local deployment setup..."
    
    # Create production directory structure
    mkdir -p production/{app,logs,data}
    
    # Copy application files
    cp -r backend/* production/app/
    cp docker-compose.prod.yml production/docker-compose.yml
    cp run_*.sh production/
    
    print_status "Local deployment files prepared in ./production/"
    print_warning "Please update VPS_IP and DOMAIN_NAME in deploy.sh before running remote deployment"
    
elif [ "$1" = "remote" ]; then
    print_status "Starting deployment to VPS: $VPS_IP"
    print_status "Domain: $DOMAIN_NAME"
    print_status "User: $VPS_USER"
    
    # Test SSH connection first
    test_ssh_connection
    
    # Run deployment steps
    setup_vps
    deploy_application
    setup_services
    start_services
    verify_deployment
    
    print_status "🎉 Deployment completed successfully!"
    echo ""
    print_status "Your Etsy Monitoring Tool is now running at:"
    print_status "  API: http://$DOMAIN_NAME:8000"
    print_status "  Health: http://$DOMAIN_NAME/health"
    echo ""
    print_status "Useful commands:"
    print_status "  Check worker: ssh $VPS_USER@$VPS_IP 'sudo systemctl status $SERVICE_NAME'"
    print_status "  View logs: ssh $VPS_USER@$VPS_IP 'sudo journalctl -u $SERVICE_NAME -f'"
    print_status "  Restart: ssh $VPS_USER@$VPS_IP 'sudo systemctl restart $SERVICE_NAME'"
    print_status "  Docker logs: ssh $VPS_USER@$VPS_IP 'cd $APP_DIR && docker compose logs -f'"
    
elif [ "$1" = "update" ]; then
    print_status "Updating application on VPS: $VPS_IP"
    
    deploy_application
    ssh $VPS_USER@$VPS_IP "cd $APP_DIR && docker compose down"
    ssh $VPS_USER@$VPS_IP "cd $APP_DIR && docker compose up -d --build"
    ssh $VPS_USER@$VPS_IP "sudo systemctl restart $SERVICE_NAME"
    
    print_status "Application updated successfully!"
    
else
    print_error "Usage: $0 {local|remote|update}"
    echo ""
    print_status "Commands:"
    print_status "  local  - Prepare local deployment files"
    print_status "  remote - Deploy to VPS (update VPS_IP first)"
    print_status "  update - Update existing deployment"
    echo ""
    print_status "Before running 'remote':"
    print_status "  1. Update VPS_IP in this script with your VPS IP address"
    print_status "  2. Update DOMAIN_NAME if you have a domain"
    print_status "  3. Ensure SSH key-based authentication is set up"
    exit 1
fi 