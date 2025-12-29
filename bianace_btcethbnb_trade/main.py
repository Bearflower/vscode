import os
import sys
from datetime import datetime
from utils.screenshot import capture_screenshot, connect_to_existing_chrome_and_screenshot, capture_all_tabs_screenshot
from utils.document_reader import read_document
from utils.deepseek_client import send_to_deepseek, send_multiple_screenshots_to_deepseek, save_response
from utils.lark_notifier import notify_completion, notify_error
from config.settings import REPORT_OUTPUT_DIR, SCREENSHOT_OUTPUT_DIR, SUPPORTED_CURRENCIES
import logging
from logging.handlers import RotatingFileHandler
import argparse


# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Create logger
    logger = logging.getLogger("binance_trade_analyzer")
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def analyze_currency(currency, prompt=None, use_existing_chrome=True):  # 默认使用现有Chrome
    """
    Analyze a single currency pair
    
    Args:
        currency (str): Currency pair to analyze
        prompt (str): Custom prompt for DeepSeek API
        use_existing_chrome (bool): Whether to use existing Chrome instance with remote debugging
    """
    logger = setup_logging()
    
    try:
        logger.info(f"Starting analysis for {currency}")
        
        # Step 1: Capture screenshot
        logger.info("Capturing screenshot...")
        if use_existing_chrome:
            screenshot_path = connect_to_existing_chrome_and_screenshot(currency)
        else:
            screenshot_path = capture_screenshot(currency)
        logger.info(f"Screenshot saved to {screenshot_path}")
        
        # Step 2: Read document
        logger.info("Reading trade rules document...")
        document_content = read_document()
        logger.info("Document read successfully")
        
        # Step 3: Send to DeepSeek API
        logger.info("Sending data to DeepSeek API...")
        response = send_to_deepseek(screenshot_path, document_content, prompt)
        logger.info("Response received from DeepSeek API")
        
        # Step 4: Save response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response_filename = f'{timestamp}_{currency}_trade.txt'
        response_path = os.path.join(REPORT_OUTPUT_DIR, response_filename)
        
        saved_path = save_response(response, response_path)
        logger.info(f"Response saved to {saved_path}")
        
        # Step 5: Send notification
        logger.info("Sending completion notification...")
        notify_completion(currency, response_path, screenshot_path)
        logger.info("Notification sent successfully")
        
        logger.info(f"Analysis completed successfully for {currency}")
        
    except Exception as e:
        logger.error(f"Error during analysis for {currency}: {str(e)}", exc_info=True)
        # Send error notification
        notify_error(currency, str(e))
        raise


def analyze_currency_multiple_screenshots(currency, date_dir=None, prompt=None, use_existing_chrome=True):
    """
    Analyze a single currency pair using multiple screenshots for the day
    
    Args:
        currency (str): Currency pair to analyze
        date_dir (str): Date directory to look for screenshots (default: today)
        prompt (str): Custom prompt for DeepSeek API
        use_existing_chrome (bool): Whether to use existing Chrome instance with remote debugging
    """
    logger = setup_logging()
    
    if date_dir is None:
        date_dir = datetime.now().strftime('%Y-%m-%d')
    
    try:
        logger.info(f"Starting analysis for {currency} with multiple screenshots")
        
        # Step 1: Find all screenshots for this currency on this date
        currency_screenshot_dir = os.path.join(SCREENSHOT_OUTPUT_DIR, date_dir, currency)
        if not os.path.exists(currency_screenshot_dir):
            logger.warning(f"No screenshots found for {currency} in {currency_screenshot_dir}")
            return
        
        screenshot_files = [f for f in os.listdir(currency_screenshot_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not screenshot_files:
            logger.warning(f"No screenshot files found for {currency} in {currency_screenshot_dir}")
            return
        
        screenshot_paths = [os.path.join(currency_screenshot_dir, f) for f in screenshot_files]
        logger.info(f"Found {len(screenshot_paths)} screenshots for {currency}")
        
        # Step 2: Read document
        logger.info("Reading trade rules document...")
        document_content = read_document()
        logger.info("Document read successfully")
        
        # Step 3: Send all screenshots to DeepSeek API
        logger.info("Sending multiple screenshots and document to DeepSeek API...")
        response = send_multiple_screenshots_to_deepseek(screenshot_paths, document_content, currency, prompt)
        logger.info("Response received from DeepSeek API")
        
        # Step 4: Save response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response_filename = f'{timestamp}_{currency}_multi_analysis.txt'
        response_path = os.path.join(REPORT_OUTPUT_DIR, response_filename)
        
        saved_path = save_response(response, response_path)
        logger.info(f"Response saved to {saved_path}")
        
        # Step 5: Send notification
        logger.info("Sending completion notification...")
        # Using the first screenshot for notification as an example
        notify_completion(currency, response_path, screenshot_paths[0])
        logger.info("Notification sent successfully")
        
        logger.info(f"Multi-screenshot analysis completed successfully for {currency}")
        
    except Exception as e:
        logger.error(f"Error during multi-screenshot analysis for {currency}: {str(e)}", exc_info=True)
        # Send error notification
        notify_error(currency, str(e))
        raise


def analyze_screenshots_from_path(screenshot_paths, prompt=None, currency="CUSTOM"):
    """
    Analyze screenshots from specified paths
    
    Args:
        screenshot_paths (list or str): Path or list of paths to screenshot images
        prompt (str): Custom prompt for DeepSeek API
        currency (str): Currency pair identifier for the analysis
    """
    logger = setup_logging()
    
    # Ensure screenshot_paths is a list
    if isinstance(screenshot_paths, str):
        screenshot_paths = [screenshot_paths]
    
    try:
        logger.info(f"Starting analysis for {currency} using {len(screenshot_paths)} screenshots from specified paths")
        
        # Step 1: Validate screenshot paths exist
        for path in screenshot_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Screenshot file does not exist: {path}")
        
        logger.info(f"Validated {len(screenshot_paths)} screenshot files")
        
        # Step 2: Read document
        logger.info("Reading trade rules document...")
        document_content = read_document()
        logger.info("Document read successfully")
        
        # Step 3: Send all screenshots to DeepSeek API
        logger.info("Sending screenshots and document to DeepSeek API...")
        response = send_multiple_screenshots_to_deepseek(screenshot_paths, document_content, currency, prompt)
        logger.info("Response received from DeepSeek API")
        
        # Step 4: Save response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response_filename = f'{timestamp}_{currency}_path_analysis.txt'
        response_path = os.path.join(REPORT_OUTPUT_DIR, response_filename)
        
        saved_path = save_response(response, response_path)
        logger.info(f"Response saved to {saved_path}")
        
        # Step 5: Send notification
        logger.info("Sending completion notification...")
        # Using the first screenshot for notification as an example
        notify_completion(currency, response_path, screenshot_paths[0])
        logger.info("Notification sent successfully")
        
        logger.info(f"Path-based analysis completed successfully for {currency}")
        
    except Exception as e:
        logger.error(f"Error during path-based analysis for {currency}: {str(e)}", exc_info=True)
        # Send error notification
        notify_error(currency, str(e))
        raise


def main(currencies=None, prompt=None, use_existing_chrome=True):  # 默认使用现有Chrome
    """
    Main function to orchestrate the analysis workflow
    
    Args:
        currencies (list): List of currency pairs to analyze
        prompt (str): Custom prompt for DeepSeek API
        use_existing_chrome (bool): Whether to use existing Chrome instance with remote debugging
    """
    if not currencies:
        # If no currencies specified, use default list
        currencies = SUPPORTED_CURRENCIES
    
    logger = setup_logging()
    
    for currency in currencies:
        try:
            logger.info(f"Processing {currency}...")
            analyze_currency(currency, prompt, use_existing_chrome)
        except Exception as e:
            logger.error(f"Failed to process {currency}: {str(e)}")
            continue


def main_multiple_screenshots(currencies=None, prompt=None, use_existing_chrome=True, date_dir=None):
    """
    Main function to orchestrate the analysis workflow using multiple screenshots per currency
    
    Args:
        currencies (list): List of currency pairs to analyze
        prompt (str): Custom prompt for DeepSeek API
        use_existing_chrome (bool): Whether to use existing Chrome instance with remote debugging
        date_dir (str): Date directory to look for screenshots (default: today)
    """
    if not currencies:
        # If no currencies specified, use default list
        currencies = SUPPORTED_CURRENCIES
    
    logger = setup_logging()
    
    for currency in currencies:
        try:
            logger.info(f"Processing {currency} with multiple screenshots...")
            analyze_currency_multiple_screenshots(currency, date_dir, prompt, use_existing_chrome)
        except Exception as e:
            logger.error(f"Failed to process {currency} with multiple screenshots: {str(e)}")
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binance Trade Analyzer")
    parser.add_argument(
        "--currencies", 
        nargs='+', 
        default=["BTCUSDT"], 
        help="List of currency pairs to analyze (default: BTCUSDT)"
    )
    parser.add_argument(
        "--prompt",
        help="Custom prompt for DeepSeek API"
    )
    parser.add_argument(
        "--use-existing-chrome",
        action="store_true",
        default=True,  # 默认使用现有Chrome
        help="Use existing Chrome instance with remote debugging instead of launching new browser"
    )
    parser.add_argument(
        "--new-browser",
        action="store_false",
        dest="use_existing_chrome",
        help="Launch new browser instance instead of using existing Chrome"
    )
    parser.add_argument(
        "--multi-analysis",
        action="store_true",
        help="Use multiple screenshots for analysis instead of single screenshot"
    )
    parser.add_argument(
        "--date",
        help="Date directory to look for screenshots (format: YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--screenshot-paths",
        nargs='+',
        help="List of specific screenshot file paths to analyze (bypasses automatic screenshot capture)"
    )
    parser.add_argument(
        "--currency-name",
        default="CUSTOM",
        help="Currency name to use when analyzing specific screenshot paths (default: CUSTOM)"
    )
    
    args = parser.parse_args()
    
    if args.screenshot_paths:
        # Analyze specific screenshot paths
        analyze_screenshots_from_path(args.screenshot_paths, args.prompt, args.currency_name)
    elif args.multi_analysis:
        main_multiple_screenshots(args.currencies, args.prompt, args.use_existing_chrome, args.date)
    else:
        main(args.currencies, args.prompt, args.use_existing_chrome)
