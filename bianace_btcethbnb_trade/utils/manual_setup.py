#!/usr/bin/env python3
"""
Manual browser configuration script.
Run this script to open a browser window where you can manually configure
the Binance page settings. When you close the browser, your session will
be saved automatically.
"""

import json
import os
from playwright.sync_api import sync_playwright
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
    print("When finished, close the browser window to save the session.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url)
            
            # Wait indefinitely until browser is closed
            import time
            while True:
                try:
                    # Check if page is still open by trying to access its URL
                    _ = page.url
                    time.sleep(1)
                except:
                    # Browser was closed, save session and exit
                    cookies = context.cookies()
                    with open('binance_session.json', 'w') as f:
                        json.dump(cookies, f)
                    print("Session saved to binance_session.json")
                    break
                    
        except Exception as e:
            print(f"Error during manual setup: {str(e)}")
        finally:
            try:
                browser.close()
            except:
                pass


if __name__ == "__main__":
    import sys
    currency = sys.argv[1] if len(sys.argv) > 1 else 'BTCUSDT'
    manual_setup(currency)