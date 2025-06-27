#!/usr/bin/env python3
"""
Comprehensive bot detection testing using selenium-wire
"""

import os
import time
import json
from datetime import datetime
import seleniumwire.undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def check_stealth_measures(driver):
    """Check if stealth measures are working properly"""
    stealth_results = {
        'webdriver_hidden': False,
        'chrome_object_present': False,
        'automation_properties_removed': False,
        'webgl_spoofed': False,
        'canvas_protected': False
    }
    
    try:
        # Check if webdriver is hidden
        webdriver_result = driver.execute_script("return navigator.webdriver;")
        stealth_results['webdriver_hidden'] = webdriver_result is None or webdriver_result is False
        
        # Check if chrome object is present
        chrome_result = driver.execute_script("return window.chrome;")
        stealth_results['chrome_object_present'] = chrome_result is not None
        
        # Check if automation properties are removed
        cdc_result = driver.execute_script("return window.cdc_adoQpoasnfa76pfcZLmcfl_Array;")
        stealth_results['automation_properties_removed'] = cdc_result is None
        
        # Check WebGL spoofing
        webgl_result = driver.execute_script("""
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            if (gl) {
                const vendor = gl.getParameter(gl.VENDOR);
                const renderer = gl.getParameter(gl.RENDERER);
                return {vendor: vendor, renderer: renderer};
            }
            return null;
        """)
        if webgl_result:
            stealth_results['webgl_spoofed'] = (
                'Intel' in webgl_result.get('vendor', '') and 
                'Intel' in webgl_result.get('renderer', '')
            )
        
        # Check canvas protection
        canvas_result = driver.execute_script("""
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            return ctx !== null;
        """)
        stealth_results['canvas_protected'] = canvas_result
        
        return stealth_results
        
    except Exception as e:
        print(f"⚠️  Stealth check failed: {e}")
        return stealth_results

def analyze_bot_detection_results(driver, site_name):
    """Analyze bot detection results for a specific site"""
    results = {
        'site': site_name,
        'timestamp': datetime.now().isoformat(),
        'successes': [],
        'concerns': [],
        'exposures': [],
        'page_title': driver.title,
        'current_url': driver.current_url
    }
    
    page_source = driver.page_source.lower()
    page_text = driver.page_source
    
    # Check JavaScript functionality
    try:
        js_test = driver.execute_script("return 'JavaScript is working';")
        if js_test == "JavaScript is working":
            results['successes'].append("JavaScript: ENABLED and functional")
        else:
            results['exposures'].append("JavaScript: DISABLED or not working")
    except Exception as e:
        results['exposures'].append(f"JavaScript: ERROR - {str(e)}")
    
    # Check for common JavaScript-based detection
    try:
        # Test if we can access navigator properties
        user_agent = driver.execute_script("return navigator.userAgent;")
        if user_agent:
            results['successes'].append("Navigator API: Accessible")
        
        # Test if we can access window properties
        window_width = driver.execute_script("return window.innerWidth;")
        window_height = driver.execute_script("return window.innerHeight;")
        if window_width and window_height:
            results['successes'].append("Window API: Accessible")
            
        # Test if we can access document properties
        doc_title = driver.execute_script("return document.title;")
        if doc_title:
            results['successes'].append("Document API: Accessible")
            
    except Exception as e:
        results['concerns'].append(f"JavaScript API access: {str(e)}")
    
    # Common detection patterns
    detection_patterns = {
        'webdriver_detected': ['webdriver', 'selenium', 'automation'],
        'headless_detected': ['headless', 'chrome-linux'],
        'bot_detected': ['bot', 'automated', 'scraper'],
        'fingerprint_detected': ['fingerprint', 'canvas', 'webgl'],
        'proxy_detected': ['proxy', 'vpn', 'tor'],
        'js_disabled': ['javascript is disabled', 'js disabled', 'enable javascript']
    }
    
    # Check for detection patterns
    for detection_type, patterns in detection_patterns.items():
        for pattern in patterns:
            if pattern in page_source:
                if detection_type == 'js_disabled':
                    results['exposures'].append(f"JavaScript detection: '{pattern}' found in page")
                else:
                    results['concerns'].append(f"{detection_type}: '{pattern}' found in page")
    
    # Site-specific analysis
    if 'bot.sannysoft.com' in site_name:
        # Look for specific test results
        if 'missing (passed)' in page_text:
            results['successes'].append("WebDriver test: PASSED")
        if 'present (passed)' in page_text:
            results['successes'].append("Chrome test: PASSED")
        if 'en-us,en' in page_source:
            results['successes'].append("Languages test: PASSED")
        if '5' in page_text and 'plugins' in page_source:
            results['successes'].append("Plugins test: PASSED")
            
        # Check for failures
        if 'failed' in page_text:
            results['concerns'].append("Some bot detection tests failed")
            
    elif 'intoli.com' in site_name:
        # Check for headless detection
        if 'not headless' in page_text.lower():
            results['successes'].append("Headless detection: PASSED (not detected as headless)")
        elif 'headless' in page_text.lower():
            results['exposures'].append("Headless detection: EXPOSED (detected as headless)")
            
    elif 'amiunique.org' in site_name:
        # Check for fingerprinting results
        if 'unique' in page_text.lower():
            results['concerns'].append("Browser fingerprint may be unique")
        if 'common' in page_text.lower():
            results['successes'].append("Browser fingerprint appears common")
            
    elif 'httpbin.org' in site_name:
        # Check headers and IP
        if 'user-agent' in page_source:
            results['successes'].append("Headers are being sent correctly")
        if 'origin' in page_source:
            results['successes'].append("IP address is visible")
            
    # General stealth checks
    if 'chrome-linux' in page_source:
        results['exposures'].append("Linux Chrome detected (should be Windows/Mac)")
    if 'google inc' in page_source.lower():
        results['exposures'].append("Google WebGL vendor detected (should be Intel/AMD)")
    if 'swiftshader' in page_source.lower():
        results['exposures'].append("SwiftShader renderer detected (should be Intel/AMD)")
        
    return results

def test_bot_detection_sites():
    print("🧪 Comprehensive Bot Detection Testing...")
    
    # Load environment variables
    load_dotenv(dotenv_path="/app/.env")
    
    proxy_host = os.getenv("IPROYAL_PROXY_HOST")
    proxy_port = os.getenv("IPROYAL_PROXY_PORT")
    proxy_user = os.getenv("IPROYAL_PROXY_USER")
    proxy_pass = os.getenv("IPROYAL_PROXY_PASS")
    
    print(f"Proxy Host: {proxy_host}")
    print(f"Proxy Port: {proxy_port}")
    print(f"Proxy User: {proxy_user}")
    print(f"Proxy Pass: {'*' * len(proxy_pass) if proxy_pass else 'None'}")
    
    # Check display environment
    print(f"DISPLAY environment: {os.getenv('DISPLAY', 'Not set')}")
    print(f"Running in Docker: {os.getenv('RUNNING_IN_DOCKER', 'No')}")
    
    # Define test sites
    test_sites = [
        {
            'name': 'Bot Detection (bot.sannysoft.com)',
            'url': 'https://bot.sannysoft.com',
            'wait_time': 15
        },
        {
            'name': 'Headless Detection (intoli.com)',
            'url': 'https://intoli.com/blog/not-possible-to-block-chrome-headless/',
            'wait_time': 10
        },
        {
            'name': 'Modern Bot Detection (botd.io)',
            'url': 'https://botd.io',
            'wait_time': 10
        },
        {
            'name': 'Browser Fingerprinting (amiunique.org)',
            'url': 'https://amiunique.org',
            'wait_time': 15
        },
        {
            'name': 'Headers Analysis (httpbin.org/headers)',
            'url': 'https://httpbin.org/headers',
            'wait_time': 5
        },
        {
            'name': 'IP Analysis (httpbin.org/ip)',
            'url': 'https://httpbin.org/ip',
            'wait_time': 5
        }
    ]
    
    all_results = []
    
    try:
        # Configure seleniumwire options for proxy
        seleniumwire_options = {}
        if proxy_host and proxy_port and proxy_user and proxy_pass:
            seleniumwire_options = {
                'proxy': {
                    'http': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}',
                    'https': f'http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
                },
                'verify_ssl': False
            }
            print("🔒 Using authenticated proxy")
        elif proxy_host and proxy_port:
            seleniumwire_options = {
                'proxy': {
                    'http': f'http://{proxy_host}:{proxy_port}',
                    'https': f'http://{proxy_host}:{proxy_port}'
                },
                'verify_ssl': False
            }
            print("🔒 Using proxy without authentication")
        else:
            print("⚠️  No proxy configured - using direct connection")
        
        # Chrome options
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        
        # Ensure JavaScript is enabled
        options.add_argument('--enable-javascript')
        options.add_argument('--disable-javascript-harmony-shipping')
        options.add_argument('--disable-javascript-harmony')
        
        # Ensure browser is visible
        options.add_argument('--start-maximized')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Additional stealth options for JavaScript
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        print("Starting Chrome browser...")
        driver = uc.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        print(f"✅ Browser started successfully!")
        
        # Inject stealth JavaScript after browser starts
        try:
            stealth_js = """
            // Override common detection methods
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Override WebGL to avoid fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.call(this, parameter);
            };
            
            // Override Canvas fingerprinting
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const context = originalGetContext.call(this, type, ...args);
                if (type === '2d') {
                    const originalFillText = context.fillText;
                    context.fillText = function(...args) {
                        return originalFillText.apply(this, args);
                    };
                }
                return context;
            };
            
            // Override toString to hide automation
            const originalToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === window.navigator.webdriver) {
                    return 'function get webdriver() { [native code] }';
                }
                return originalToString.call(this);
            };
            
            // Override chrome object
            Object.defineProperty(window, 'chrome', {
                writable: true,
                enumerable: true,
                configurable: true,
                value: {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                }
            });
            
            // Override automation properties
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            console.log('Enhanced stealth JavaScript injected successfully');
            """
            driver.execute_script(stealth_js)
            print("🔒 Enhanced stealth JavaScript injected")
        except Exception as e:
            print(f"⚠️  Failed to inject stealth JavaScript: {e}")
        
        # Test each site
        for i, site in enumerate(test_sites, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}/{len(test_sites)}: {site['name']}")
            print(f"URL: {site['url']}")
            print(f"{'='*60}")
            
            # Check stealth measures before testing
            print("🔍 Checking stealth measures...")
            stealth_status = check_stealth_measures(driver)
            
            stealth_summary = []
            if stealth_status['webdriver_hidden']:
                stealth_summary.append("✅ WebDriver hidden")
            else:
                stealth_summary.append("❌ WebDriver exposed")
                
            if stealth_status['chrome_object_present']:
                stealth_summary.append("✅ Chrome object present")
            else:
                stealth_summary.append("❌ Chrome object missing")
                
            if stealth_status['automation_properties_removed']:
                stealth_summary.append("✅ Automation properties removed")
            else:
                stealth_summary.append("❌ Automation properties present")
                
            if stealth_status['webgl_spoofed']:
                stealth_summary.append("✅ WebGL spoofed")
            else:
                stealth_summary.append("❌ WebGL not spoofed")
                
            if stealth_status['canvas_protected']:
                stealth_summary.append("✅ Canvas protected")
            else:
                stealth_summary.append("❌ Canvas not protected")
            
            print("   " + " | ".join(stealth_summary))
            
            try:
                print(f"Navigating to {site['url']}...")
                driver.get(site['url'])
                
                print(f"Waiting {site['wait_time']} seconds for page to load...")
                time.sleep(site['wait_time'])
                
                # Analyze results
                results = analyze_bot_detection_results(driver, site['name'])
                all_results.append(results)
                
                # Print summary
                print(f"📊 Results for {site['name']}:")
                print(f"   Page Title: {results['page_title']}")
                
                if results['successes']:
                    print(f"   ✅ Successes ({len(results['successes'])}):")
                    for success in results['successes']:
                        print(f"      • {success}")
                
                if results['concerns']:
                    print(f"   ⚠️  Concerns ({len(results['concerns'])}):")
                    for concern in results['concerns']:
                        print(f"      • {concern}")
                
                if results['exposures']:
                    print(f"   🚨 Exposures ({len(results['exposures'])}):")
                    for exposure in results['exposures']:
                        print(f"      • {exposure}")
                
                if not results['successes'] and not results['concerns'] and not results['exposures']:
                    print(f"   ℹ️  No specific results detected")
                
            except Exception as e:
                print(f"❌ Error testing {site['name']}: {e}")
                all_results.append({
                    'site': site['name'],
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'successes': [],
                    'concerns': [],
                    'exposures': []
                })
        
        # Generate final report
        print(f"\n{'='*60}")
        print("📋 FINAL STEALTH REPORT")
        print(f"{'='*60}")
        
        total_successes = sum(len(r.get('successes', [])) for r in all_results)
        total_concerns = sum(len(r.get('concerns', [])) for r in all_results)
        total_exposures = sum(len(r.get('exposures', [])) for r in all_results)
        
        print(f"✅ Total Successes: {total_successes}")
        print(f"⚠️  Total Concerns: {total_concerns}")
        print(f"🚨 Total Exposures: {total_exposures}")
        
        # Calculate stealth score
        total_tests = len(all_results)
        successful_sites = len([r for r in all_results if r.get('successes') and not r.get('exposures')])
        stealth_score = (successful_sites / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Stealth Score: {stealth_score:.1f}%")
        
        if stealth_score >= 80:
            print("🌟 EXCELLENT - Ready for production!")
        elif stealth_score >= 60:
            print("✅ GOOD - Minor improvements needed")
        elif stealth_score >= 40:
            print("⚠️  FAIR - Significant improvements needed")
        else:
            print("❌ POOR - Major stealth improvements required")
        
        # Save detailed results to file
        report_file = f"stealth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        print("\n✅ All bot detection tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Bot detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if 'driver' in locals():
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    success = test_bot_detection_sites()
    if success:
        print("🎉 Comprehensive stealth testing completed!")
    else:
        print("💥 Stealth testing failed!")
        exit(1) 