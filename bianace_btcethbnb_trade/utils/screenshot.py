import os
import json
import time
import subprocess
import logging
from playwright.sync_api import sync_playwright
from config.settings import BINANCE_CONTRACT_URLS
from datetime import datetime

def save_session(context, session_file='binance_session.json'):
    """
    Save browser session (cookies) to a file
    
    Args:
        context: Playwright browser context
        session_file (str): Path to save session file
    """
    cookies = context.cookies()
    with open(session_file, 'w') as f:
        json.dump(cookies, f)
    print(f"Session saved to {session_file}")


def load_session(context, session_file='binance_session.json'):
    """
    Load browser session (cookies) from a file
    
    Args:
        context: Playwright browser context
        session_file (str): Path to session file
    
    Returns:
        bool: True if session loaded successfully, False otherwise
    """
    try:
        with open(session_file, 'r') as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"Session loaded from {session_file}")
        return True
    except FileNotFoundError:
        print(f"Session file {session_file} not found")
        return False
    except Exception as e:
        print(f"Error loading session: {str(e)}")
        return False


def capture_screenshot(currency, use_session=True):
    """
    Capture screenshot of Binance futures contract page with improved loading handling
    
    Args:
        currency (str): Currency pair to capture (e.g., BTCUSDT)
        use_session (bool): Whether to use saved session cookies
    
    Returns:
        str: Path to the saved screenshot file
    """
    # Get the URL for the specific currency
    url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
    
    # Create timestamped filename with date and currency subdirectories
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp_str}_{currency}_trade.png'
    
    # Create path with date and currency subdirectories
    currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
    os.makedirs(currency_dir, exist_ok=True)
    
    filepath = os.path.join(currency_dir, filename)
    
    # Ensure screenshots directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Load saved session if available and requested
            if use_session:
                load_session(context)
            
            # Set a larger viewport to ensure we capture all elements
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to the Binance futures page with a longer timeout
            page.goto(url, timeout=60000)
            
            # Wait for page to load - using load event
            page.wait_for_load_state("load", timeout=30000)
            
            # Additional wait to ensure dynamic content is loaded
            page.wait_for_timeout(10000)
            
            # Capture full page screenshot
            page.screenshot(path=filepath, full_page=True)
            
            print(f"Screenshot saved to {filepath}")
            
        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
            raise
        
        finally:
            browser.close()
    
    return filepath


def manual_session_setup(currency='BTCUSDT'):
    """
    Creates a separate script for manual browser configuration.
    This function creates a script that you can run separately to manually 
    configure the browser and save the session.
    
    Args:
        currency (str): Currency pair to configure (e.g., BTCUSDT)
    """
    # Get the URL for the specific currency
    url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
    
    script_content = f'''#!/usr/bin/env python3
"""
Manual browser configuration script.
Run this script to open a browser window where you can manually configure
the Binance page settings. When you close the browser, your session will
be saved automatically.
"""

import json
import time
import os
import sys

# Add the project root directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import BINANCE_CONTRACT_URLS


def manual_setup(currency='{currency}'):
    """
    Open browser for manual configuration and save session when closed.
    
    Args:
        currency (str): Currency pair to configure (e.g., BTCUSDT)
    """
    # Get the URL for the specific currency
    url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['{currency}'])
    
    print(f"Opening browser for manual configuration of {{currency}}...")
    print("Please configure your desired settings on the page.")
    print("When finished, press Enter in this terminal to continue...")
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url)
            print("Browser opened. After configuring your settings, press Enter in this terminal to save session and continue...")
            input()  # Wait for user to press Enter instead of waiting for browser close
            
            # Save session before closing browser
            cookies = context.cookies()
            with open('binance_session.json', 'w') as f:
                json.dump(cookies, f)
            print("Session saved to binance_session.json")
            
        except Exception as e:
            print(f"Error during manual setup: {{str(e)}}")
        finally:
            browser.close()


if __name__ == "__main__":
    import sys
    currency = sys.argv[1] if len(sys.argv) > 1 else '{currency}'
    manual_setup(currency)
'''
    
    # Write the script to a file
    script_path = os.path.join('utils', 'manual_configurator.py')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"Manual configuration script created at {script_path}")
    print(f"To use it, run: python3 {script_path}")
    print("After running the script and configuring the page, the session will be saved automatically.")
    print("Then you can use capture_screenshot() with use_session=True to apply your settings.")


def capture_screenshot_with_manual_config_and_save(currency):
    """
    DEPRECATED: Use the manual_configurator.py script instead.
    This function provides instructions for manual configuration.
    
    Args:
        currency (str): Currency pair to capture (e.g., BTCUSDT)
    
    Returns:
        str: Path to the saved screenshot file
    """
    print("For manual configuration, please run the manual setup function first:")
    manual_session_setup(currency)
    print("\nAfter running the manual configuration script and setting your preferences:")
    print("1. The session will be saved automatically when you close the browser")
    print("2. Then run capture_screenshot() with use_session=True to use your settings")
    
    # Take the screenshot with the saved session
    return capture_screenshot(currency, use_session=True)


def get_chrome_cookies_manually():
    """
    Instructions for manually getting cookies from Chrome browser.
    """
    print("To manually get cookies from your Chrome browser:")
    print("1. Open Chrome and log in to Binance")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the 'Application' tab (or 'Storage' in some versions)")
    print("4. In the left panel, expand 'Cookies' and select 'https://www.binance.com'")
    print("5. Select all cookies (Ctrl+A or Cmd+A), copy them (Ctrl+C or Cmd+C)")
    print("6. Create a binance_session.json file with the cookies data")
    print("\nAlternatively, you can use the manual_configurator.py script to do this automatically.")


def capture_with_chrome_profile(currency):
    """
    Capture screenshot using a persistent context that mimics your Chrome setup.
    This method creates a new Chrome profile with your settings but doesn't require
    direct access to your main Chrome profile.
    
    Args:
        currency (str): Currency pair to capture (e.g., BTCUSDT)
    """
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp_str}_{currency}_trade.png'
    filepath = os.path.join('data', 'screenshots', date_dir, filename)
    
    # Ensure screenshots directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with sync_playwright() as p:
        # Create a new user data directory to store session data
        user_data_dir = os.path.join(os.getcwd(), 'chrome_user_data')
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Launch Chrome with a persistent context (like opening a new Chrome window)
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Navigate to the target page
        page = browser.new_page()
        url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
        page.goto(url)
        
        print("Browser opened. Please log in to Binance and set your preferences.")
        print("After setting up, press Enter in this terminal to continue...")
        input()
        
        # Wait for page to load
        page.wait_for_load_state("load", timeout=30000)
        page.wait_for_timeout(10000)
        
        # Capture full page screenshot
        page.screenshot(path=filepath, full_page=True)
        
        # Save the session cookies for future use
        cookies = browser.cookies()
        with open('binance_session.json', 'w') as f:
            json.dump(cookies, f)
        print("Session saved to binance_session.json")
        
        print(f"Screenshot saved to {filepath}")
        
        browser.close()
    
    return filepath


def connect_to_existing_chrome_and_screenshot(currency):
    """
    Connect to an existing Chrome instance with remote debugging enabled.
    To use this function, you need to start Chrome with remote debugging:
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug
    Then run this function.
    
    Args:
        currency (str): Currency pair to capture (e.g., BTCUSDT)
    """
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('binance_trade_analyzer')
    
    logger.info("Capturing screenshot...")
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    
    # Create directory path with currency folder
    currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
    os.makedirs(currency_dir, exist_ok=True)
    
    filename = f'{timestamp_str}_{currency}_trade.png'
    filepath = os.path.join(currency_dir, filename)
    
    with sync_playwright() as p:
        # Connect to an existing Chrome instance
        # This requires Chrome to be started with --remote-debugging-port=9222
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the first available context or create a new one
            if browser.contexts:
                context = browser.contexts[0]
            else:
                context = browser.new_context()
            
            # Create a new page or use an existing one
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()
            
            # Navigate to the target URL
            url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
            page.goto(url, timeout=60000)
            
            # Wait for page to load with extended timeout
            page.wait_for_load_state("load", timeout=60000)
            
            # Wait for key UI elements to ensure page is ready
            try:
                # Wait for chart container to be visible
                page.wait_for_selector('[data-testid="chart-container"], .tradingview-chart, .chart-wrapper, .chart-container, .tv-chart-container', 
                                     state='visible', timeout=30000)
                
                # Wait for trading panel to be visible
                page.wait_for_selector('.trade-panel, .order-form, .position-info', 
                                     state='visible', timeout=20000)
                
                # Wait for market data to be visible
                page.wait_for_selector('.price-data, .market-price, .chart-price', 
                                     state='visible', timeout=15000)
            except Exception as e:
                logger.warning(f"Some UI elements not fully loaded: {str(e)}")
                print("Proceeding with screenshot as basic elements are present")
            
            # Capture only the visible viewport to avoid timeout issues with complex pages
            # Full page screenshots can fail on trading interfaces with infinite scroll
            # Retry screenshot with reduced timeout and error handling
            screenshot_success = False
            for attempt in range(3):
                try:
                    page.screenshot(path=filepath, full_page=False, timeout=30000)
                    screenshot_success = True
                    break
                except TimeoutError as te:
                    print(f"Screenshot attempt {attempt + 1} failed: {str(te)}")
                    if attempt == 2:  # Last attempt
                        print("All screenshot attempts failed. Proceeding with error state.")
                        raise
                    # Wait before retry
                    time.sleep(5)
            
            if screenshot_success:
                logger.info(f"Screenshot saved to {filepath}")

            # Note: We don't close the browser as it's connected to an existing instance
            return filepath
            
        except Exception as e:
            print(f"Error connecting to existing Chrome: {str(e)}")
            print("Make sure Chrome is running with remote debugging enabled:")
            print("For example: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            raise


def instructions_for_remote_debugging_chrome():
    """
    Provide instructions for setting up Chrome with remote debugging.
    """
    print("To use your existing Chrome browser for screenshots:")
    print("1. Close all Chrome windows")
    print("2. Open Terminal and run this command:")
    print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug")
    print("3. When Chrome opens, log in to Binance and set your preferences")
    print("4. Then run the following command in another terminal:")
    print("   python3 -c \"from utils.screenshot import connect_to_existing_chrome_and_screenshot; connect_to_existing_chrome_and_screenshot('BTCUSDT')\"")
    print("\nNote: Using a separate user-data-dir prevents conflicts with your normal Chrome usage.")


def start_chrome_with_debugging_and_urls():
    """
    Automatically start Chrome with remote debugging enabled and navigate to Binance URLs.
    This function starts Chrome with remote debugging port 9222 and opens all Binance contract pages.
    
    Returns:
        bool: True if Chrome started successfully, False otherwise
    """
    logger = logging.getLogger('binance_trade_analyzer')
    
    # Define the Chrome path and debugging parameters
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # Check if Chrome exists at the expected path
    if not os.path.exists(chrome_path):
        print(f"Chrome not found at {chrome_path}")
        # Try alternative paths
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        else:
            print("Could not find Chrome browser")
            return False
    
    # Prepare the URLs to open
    urls = [url for url in BINANCE_CONTRACT_URLS.values()]
    
    # Construct the command to start Chrome with remote debugging
    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=/tmp/chrome_debug",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled"
    ]
    
    # Add the URLs to the command
    cmd.extend(urls)
    
    try:
        # Start Chrome with debugging enabled
        subprocess.Popen(cmd)
        print(f"Chrome started with remote debugging on port 9222")
        print(f"Navigating to Binance URLs: {list(BINANCE_CONTRACT_URLS.values())}")
        
        # Wait a bit for the browser to start
        time.sleep(5)
        
        return True
    except Exception as e:
        logger.error(f"Failed to start Chrome with debugging: {str(e)}")
        return False


def launch_chrome_with_remote_debugging():
    """
    Provides instructions for launching Chrome with remote debugging enabled.
    This is required for using existing Chrome instance for screenshots.
    """
    print("To use existing Chrome browser for screenshots, please follow these steps:")
    print("\nOn macOS, run the following command in Terminal:")
    print("    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug")
    print("\nOn Windows, run the following command in Command Prompt:")
    print("    start chrome --remote-debugging-port=9222 --user-data-dir=C:\\temp\\chrome_debug")
    print("\nOn Linux, run the following command in terminal:")
    print("    google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug")
    print("\nThen run your Python script to capture screenshots using the existing Chrome instance.")
    print("Remember to keep the Chrome window open while the script is running.")


def capture_multiple_screenshots(currencies, capture_times_per_currency=1):
    """
    Capture screenshots for multiple currencies, with ability to capture multiple times per currency.
    
    Args:
        currencies (list): List of currency pairs to capture (e.g., ['BTCUSDT', 'ETHUSDT'])
        capture_times_per_currency (int): Number of times to capture each currency
    
    Returns:
        list: List of file paths to saved screenshots
    """
    from playwright.sync_api import sync_playwright
    import time
    
    file_paths = []
    
    # Get the date for directory naming
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    
    with sync_playwright() as p:
        # Launch a new Chrome instance
        try:
            browser = p.chromium.launch(
                headless=False,  # Keep visible to allow for manual login
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-ipc-flooding-protection",
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps",
                    "--disable-backgrounding-occluded-windows"
                ]
            )
            
            # Create a new context
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Load session if it exists
            load_session(context)
            
            for currency in currencies:
                url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
                
                for i in range(capture_times_per_currency):
                    page = None
                    try:
                        # Create a new page for each capture
                        page = context.new_page()
                        
                        # Navigate to the target URL
                        page.goto(url, timeout=60000)
                        
                        # Wait for page to load with extended timeout
                        page.wait_for_load_state("load", timeout=60000)
                        
                        # Instead of waiting for networkidle, wait for a fixed time to allow resources to load
                        # Binance pages often have ongoing network activity that prevents reaching networkidle state
                        page.wait_for_timeout(15000)
                        
                        # Wait for specific elements that indicate the page is ready
                        try:
                            # Wait for chart or trading interface elements to be loaded
                            page.wait_for_selector('[data-testid="chart-container"], .tradingview-chart, .chart-wrapper, .chart-container, .tv-chart-container', timeout=30000)
                        except:
                            # If specific selectors are not found, continue with the screenshot
                            print("Specific chart elements not found, proceeding with screenshot")
                        
                        # Additional wait for dynamic content to visually render
                        page.wait_for_timeout(5000)
                        
                        # Create timestamped filename with date and currency subdirectories
                        current_time = datetime.now()
                        timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')
                        if capture_times_per_currency > 1:
                            filename = f'{timestamp_str}_{currency}_trade_{i+1}.png'
                        else:
                            filename = f'{timestamp_str}_{currency}_trade.png'
                        
                        # Create path with date and currency subdirectories
                        currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
                        os.makedirs(currency_dir, exist_ok=True)
                        
                        filepath = os.path.join(currency_dir, filename)
                        
                        # Ensure screenshots directory exists
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        
                        # Capture full page screenshot with extended timeout
                        page.screenshot(path=filepath, full_page=True, timeout=120000)
                        
                        print(f"Screenshot {i+1} for {currency} saved to {filepath}")
                        file_paths.append(filepath)
                        
                    except Exception as e:
                        print(f"Error capturing screenshot for {currency} (attempt {i+1}): {str(e)}")
                        # Continue with next currency instead of failing completely
                        continue
                    finally:
                        # Close the page after capturing (only if page exists and not already closed)
                        if page:
                            try:
                                page.close()
                            except Exception as e:
                                print(f"Error closing page for {currency}: {str(e)}")
                                pass  # Page might already be closed
            
            # Save session when done
            save_session(context)
            
            # Close the browser after all screenshots
            browser.close()
            
            return file_paths
            
        except Exception as e:
            print(f"Error launching new browser: {str(e)}")
            if 'browser' in locals():
                try:
                    browser.close()
                except:
                    pass
            raise


def capture_multiple_screenshots_existing_browser(currencies, capture_times_per_currency=1):
    """
    Capture screenshots for multiple currencies using an existing browser instance,
    with ability to capture multiple times per currency.
    
    Args:
        currencies (list): List of currency pairs to capture (e.g., ['BTCUSDT', 'ETHUSDT'])
        capture_times_per_currency (int): Number of times to capture each currency
    
    Returns:
        list: List of file paths to saved screenshots
    """
    from playwright.sync_api import sync_playwright
    import time
    import logging
    from datetime import datetime
    from config.settings import BINANCE_CONTRACT_URLS
    
    logger = logging.getLogger('binance_trade_analyzer')
    
    file_paths = []
    
    # Get the date for directory naming
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    
    with sync_playwright() as p:
        # Connect to an existing Chrome instance
        # This requires Chrome to be started with --remote-debugging-port=9222
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Successfully connected to existing Chrome instance")
            
            # Check if there are any pages already open
            contexts = browser.contexts
            if contexts:
                context = contexts[0]  # Use the first context
            else:
                context = browser.new_context()
                
            # Load session if it exists
            load_session(context, 'binance_session.json')
            
            for currency in currencies:
                url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
                
                # Try to find an existing page for this currency
                page = None
                for p in context.pages:
                    if url in p.url or currency in p.url:
                        page = p
                        break
                
                # If no existing page found for this currency, create a new one
                if not page:
                    page = context.new_page()
                    page.goto(url, timeout=60000)
                
                for i in range(capture_times_per_currency):
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            # Bring the page to front to ensure it's active
                            page.bring_to_front()
                            
                            # Wait for page to be fully loaded and dynamic content to render
                            page.wait_for_load_state("load", timeout=30000)
                            
                            # Additional wait for JavaScript and dynamic content to render
                            page.wait_for_timeout(20000)
                            
                            # Try to wait for specific elements that should be present on Binance futures page
                            selectors_to_wait = [
                                '[data-testid="chart-container"]', 
                                '.tradingview-chart', 
                                '.chart-wrapper', 
                                '.chart-container', 
                                '.tv-chart-container',
                                '.futures-chart',
                                '.price-container'
                            ]
                            
                            element_found = False
                            for selector in selectors_to_wait:
                                try:
                                    page.wait_for_selector(selector, timeout=10000)
                                    element_found = True
                                    print(f"Found element: {selector}")
                                    break
                                except:
                                    continue
                            
                            if not element_found:
                                print("No specific chart elements found, proceeding with screenshot after additional wait")
                                # Wait a bit more if no specific elements are found
                                page.wait_for_timeout(10000)
                            
                            # Additional wait for dynamic content to visually render
                            page.wait_for_timeout(5000)
                            
                            # Create timestamped filename with date and currency subdirectories
                            current_time = datetime.now()
                            timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')
                            if capture_times_per_currency > 1:
                                filename = f'{timestamp_str}_{currency}_trade_{i+1}.png'
                            else:
                                filename = f'{timestamp_str}_{currency}_trade.png'
                            
                            # Create path with date and currency subdirectories
                            currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
                            os.makedirs(currency_dir, exist_ok=True)
                            
                            filepath = os.path.join(currency_dir, filename)
                            
                            # Ensure screenshots directory exists
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            
                            # Capture screenshot - try viewport screenshot instead of full page
                            # Full page screenshots can fail on complex dynamic pages
                            page.screenshot(path=filepath, full_page=False, timeout=120000)
                            
                            print(f"Screenshot {i+1} for {currency} saved to {filepath}")
                            file_paths.append(filepath)
                            
                            # Success, break out of retry loop
                            break
                            
                        except Exception as e:
                            retry_count += 1
                            print(f"Error capturing screenshot for {currency} (attempt {i+1}, retry {retry_count}): {str(e)}")
                            
                            if retry_count < max_retries:
                                print(f"Retrying in 5 seconds...")
                                time.sleep(5)
                            else:
                                print(f"Failed to capture screenshot for {currency} after {max_retries} attempts")
                                continue  # Continue with next currency instead of failing completely
            
            # Save session when done - ensuring browser context is still available
            try:
                if context and browser and browser.is_connected():
                    save_session(context, 'binance_session.json')
            except Exception as e:
                print(f"Error saving session: {str(e)}")
                # Continue even if session saving fails
                
            # Don't close the browser as it's connected to an existing instance
            # browser.close()  # Commented out since we're using existing browser
            
            return file_paths
            
        except Exception as e:
            print(f"Error connecting to existing Chrome: {str(e)}")
            print("Make sure Chrome is running with remote debugging enabled:")
            print("For example: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug")
            return []


def capture_multiple_screenshots_new_browser(currencies, capture_times_per_currency=1):
    """
    Capture screenshots for multiple currencies using a newly launched browser instance,
    with ability to capture multiple times per currency.
    
    Args:
        currencies (list): List of currency pairs to capture (e.g., ['BTCUSDT', 'ETHUSDT'])
        capture_times_per_currency (int): Number of times to capture each currency
    
    Returns:
        list: List of file paths to saved screenshots
    """
    from playwright.sync_api import sync_playwright
    import time
    
    file_paths = []
    
    # Get the date for directory naming
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    
    with sync_playwright() as p:
        # Launch a new Chrome instance
        browser = None
        try:
            browser = p.chromium.launch(
                headless=False,  # Keep visible to allow for manual login
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-ipc-flooding-protection",
                    "--disable-background-timer-throttling",
                    "--disable-renderer-backgrounding",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-default-apps",
                    "--disable-backgrounding-occluded-windows",
                    # Add arguments to prevent crashes
                    "--disable-extensions",
                    "--disable-plugins",
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-ipc-flooding-protection"
                ]
            )
            
            # Create a new context
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Load session if it exists
            load_session(context, 'binance_session.json')
            
            # Process all currencies and captures with a single browser instance
            for currency in currencies:
                url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
                
                for i in range(capture_times_per_currency):
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        page = None
                        try:
                            # Check if browser is still connected before creating a new page
                            if not browser or not browser.is_connected():
                                print("Browser disconnected, attempting to relaunch...")
                                # Relaunch browser if disconnected
                                if browser:
                                    try:
                                        browser.close()
                                    except:
                                        pass
                                browser = p.chromium.launch(
                                    headless=False,
                                    args=[
                                        "--disable-blink-features=AutomationControlled",
                                        "--disable-dev-shm-usage",
                                        "--no-sandbox",
                                        "--disable-setuid-sandbox",
                                        "--disable-web-security",
                                        "--disable-features=VizDisplayCompositor",
                                        "--disable-ipc-flooding-protection",
                                        "--disable-background-timer-throttling",
                                        "--disable-renderer-backgrounding",
                                        "--no-first-run",
                                        "--no-default-browser-check",
                                        "--disable-default-apps",
                                        "--disable-backgrounding-occluded-windows",
                                        "--disable-extensions",
                                        "--disable-plugins",
                                        "--no-sandbox",
                                        "--disable-gpu",
                                        "--disable-dev-shm-usage",
                                        "--disable-ipc-flooding-protection"
                                    ]
                                )
                                context = browser.new_context(
                                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                                )
                                # Reload session in new context
                                load_session(context, 'binance_session.json')
                            
                            # Create a new page for each capture
                            page = context.new_page()
                            
                            # Navigate to the target URL
                            page.goto(url, timeout=60000)
                            
                            # Wait for page to load with extended timeout
                            page.wait_for_load_state("load", timeout=60000)
                            
                            # Instead of waiting for networkidle, wait for a fixed time to allow resources to load
                            # Binance pages often have ongoing network activity that prevents reaching networkidle state
                            page.wait_for_timeout(10000)
                            
                            # Wait for specific elements that indicate the page is ready
                            try:
                                # Wait for chart or trading interface elements to be loaded
                                page.wait_for_selector('[data-testid="chart-container"], .tradingview-chart, .chart-wrapper, .chart-container, .tv-chart-container', timeout=30000)
                            except:
                                # If specific selectors are not found, continue with the screenshot
                                print("Specific chart elements not found, proceeding with screenshot")
                            
                            # Additional wait for dynamic content to visually render
                            page.wait_for_timeout(5000)
                            
                            # Create timestamped filename with date and currency subdirectories
                            current_time = datetime.now()
                            timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')
                            if capture_times_per_currency > 1:
                                filename = f'{timestamp_str}_{currency}_trade_{i+1}.png'
                            else:
                                filename = f'{timestamp_str}_{currency}_trade.png'
                            
                            # Create path with date and currency subdirectories
                            currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
                            os.makedirs(currency_dir, exist_ok=True)
                            
                            filepath = os.path.join(currency_dir, filename)
                            
                            # Ensure screenshots directory exists
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            
                            # Capture full page screenshot with extended timeout
                            page.screenshot(path=filepath, full_page=True, timeout=120000)
                            
                            print(f"Screenshot {i+1} for {currency} saved to {filepath}")
                            file_paths.append(filepath)
                            
                            # Success, break out of retry loop
                            break
                            
                        except Exception as e:
                            retry_count += 1
                            print(f"Error capturing screenshot for {currency} (attempt {i+1}, retry {retry_count}): {str(e)}")
                            
                            if retry_count < max_retries:
                                print(f"Retrying in 5 seconds...")
                                time.sleep(5)
                            else:
                                print(f"Failed to capture screenshot for {currency} after {max_retries} attempts")
                                continue  # Continue with next currency instead of failing completely
                        finally:
                            # Close the page after capturing (only if page exists and not already closed)
                            if page and not page.is_closed():
                                try:
                                    page.close()
                                except Exception as e:
                                    print(f"Error closing page for {currency}: {str(e)}")
                                    pass  # Page might already be closed
                            # Explicitly delete the page reference to ensure it's cleaned up
                            page = None
            
            # Save session when done - ensuring browser context is still available
            try:
                if context and browser and browser.is_connected():
                    save_session(context, 'binance_session.json')
            except Exception as e:
                print(f"Error saving session: {str(e)}")
                # Continue even if session saving fails
            
            # Close the browser after all screenshots
            if browser:
                browser.close()
            
            return file_paths
            
        except Exception as e:
            print(f"Error launching new browser: {str(e)}")
            # If there was an exception outside the inner loop, make sure to close the browser if it was opened
            if browser:
                try:
                    browser.close()
                except:
                    pass
            # Return what we have so far (might be empty)
            return file_paths


def capture_specific_tab_screenshot(currency, tab_index=0):
    """
    Capture screenshot of a specific tab in an existing browser window.
    
    Args:
        currency (str): Currency pair to capture (e.g., BTCUSDT)
        tab_index (int): Index of the tab to capture (0-based)
    
    Returns:
        str: Path to the saved screenshot file
    """
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp_str}_{currency}_trade.png'
    filepath = os.path.join('data', 'screenshots', date_dir, filename)
    
    # Ensure screenshots directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with sync_playwright() as p:
        # Connect to an existing Chrome instance
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the context
            if browser.contexts:
                context = browser.contexts[0]
            else:
                print("No browser contexts found")
                return None
            
            # Get the specific page/tab
            pages = context.pages
            if tab_index >= len(pages):
                print(f"Tab index {tab_index} is out of range. Available tabs: {len(pages)}")
                return None
            
            page = pages[tab_index]
            
            # Navigate to the target URL
            url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
            page.goto(url, timeout=60000)
            
            # Wait for page to load with extended timeout
            page.wait_for_load_state("load", timeout=60000)
            
            # Additional wait for JavaScript and dynamic content to render
            page.wait_for_timeout(20000)
            
            # Wait for key UI elements to ensure page is ready
            selectors_to_wait = [
                '[data-testid="chart-container"]', 
                '.tradingview-chart', 
                '.chart-wrapper', 
                '.chart-container', 
                '.tv-chart-container',
                '.futures-chart',
                '.price-container',
                '.trade-panel',
                '.order-form',
                '.position-info',
                '.price-data',
                '.market-price',
                '.chart-price'
            ]
            
            element_found = False
            for selector in selectors_to_wait:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    element_found = True
                    print(f"Found element: {selector}")
                    break
                except:
                    continue
            
            if not element_found:
                print("No specific chart elements found, proceeding with screenshot after additional wait")
                # Wait a bit more if no specific elements are found
                page.wait_for_timeout(10000)
            
            # Additional wait for dynamic content to visually render
            page.wait_for_timeout(5000)
            
            # Capture only the visible viewport to avoid timeout issues with complex pages
            # Full page screenshots can fail on trading interfaces with infinite scroll
            page.screenshot(path=filepath, full_page=False, timeout=60000)
            
            print(f"Screenshot saved to {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"Error capturing screenshot from specific tab: {str(e)}")
            print("Make sure Chrome is running with remote debugging enabled:")
            print("For example: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            raise


def capture_all_tabs_screenshot():
    """
    Capture screenshot of all tabs in the existing browser window.
    Each tab will be captured and saved as a separate screenshot in a folder named after the currency pair.
    
    Returns:
        list: List of file paths to saved screenshots
    """
    timestamp = datetime.now()
    date_dir = timestamp.strftime('%Y-%m-%d')
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    
    file_paths = []
    
    with sync_playwright() as p:
        # Connect to an existing Chrome instance
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the context
            if browser.contexts:
                context = browser.contexts[0]
            else:
                print("No browser contexts found")
                return file_paths  # Return empty list instead of None
            
            # Get all pages/tabs
            pages = context.pages
            print(f"Found {len(pages)} tabs, capturing screenshot for each...")
            
            # Ensure all pages are loaded before starting
            for page_idx, page in enumerate(pages):
                try:
                    page.wait_for_load_state("load", timeout=10000)
                    print(f"Page {page_idx+1} loaded, URL: {page.url}")
                except Exception as e:
                    print(f"Page {page_idx+1} load timeout or error: {str(e)}")
                    print(f"Page {page_idx+1} URL: {page.url}")
                    pass
            
            for i, page in enumerate(pages):
                # Get the URL of the current page to determine the currency
                currency = "UNKNOWN"
                try:
                    page_url = page.url
                    print(f"Processing tab {i+1}, URL: {page_url}")
                    
                    # Extract currency pair from URL - this might need adjustment based on actual URL format
                    if "binance" in page_url.lower():
                        # Try to extract currency pair from URL
                        import re
                        matches = re.findall(r'([A-Z]+USDT)', page_url)
                        print(f"Found URL matches: {matches}")
                        if matches:
                            currency = matches[0]
                            print(f"Identified currency from URL: {currency}")
                        else:
                            # If no currency found in URL, try to extract from page title or other sources
                            try:
                                # Wait a bit for the page to fully load
                                page.wait_for_load_state("load", timeout=10000)
                                # Try to get currency from the page content
                                title_element = page.query_selector('.symbol-text, [data-symbol], .tradingview-symbol')
                                if title_element:
                                    currency_text = title_element.text_content().strip()
                                    print(f"Found currency text in page: {currency_text}")
                                    
                                    # Ensure currency is in proper format
                                    currency_match = re.search(r'([A-Z]+USDT)', currency_text)
                                    if currency_match:
                                        currency = currency_match.group(1)
                                        print(f"Identified currency from page content: {currency}")
                                    else:
                                        currency = "UNKNOWN"
                                else:
                                    print(f"No currency element found in page content for tab {i+1}")
                                    currency = "UNKNOWN"
                            except Exception as e:
                                print(f"Error extracting currency from page content for tab {i+1}: {str(e)}")
                                currency = "UNKNOWN"
                    else:
                        # If not a binance page, use a generic tab identifier
                        print(f"Non-binance page detected for tab {i+1}, using generic identifier")
                        currency = f"TAB_{i+1}"
                except Exception as e:
                    print(f"Error determining currency for tab {i+1}: {str(e)}")
                    currency = f"TAB_{i+1}"
                
                print(f"Final currency for tab {i+1}: {currency}")
                
                # Create directory path with currency folder
                currency_dir = os.path.join('data', 'screenshots', date_dir, currency)
                os.makedirs(currency_dir, exist_ok=True)
                
                # Create filename with tab index
                filename = f'{timestamp_str}_tab_{i+1}_{currency}_trade.png'
                filepath = os.path.join(currency_dir, filename)
                
                # Wait for page to be ready - use a more flexible approach
                try:
                    # Wait for key UI elements to ensure page is ready
                    page.wait_for_load_state("load", timeout=15000)
                    
                    # Wait for chart container to be visible with shorter timeout
                    try:
                        page.wait_for_selector('[data-testid="chart-container"], .tradingview-chart, .chart-wrapper, .chart-container, .tv-chart-container', 
                                             state='visible', timeout=15000)
                    except:
                        # If chart container not found, continue anyway
                        print(f"Chart container not found for tab {i+1}, continuing...")
                    
                    # Wait for trading panel to be visible with shorter timeout
                    try:
                        page.wait_for_selector('.trade-panel, .order-form, .position-info', 
                                             state='visible', timeout=10000)
                    except:
                        # If trading panel not found, continue anyway
                        print(f"Trading panel not found for tab {i+1}, continuing...")
                    
                    # Wait for market data to be visible with shorter timeout
                    try:
                        page.wait_for_selector('.price-data, .market-price, .chart-price', 
                                             state='visible', timeout=8000)
                    except:
                        # If market data not found, continue anyway
                        print(f"Market data not found for tab {i+1}, continuing...")
                        
                except Exception as e:
                    print(f"Warning: Some UI elements not fully loaded for tab {i+1}: {str(e)}")
                    print("Proceeding with screenshot as basic elements are present")
                
                # Capture screenshot of the current tab
                try:
                    # Make sure we're on the right page before taking screenshot
                    page.bring_to_front()
                    page.screenshot(path=filepath, full_page=False, timeout=60000)
                    print(f"Screenshot for tab {i+1} ({currency}) saved to {filepath}")
                    file_paths.append(filepath)
                except Exception as e:
                    print(f"Error capturing screenshot for tab {i+1} ({currency}): {str(e)}")
                    # Continue with next tab instead of failing completely
                    continue
            
            print(f"Successfully captured {len(file_paths)} screenshots from {len(pages)} tabs")
            print(f"Captured files: {file_paths}")
            return file_paths
            
        except Exception as e:
            print(f"Error connecting to browser: {str(e)}")
            print("Make sure Chrome is running with remote debugging enabled:")
            print("For example: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            raise
