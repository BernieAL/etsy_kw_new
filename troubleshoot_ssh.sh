#!/bin/bash
# SSH Troubleshooting Script for DigitalOcean Deployment

set -e

# Load environment variables if .env file exists
if [ -f .env ]; then
    # Load environment variables, ignoring comments and empty lines
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
fi

# Configuration - can be overridden by environment variables
VPS_IP="${VPS_IP:-YOUR_VPS_IP_HERE}"  # Update this with your VPS IP
VPS_USER="${VPS_USER:-root}"

# Validate configuration
if [ "$VPS_IP" = "YOUR_VPS_IP_HERE" ]; then
    echo "❌ ERROR: Please update VPS_IP in .env file or set VPS_IP environment variable"
    echo "   Create a .env file based on env.example and set your actual VPS IP address"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🔍 SSH Troubleshooting for DigitalOcean VPS"
echo "=========================================="

# Check if SSH key exists
print_step "Checking SSH key setup..."
if [ -f ~/.ssh/id_rsa.pub ]; then
    print_status "SSH public key found: ~/.ssh/id_rsa.pub"
    echo "Public key content:"
    cat ~/.ssh/id_rsa.pub
    echo ""
else
    print_warning "No SSH public key found. Generating one..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    print_status "SSH key generated. Please copy it to your VPS:"
    cat ~/.ssh/id_rsa.pub
    echo ""
fi

# Test different users
print_step "Testing SSH connections with different users..."

for user in "root" "ubuntu" "debian" "admin"; do
    print_status "Testing user: $user"
    
    # Test with verbose output
    if ssh -o ConnectTimeout=10 -o BatchMode=yes -v $user@$VPS_IP "echo 'Connection successful'" 2>&1 | grep -q "Connection successful"; then
        print_status "✅ SUCCESS: $user@$VPS_IP"
        echo ""
        print_status "To copy your SSH key to this user, run:"
        print_status "ssh-copy-id $user@$VPS_IP"
        echo ""
        break
    else
        print_warning "❌ Failed: $user@$VPS_IP"
    fi
done

# Check if VPS is reachable
print_step "Checking if VPS is reachable..."
if ping -c 3 $VPS_IP > /dev/null 2>&1; then
    print_status "✅ VPS is reachable via ping"
else
    print_error "❌ VPS is not reachable via ping"
    print_warning "Check your VPS IP address and ensure the droplet is running"
fi

# Check port 22
print_step "Checking SSH port (22)..."
if nc -z -w5 $VPS_IP 22 2>/dev/null; then
    print_status "✅ Port 22 is open"
else
    print_error "❌ Port 22 is closed or blocked"
    print_warning "Check DigitalOcean firewall rules and droplet settings"
fi

echo ""
print_step "Manual SSH Connection Test"
echo "=============================="
print_status "Try connecting manually with:"
print_status "ssh root@$VPS_IP"
echo ""
print_status "If that fails, try:"
print_status "ssh ubuntu@$VPS_IP"
echo ""
print_warning "If you get a password prompt, you may need to:"
print_warning "1. Use the password from DigitalOcean console"
print_warning "2. Or set up SSH key authentication"
echo ""
print_status "To set up SSH key authentication:"
print_status "1. Copy your public key: cat ~/.ssh/id_rsa.pub"
print_status "2. SSH to your VPS: ssh root@$VPS_IP"
print_status "3. Add key to authorized_keys: echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys" 