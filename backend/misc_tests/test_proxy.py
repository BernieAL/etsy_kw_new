#!/usr/bin/env python3
"""
Test script to verify proxy configuration is working correctly.
This script will test the proxy test scraper and show the results.
"""

import asyncio
import os
from scrapers.proxy_test_scraper import ProxyTestScraper

async def test_proxy():
    """Test the proxy configuration"""
    print("=== Comprehensive Proxy Configuration Test ===")
    
    # Check environment variables
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
        print("Please set IPROYAL_PROXY_HOST and IPROYAL_PROXY_PORT in your .env file")
        return
    
    print("✅ Proxy configuration found")
    print("Starting comprehensive proxy test...")
    print()
    
    # Create scraper and test
    scraper = ProxyTestScraper()
    
    try:
        # Call pre-scrape hook
        scraper.pre_scrape_hook({})
        
        # Run the scrape
        result = await scraper.scrape({})
        
        # Call post-scrape hook
        scraper.post_scrape_hook(result)
        
        print()
        print("=== Test Results ===")
        print(f"Success: {result.get('success', False)}")
        print(f"Proxy Used: {result.get('proxy_used', False)}")
        print(f"Proxy Host: {result.get('proxy_host', 'None')}")
        print(f"Proxy Port: {result.get('proxy_port', 'None')}")
        
        if result.get('success'):
            print("✅ Proxy test completed successfully!")
            
            if result.get('proxy_used'):
                print("✅ Proxy is being used")
            else:
                print("❌ Proxy is NOT being used")
            
            # Display results for each test site
            test_results = result.get('test_results', {})
            print(f"\n📊 Results by Site:")
            
            for site_url, site_result in test_results.items():
                site_name = site_url.split('/')[2]  # Extract domain name
                print(f"\n🌐 {site_name}:")
                
                if site_result.get('success'):
                    print(f"  ✅ Success")
                    print(f"  📍 IP Detection: {site_result.get('ip_detected', 'Unknown')}")
                    print(f"  🔍 Detected IP: {site_result.get('detected_ip', 'Unknown')}")
                    print(f"  📄 Page Title: {site_result.get('page_title', 'Unknown')}")
                    print(f"  📏 Content Length: {site_result.get('content_length', 0)} chars")
                    
                    # Show site-specific results
                    site_results = site_result.get('site_results', {})
                    if site_results:
                        print(f"  📋 Site Results:")
                        for key, value in site_results.items():
                            print(f"    • {key}: {value}")
                else:
                    print(f"  ❌ Failed: {site_result.get('error', 'Unknown error')}")
            
            # Summary
            successful_tests = sum(1 for site_result in test_results.values() if site_result.get('success', False))
            total_tests = len(test_results)
            
            print(f"\n📈 Summary:")
            print(f"  • {successful_tests}/{total_tests} sites successful")
            
            if successful_tests == total_tests:
                print("  🎉 All tests passed!")
            elif successful_tests > 0:
                print("  ⚠️  Some tests passed, some failed")
            else:
                print("  ❌ All tests failed")
                
        else:
            print("❌ Proxy test failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_proxy()) 