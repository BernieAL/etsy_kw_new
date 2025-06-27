import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load proxy config from environment variables
proxy_host = os.getenv("IPROYAL_PROXY_HOST")
proxy_port = os.getenv("IPROYAL_PROXY_PORT")
proxy_user = os.getenv("IPROYAL_PROXY_USER")
proxy_pass = os.getenv("IPROYAL_PROXY_PASS")

print("=== PROXY CONFIGURATION ===")
print(f"Proxy Host: {proxy_host}")
print(f"Proxy Port: {proxy_port}")
print(f"Proxy User: {proxy_user}")
print(f"Proxy Pass: {'*' * len(proxy_pass) if proxy_pass else 'None'}")

proxy = None
if proxy_host and proxy_port:
    if proxy_user and proxy_pass:
        proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    else:
        proxy = f"http://{proxy_host}:{proxy_port}"
    print(f"✅ Proxy configured: {proxy_host}:{proxy_port}")
else:
    print("❌ No proxy configuration found!")

def test_proxy():
    """Test if the proxy is working"""
    if not proxy:
        print("❌ No proxy configured")
        return False
    
    try:
        print("\n=== TESTING PROXY ===")
        proxies = {
            'http': proxy,
            'https': proxy
        }
        
        print("Testing with httpbin.org...")
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        ip_info = response.json()
        print(f"✅ Proxy working - IP: {ip_info.get('origin', 'Unknown')}")
        
        print("\nTesting with ipify.org...")
        response2 = requests.get('https://api.ipify.org', proxies=proxies, timeout=10)
        ip_text = response2.text
        print(f"✅ IPify confirms - IP: {ip_text}")
        
        print("\nTesting with ipinfo.io...")
        response3 = requests.get('https://ipinfo.io/json', proxies=proxies, timeout=10)
        ip_details = response3.json()
        print(f"✅ IPInfo details - IP: {ip_details.get('ip', 'Unknown')}")
        print(f"   Location: {ip_details.get('city', 'Unknown')}, {ip_details.get('country', 'Unknown')}")
        print(f"   ISP: {ip_details.get('org', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")
        return False

def test_without_proxy():
    """Test without proxy to compare"""
    try:
        print("\n=== TESTING WITHOUT PROXY (for comparison) ===")
        response = requests.get('https://httpbin.org/ip', timeout=10)
        ip_info = response.json()
        print(f"🌐 Direct connection IP: {ip_info.get('origin', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Direct connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Test without proxy first
    test_without_proxy()
    
    # Test with proxy
    proxy_working = test_proxy()
    
    if proxy_working:
        print("\n🎉 PROXY IS WORKING! Your real IP is hidden.")
    else:
        print("\n⚠️  PROXY NOT WORKING! Check your configuration.") 