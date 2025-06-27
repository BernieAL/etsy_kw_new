from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import os
from datetime import datetime
from typing import Dict, Any
import random

from scraper_base import BaseScraper

class ProxyTestScraper(BaseScraper):
    """Tests proxy functionality using multiple bot detection sites"""
    
    def __init__(self):
        super().__init__("proxy_test", "Proxy Test Scraper")
    
    async def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test proxy functionality using multiple bot detection sites"""
        
        # Get proxy configuration from environment variables or params
        proxy_host = params.get("proxy_host") or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get("proxy_port") or os.getenv("IPROYAL_PROXY_PORT")
        proxy_user = params.get("proxy_user") or os.getenv("IPROYAL_PROXY_USER")
        proxy_pass = params.get("proxy_pass") or os.getenv("IPROYAL_PROXY_PASS")
        
        # Bot test links to check
        bot_test_links = [
            "https://bot.sannysoft.com/",
            "https://bot.incolumitas.com/",
            "https://ipinfo.io/json",
            "https://amiunique.org/fp",
            "https://pixelscan.net/",
            "https://browserleaks.com/",
            "https://whoer.net/",
            "https://abrahamjuliot.github.io/creepjs/",
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "https://dnsleaktest.com/",
            "https://ipleak.net/",
            "https://browserleaks.com/webrtc",
            "https://detectmybrowser.com/",
            "https://webbrowsertools.com/javascript-tester/",
            "https://webbrowsertools.com/cookie-test/",
            "https://webbrowsertools.com/localstorage-test/"
        ]
        
        test_results = {}
        
        async with async_playwright() as p:
            # Configure browser launch arguments to match Selenium setup
            browser_args = [
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions-except',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            browser = await p.chromium.launch(
                headless=True,
                args=browser_args
            )
            
            # Create browser context with proxy configuration and user agent
            context_options = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'viewport': {'width': 1920, 'height': 1080},
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'extra_http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            }
            
            if proxy_host and proxy_port:
                # Always set proxy in context if host and port are provided
                proxy_config = {
                    'server': f'http://{proxy_host}:{proxy_port}'
                }
                
                # Add authentication if credentials are provided
                if proxy_user and proxy_pass:
                    proxy_config['username'] = proxy_user
                    proxy_config['password'] = proxy_pass
                
                context_options['proxy'] = proxy_config
                print(f"Using proxy: {proxy_host}:{proxy_port}")
            else:
                print("No proxy configuration found - using direct connection")
            
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            # Apply stealth measures (similar to selenium-stealth)
            await stealth_async(page)
            
            # Set additional properties to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                window.chrome = {
                    runtime: {},
                };
            """)
            
            # Block WebRTC leaks by overriding APIs and permissions
            await context.grant_permissions([], origin="https://browserleaks.com")
            await page.add_init_script('''
                // Block WebRTC leaks
                Object.defineProperty(navigator, 'mediaDevices', { get: () => undefined });
                if (window.RTCPeerConnection) {
                    window.RTCPeerConnection = undefined;
                }
                if (window.webkitRTCPeerConnection) {
                    window.webkitRTCPeerConnection = undefined;
                }
                // Block WebRTC in iframe
                if (window.top !== window.self) {
                    if (window.RTCPeerConnection) {
                        window.RTCPeerConnection = undefined;
                    }
                    if (window.webkitRTCPeerConnection) {
                        window.webkitRTCPeerConnection = undefined;
                    }
                }
            ''')
            
            # Test each bot detection site
            for i, test_url in enumerate(bot_test_links):
                print(f"\n--- Testing {test_url} ---")
                try:
                    # Go to bot detection test page
                    await page.goto(test_url, wait_until='networkidle')
                    
                    # Wait for page to load and JavaScript to execute
                    await page.wait_for_timeout(8000)
                    
                    # Take a screenshot for debugging
                    try:
                        screenshot_path = f"/app/proxy_test_screenshot_{i}.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"Screenshot saved to {screenshot_path}")
                    except Exception as e:
                        print(f"Could not take screenshot: {e}")

                    # Get page title and URL
                    try:
                        page_title = await page.title()
                        current_url = page.url
                        print(f"Page title: {page_title}")
                        print(f"Current URL: {current_url}")
                    except Exception as e:
                        print(f"Could not get page info: {e}")

                    # Extract test results based on the site
                    site_results = {}
                    
                    if "bot.sannysoft.com" in test_url:
                        # Extract bot detection results from sannysoft
                        try:
                            await page.wait_for_selector("table", timeout=10000)
                            rows = await page.query_selector_all("table tr")
                            
                            for row in rows:
                                try:
                                    cells = await row.query_selector_all("td")
                                    if len(cells) >= 2:
                                        test_name = await cells[0].inner_text()
                                        test_result = await cells[1].inner_text()
                                        site_results[test_name.strip()] = test_result.strip()
                                except Exception as e:
                                    continue
                        except Exception as e:
                            print(f"Could not extract sannysoft test results: {e}")
                    
                    elif "bot.incolumitas.com" in test_url:
                        # Extract bot detection results from incolumitas
                        try:
                            # Look for bot detection indicators
                            page_content = await page.content()
                            if "bot detected" in page_content.lower():
                                site_results["bot_detected"] = "Yes"
                            else:
                                site_results["bot_detected"] = "No"
                            
                            # Extract any visible test results
                            test_elements = await page.query_selector_all("[class*='test'], [class*='result']")
                            for elem in test_elements:
                                try:
                                    text = await elem.inner_text()
                                    if text.strip():
                                        site_results[f"test_{len(site_results)}"] = text.strip()
                                except:
                                    continue
                        except Exception as e:
                            print(f"Could not extract incolumitas test results: {e}")
                    
                    elif "ipinfo.io" in test_url:
                        # Extract IP information from ipinfo
                        try:
                            page_content = await page.content()
                            import re
                            import json
                            
                            # Try to parse JSON response
                            try:
                                json_data = json.loads(page_content)
                                site_results["ip"] = json_data.get("ip", "Unknown")
                                site_results["city"] = json_data.get("city", "Unknown")
                                site_results["region"] = json_data.get("region", "Unknown")
                                site_results["country"] = json_data.get("country", "Unknown")
                                site_results["org"] = json_data.get("org", "Unknown")
                            except:
                                # Fallback to regex extraction
                                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                                ip_matches = re.findall(ip_pattern, page_content)
                                if ip_matches:
                                    site_results["ip"] = ip_matches[0]
                                else:
                                    site_results["ip"] = "Unknown"
                        except Exception as e:
                            print(f"Could not extract ipinfo results: {e}")
                    
                    elif "amiunique.org" in test_url:
                        # Try to extract fingerprint hash
                        try:
                            await page.wait_for_selector("#fingerprint-hash", timeout=10000)
                            fp_hash = await page.locator("#fingerprint-hash").inner_text()
                            site_results["fingerprint_hash"] = fp_hash
                        except Exception as e:
                            print(f"Could not extract amiunique fingerprint: {e}")
                    elif "pixelscan.net" in test_url:
                        # Try to extract bot score or summary
                        try:
                            await page.wait_for_selector(".result", timeout=10000)
                            summary = await page.locator(".result").inner_text()
                            site_results["pixelscan_result"] = summary
                        except Exception as e:
                            print(f"Could not extract pixelscan result: {e}")
                    elif "browserleaks.com" in test_url:
                        # Just note that the page loaded
                        site_results["note"] = "Loaded browserleaks.com page"
                    elif "whoer.net" in test_url:
                        # Try to extract anonymity score
                        try:
                            await page.wait_for_selector(".anonymity-status__text", timeout=10000)
                            anon_score = await page.locator(".anonymity-status__text").inner_text()
                            site_results["anonymity_status"] = anon_score
                        except Exception as e:
                            print(f"Could not extract whoer anonymity: {e}")
                    elif "creepjs" in test_url:
                        # Try to extract bot score or summary
                        try:
                            await page.wait_for_selector("#fingerprint", timeout=10000)
                            creep_fp = await page.locator("#fingerprint").inner_text()
                            site_results["creepjs_fingerprint"] = creep_fp
                        except Exception as e:
                            print(f"Could not extract creepjs fingerprint: {e}")
                    elif "intoli.com" in test_url:
                        # Try to extract headless detection result
                        try:
                            await page.wait_for_selector("#not-headless", timeout=10000)
                            not_headless = await page.locator("#not-headless").inner_text()
                            site_results["headless_detection"] = not_headless
                        except Exception as e:
                            print(f"Could not extract intoli headless detection: {e}")
                    elif "dnsleaktest.com" in test_url or "ipleak.net" in test_url:
                        # Just note that the page loaded
                        site_results["note"] = "Loaded DNS/IP leak test page"
                    elif "webrtc" in test_url:
                        # Try to extract WebRTC IPs
                        try:
                            page_content = await page.content()
                            import re
                            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                            ip_matches = re.findall(ip_pattern, page_content)
                            site_results["webrtc_ips"] = ip_matches
                        except Exception as e:
                            print(f"Could not extract webrtc IPs: {e}")
                    elif "detectmybrowser.com" in test_url:
                        site_results["note"] = "Loaded detectmybrowser.com page"
                    elif "javascript-tester" in test_url:
                        site_results["note"] = "Loaded JS tester page"
                    elif "cookie-test" in test_url:
                        site_results["note"] = "Loaded cookie test page"
                    elif "localstorage-test" in test_url:
                        site_results["note"] = "Loaded localstorage test page"
                    
                    # Get page content to check for IP information
                    try:
                        page_content = await page.content()
                        print(f"Page content length: {len(page_content)} characters")
                        
                        # Look for IP information in the page
                        import re
                        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                        ip_matches = re.findall(ip_pattern, page_content)
                        
                        detected_ip = "Unknown"
                        if ip_matches:
                            from collections import Counter
                            ip_counter = Counter(ip_matches)
                            detected_ip = ip_counter.most_common(1)[0][0]
                            print(f"Detected IP address: {detected_ip}")
                        
                        # Check for real IP
                        real_ip = "74.102.159.251"
                        if real_ip in page_content:
                            print("WARNING: Real IP detected in page content!")
                            ip_detected = f"Real IP ({real_ip}) - Proxy NOT working!"
                        elif detected_ip != "Unknown":
                            print(f"Proxy IP detected: {detected_ip}")
                            if detected_ip != real_ip:
                                ip_detected = f"Proxy IP ({detected_ip}) - Different from real IP ({real_ip})"
                            else:
                                ip_detected = f"Same IP detected ({detected_ip}) - Proxy may not be working"
                        else:
                            print("Could not determine IP address")
                            ip_detected = "Unknown IP"
                            
                    except Exception as e:
                        print(f"Could not analyze page content: {e}")
                        ip_detected = "Error analyzing IP"
                    
                    # Store results for this site
                    test_results[test_url] = {
                        "success": True,
                        "ip_detected": ip_detected,
                        "detected_ip": detected_ip,
                        "site_results": site_results,
                        "page_title": page_title if 'page_title' in locals() else "Unknown",
                        "content_length": len(page_content) if 'page_content' in locals() else 0
                    }
                    
                    # Wait between tests (2-4 seconds)
                    if i < len(bot_test_links) - 1:
                        await page.wait_for_timeout(int(random.uniform(2, 4) * 1000))
                        
                except Exception as e:
                    print(f"Error testing {test_url}: {e}")
                    test_results[test_url] = {
                        "success": False,
                        "error": str(e)
                    }

            await context.close()
            await browser.close()
            
            return {
                "scraper_id": self.scraper_id,
                "proxy_used": proxy_host is not None,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "test_results": test_results,
                "scraped_at": datetime.now().isoformat(),
                "success": True
            }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate that required parameters are present"""
        return True  # No required params for proxy test
    
    def get_description(self) -> str:
        """Return description of what this scraper does"""
        return "Tests proxy functionality using multiple bot detection sites to verify proxy is working and detect bot detection methods"
    
    def get_required_params(self) -> list:
        """Return list of required parameters for this scraper"""
        return []
    
    def pre_scrape_hook(self, params: Dict[str, Any]) -> None:
        """Hook called before scraping starts"""
        proxy_info = ""
        proxy_host = params.get('proxy_host') or os.getenv("IPROYAL_PROXY_HOST")
        proxy_port = params.get('proxy_port') or os.getenv("IPROYAL_PROXY_PORT")
        if proxy_host and proxy_port:
            proxy_info = f" with proxy: {proxy_host}:{proxy_port}"
        print(f"Starting comprehensive proxy test scrape{proxy_info}")
    
    def post_scrape_hook(self, result: Dict[str, Any]) -> None:
        """Hook called after scraping completes"""
        if result.get("success"):
            test_results = result.get("test_results", {})
            successful_tests = sum(1 for site_result in test_results.values() if site_result.get("success", False))
            total_tests = len(test_results)
            print(f"Completed proxy test scrape: {successful_tests}/{total_tests} sites successful")
        else:
            print(f"Proxy test scrape failed: {result.get('error', 'Unknown error')}") 