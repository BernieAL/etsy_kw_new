import os
import random
from seleniumwire import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class SeleniumStealthBase:
    """
    Base class for Selenium stealth configuration. Provides a get_stealth_driver method
    that returns a fully configured seleniumwire.undetected_chromedriver.Chrome instance with all
    stealth options, proxy support, and anti-bot JS applied.
    """
    def __init__(self):
        load_dotenv(dotenv_path="/app/.env")
        self.proxy_host = os.getenv("IPROYAL_PROXY_HOST")
        self.proxy_port = os.getenv("IPROYAL_PROXY_PORT")
        self.proxy_user = os.getenv("IPROYAL_PROXY_USER")
        self.proxy_pass = os.getenv("IPROYAL_PROXY_PASS")
        self.proxy = None
        if self.proxy_host and self.proxy_port:
            if self.proxy_user and self.proxy_pass:
                self.proxy = f"http://{self.proxy_user}:{self.proxy_pass}@{self.proxy_host}:{self.proxy_port}"
            else:
                self.proxy = f"http://{self.proxy_host}:{self.proxy_port}"

    def get_stealth_driver(self, proxy=None):
        """
        Returns a configured seleniumwire.undetected_chromedriver.Chrome instance with all stealth options.
        If proxy is provided, it overrides the .env proxy.
        """
        try:
            chrome_version = os.popen('google-chrome --version').read().strip().split()[-1].split('.')[0]
            print(f"Detected Chrome version: {chrome_version}")
            
            # Set up selenium-wire options for proxy
            proxy_to_use = proxy if proxy is not None else self.proxy
            seleniumwire_options = {}
            
            if proxy_to_use:
                print(f"🔒 Adding proxy to Chrome: {proxy_to_use}")
                seleniumwire_options = {
                    'proxy': {
                        'http': proxy_to_use,
                        'https': proxy_to_use
                    },
                    'verify_ssl': False  # Allow insecure SSL connections
                }
            else:
                print("⚠️  No proxy configured - using direct connection!")
            
            options = uc.ChromeOptions()
            
            # Essential Docker stability flags
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-component-extensions-with-background-pages')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            options.add_argument('--hide-scrollbars')
            options.add_argument('--mute-audio')
            options.add_argument('--no-first-run')
            options.add_argument('--safebrowsing-disable-auto-update')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-component-update')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-background-networking')
            
            # Advanced stealth flags
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors-spki-list')
            options.add_argument('--ignore-ssl-errors-spki-list')
            
            # Performance optimizations (but keep JavaScript enabled!)
            options.add_argument('--blink-settings=imagesEnabled=false')
            
            # Docker-specific optimizations
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--remote-debugging-address=0.0.0.0')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-webgl')
            options.add_argument('--disable-3d-apis')
            options.add_argument('--disable-accelerated-2d-canvas')
            options.add_argument('--disable-accelerated-jpeg-decoding')
            options.add_argument('--disable-accelerated-mjpeg-decode')
            options.add_argument('--disable-accelerated-video-decode')
            options.add_argument('--disable-gpu-sandbox')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-threaded-animation')
            options.add_argument('--disable-threaded-scrolling')
            options.add_argument('--disable-checker-imaging')
            options.add_argument('--disable-new-content-rendering-timeout')
            options.add_argument('--disable-image-animation-resync')
            options.add_argument('--disable-partial-raster')
            options.add_argument('--disable-smooth-scrolling')
            options.add_argument('--disable-low-res-tiling')
            options.add_argument('--disable-background-media-suspend')
            options.add_argument('--disable-background-video-track')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            
            # Ensure browser is visible and stable
            options.add_argument('--start-maximized')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            
            # Advanced stealth: Random window size
            window_sizes = [
                (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
                (1280, 720), (1600, 900), (1024, 768), (1280, 800)
            ]
            window_size = random.choice(window_sizes)
            options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
            
            # Advanced stealth: Rotate user agent with more realistic ones
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
            ]
            ua = random.choice(user_agents)
            options.add_argument(f'--user-agent={ua}')
            print(f"[Stealth] User-Agent set: {ua}")
            print(f"[Stealth] Window size set: {window_size[0]}x{window_size[1]}")
            
            # Initialize driver with selenium-wire (headed mode for debugging)
            driver = uc.Chrome(
                service=Service(ChromeDriverManager().install()),
                seleniumwire_options=seleniumwire_options,
                options=options,
                version_main=int(chrome_version)
                # Removed use_subprocess=True to fix blank page issue
            )
            print("[Stealth] seleniumwire.undetected-chromedriver initialized.")
            
            # Wait a moment for driver to stabilize
            time.sleep(3)
            
            # --- Advanced Stealth JavaScript ---
            def try_stealth(js, desc):
                try:
                    driver.execute_script(js)
                    print(f"[Stealth] {desc} applied.")
                except Exception as e:
                    print(f"[Stealth] {desc} failed: {e}")
            
            # Enhanced stealth - more aggressive anti-detection
            try_stealth("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                    configurable: true
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                    configurable: true
                });
                
                // Override platform to match user agent
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32',
                    configurable: true
                });
                
                // Add chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Override permissions to return granted
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({state: 'granted'})
                    }),
                    configurable: true
                });
                
                // Override device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                    configurable: true
                });
                
                // Override hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                    configurable: true
                });
                
                // Remove automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Override toString to hide automation
                const originalFunction = window.Function.prototype.toString;
                window.Function.prototype.toString = function() {
                    if (this === window.Function.prototype.toString) return originalFunction.call(this);
                    if (this === window.navigator.webdriver) return 'function get webdriver() { [native code] }';
                    return originalFunction.call(this);
                };
            """, "Enhanced stealth properties applied")
            
            # Advanced stealth: WebGL spoofing - improved to avoid Google/SwiftShader detection
            try_stealth("""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) { return 'Intel Inc.'; }
                    if (parameter === 37446) { return 'Intel Iris OpenGL Engine'; }
                    return getParameter(parameter);
                };
                
                // Also override WebGL2 context
                if (WebGL2RenderingContext) {
                    const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
                    WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) { return 'Intel Inc.'; }
                        if (parameter === 37446) { return 'Intel Iris OpenGL Engine'; }
                        return getParameter2(parameter);
                    };
                }
            """, "WebGL vendor/renderer spoofed")
            
            # Advanced stealth: Canvas fingerprinting protection
            try_stealth("""
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                    const context = originalGetContext.call(this, type, ...args);
                    if (type === '2d') {
                        const originalFillText = context.fillText;
                        context.fillText = function(...args) {
                            args[0] = args[0] + ' ';
                            return originalFillText.apply(this, args);
                        };
                    }
                    return context;
                };
            """, "Canvas fingerprinting protection applied")
            
            # Advanced stealth: Audio fingerprinting protection
            try_stealth("""
                const originalGetChannelData = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function(channel) {
                    const data = originalGetChannelData.call(this, channel);
                    const newData = new Float32Array(data.length);
                    for (let i = 0; i < data.length; i++) {
                        newData[i] = data[i] + (Math.random() * 0.0001);
                    }
                    return newData;
                };
            """, "Audio fingerprinting protection applied")
            
            # Advanced stealth: Timezone and locale spoofing
            try_stealth("""
                Object.defineProperty(Intl, 'DateTimeFormat', {
                    get: function() {
                        return function() {
                            return {
                                resolvedOptions: function() {
                                    return { timeZone: 'America/New_York' };
                                }
                            };
                        };
                    }
                });
            """, "Timezone spoofed")
            
            # Advanced stealth: Media devices spoofing
            try_stealth("""
                navigator.mediaDevices = {
                    enumerateDevices: () => Promise.resolve([
                        { kind: 'videoinput', deviceId: 'default', label: 'Default Camera' },
                        { kind: 'audioinput', deviceId: 'default', label: 'Default Microphone' }
                    ])
                };
            """, "Media devices spoofed")
            
            # Advanced stealth: Connection API spoofing
            try_stealth("""
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50,
                        downlink: 10,
                        saveData: false
                    })
                });
            """, "Connection API spoofed")
            
            # Advanced stealth: Battery API spoofing
            try_stealth("""
                Object.defineProperty(navigator, 'getBattery', {
                    get: () => () => Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 0.85
                    })
                });
            """, "Battery API spoofed")
            
            # Advanced stealth: Permissions API spoofing - improved to always return granted
            try_stealth("""
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = function(parameters) {
                    return Promise.resolve({ state: 'granted' });
                };
            """, "Permissions API spoofed")
            
            # Advanced stealth: Notification API spoofing
            try_stealth("""
                Object.defineProperty(Notification, 'permission', {
                    get: () => 'granted'
                });
            """, "Notification API spoofed")
            
            # Advanced stealth: Screen orientation spoofing
            try_stealth("""
                Object.defineProperty(screen, 'orientation', {
                    get: () => ({
                        type: 'landscape-primary',
                        angle: 0
                    })
                });
            """, "Screen orientation spoofed")
            
            # Set window size
            try:
                driver.set_window_size(window_size[0], window_size[1])
                print(f"[Stealth] Window size set to {window_size[0]}x{window_size[1]}.")
            except Exception as e:
                print(f"[Stealth] Window size spoof failed: {e}")
            
            # Advanced stealth: Random mouse movements simulation
            try_stealth("""
                // Simulate random mouse movements
                setInterval(() => {
                    const event = new MouseEvent('mousemove', {
                        clientX: Math.random() * window.innerWidth,
                        clientY: Math.random() * window.innerHeight,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                }, Math.random() * 5000 + 2000);
            """, "Random mouse movements simulation")
            
            print("[Stealth] All advanced stealth settings applied.")
            return driver
            
        except Exception as e:
            print(f"Error initializing ChromeDriver: {str(e)}")
            raise 