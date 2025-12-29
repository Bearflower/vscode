#!/usr/bin/env python3
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


def manual_setup(currency='BTCUSDT'):
    """
    Open browser for manual configuration and save session when closed.
    
    Args:
        currency (str): Currency pair to configure (e.g., BTCUSDT)
    """
    # Get the URL for the specific currency
    url = BINANCE_CONTRACT_URLS.get(currency, BINANCE_CONTRACT_URLS['BTCUSDT'])
    
    print(f"Opening browser for manual configuration of {currency}...")
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
            print(f"Error during manual setup: {str(e)}")
        finally:
            browser.close()


if __name__ == "__main__":
    import sys
    currency = sys.argv[1] if len(sys.argv) > 1 else 'BTCUSDT'
    manual_setup(currency)