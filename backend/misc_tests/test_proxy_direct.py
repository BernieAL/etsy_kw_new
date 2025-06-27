#!/usr/bin/env python3
"""
Direct proxy test using IP detection services.
This script will test the proxy by visiting IP detection websites.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def test_proxy_direct():
    """Test proxy by visiting IP detection websites"""
    print("=== Direct Proxy IP Test ===")
    
    # Get proxy configuration
    proxy_host = os.getenv("IPROYAL_PROXY_HOST")
    proxy_port = os.getenv("IPROYAL_PROXY_PORT")
    proxy_user = os.getenv("IPROYAL_PROXY_USER")
    proxy_pass = os.getenv("IPROYAL_PROXY_PASS")
    
    print(f"Proxy Host: {proxy_host}")
    print(f"Proxy Port: {proxy_port}")
    print(f"Proxy User: {proxy_user}")
    print(f"Proxy Pass: {'*' * len(proxy_pass) if proxy_pass else 'None'}")
    print()
    
    if not proxy_host or not proxy_port:
        print("❌ ERROR: Proxy host and port are required!")
        return
    
    print("✅ Proxy configuration found")
    print("Testing proxy with IP detection services...")
    print()
    
    async with async_playwright() as p:
        # Configure browser
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors'
        ]
        
        browser = await p.chromium.launch(
            headless=True,
            args=browser_args
        )
        
        # Create browser context with proxy
        context_options = {}
        if proxy_host and proxy_port:
            proxy_config = {
                'server': f'http://{proxy_host}:{proxy_port}'
            }
            
            if proxy_user and proxy_pass:
                proxy_config['username'] = proxy_user
                proxy_config['password'] = proxy_pass
            
            context_options['proxy'] = proxy_config
            print(f"Using proxy: {proxy_host}:{proxy_port}")
        
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        await stealth_async(page)
        
        # Test multiple IP detection services
        ip_services = [
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "https://ipinfo.io/json",
            "https://ip-api.com/json"
        ]
        
        detected_ips = []
        
        for service_url in ip_services:
            try:
                print(f"Testing: {service_url}")
                await page.goto(service_url, timeout=10000)
                await page.wait_for_timeout(2000)
                
                # Get page content
                content = await page.content()
                
                # Extract IP from response
                import re
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ip_matches = re.findall(ip_pattern, content)
                
                if ip_matches:
                    detected_ip = ip_matches[0]
                    detected_ips.append(detected_ip)
                    print(f"  → Detected IP: {detected_ip}")
                else:
                    print(f"  → No IP found in response")
                    
            except Exception as e:
                print(f"  → Error: {e}")
        
        await context.close()
        await browser.close()
        
        print()
        print("=== Results ===")
        
        if detected_ips:
            # Get unique IPs
            unique_ips = list(set(detected_ips))
            print(f"Detected IPs: {unique_ips}")
            
            real_ip = "74.102.159.251"
            
            if len(unique_ips) == 1:
                detected_ip = unique_ips[0]
                if detected_ip == real_ip:
                    print("❌ SAME IP DETECTED - Proxy NOT working!")
                    print(f"   Real IP: {real_ip}")
                    print(f"   Detected IP: {detected_ip}")
                else:
                    print("✅ DIFFERENT IP DETECTED - Proxy working!")
                    print(f"   Real IP: {real_ip}")
                    print(f"   Proxy IP: {detected_ip}")
            else:
                print("⚠️  Multiple IPs detected - Proxy may be rotating")
                print(f"   Real IP: {real_ip}")
                print(f"   Detected IPs: {unique_ips}")
        else:
            print("❌ No IPs detected - Test failed")

if __name__ == "__main__":
    asyncio.run(test_proxy_direct()) 