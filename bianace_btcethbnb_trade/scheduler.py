from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime
from config.settings import SCHEDULE_TIME, TIMEZONE, SUPPORTED_CURRENCIES, LARK_WEBHOOK_URL
from utils.screenshot import capture_multiple_screenshots_new_browser, start_chrome_with_debugging_and_urls
from utils.document_reader import read_document
from utils.deepseek_client import send_multiple_screenshots_to_deepseek, save_response
from utils.lark_notifier import LarkNotifier
from config.settings import REPORT_OUTPUT_DIR, ANALYSIS_PROMPT_TEMPLATE
import os
import logging


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/scheduler.log')
    ]
)

logger = logging.getLogger('binance_scheduler')

# Initialize Lark notifier
lark_notifier = LarkNotifier(LARK_WEBHOOK_URL) if LARK_WEBHOOK_URL else None


def run_analysis(use_existing_chrome=False):  # 修改为默认不使用现有Chrome
    """
    Run the analysis by launching a new browser instance, navigating to URLs, capturing screenshots, and sending to DeepSeek
    """
    logger.info("Scheduled task started")
    try:
        logger.info("Capturing screenshots from multiple currency pages...")
        
        # If using existing chrome and it's not running, try to start it
        if use_existing_chrome:
            # Try to connect to existing Chrome instance, if fails, start a new one
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.connect_over_cdp("http://localhost:9222")
                    browser.close()
                    logger.info("Successfully connected to existing Chrome instance")
            except:
                logger.info("Existing Chrome instance not found, attempting to start Chrome with debugging...")
                from utils.screenshot import start_chrome_with_debugging_and_urls
                success = start_chrome_with_debugging_and_urls()
                if not success:
                    logger.error("Failed to start Chrome with debugging, falling back to new browser instance")
                    use_existing_chrome = False
                else:
                    logger.info("Chrome started with debugging, waiting 10 seconds for pages to load...")
                    import time
                    time.sleep(10)  # Wait for pages to load
        
        # Capture screenshots for all supported currencies
        if use_existing_chrome:
            # Use existing browser instance
            from utils.screenshot import capture_multiple_screenshots_existing_browser
            screenshot_paths = capture_multiple_screenshots_existing_browser(SUPPORTED_CURRENCIES)
        else:
            # Use new browser instance
            screenshot_paths = capture_multiple_screenshots_new_browser(SUPPORTED_CURRENCIES)
        
        if not screenshot_paths:
            logger.warning("No screenshots were captured")
            if lark_notifier:
                lark_notifier.send_text_message("⚠️ 警告：未捕获到任何截图")
            return
        
        logger.info(f"Captured {len(screenshot_paths)} screenshots: {screenshot_paths}")
        
        # Group screenshots by currency
        screenshots_by_currency = {}
        for path in screenshot_paths:
            # Extract currency from path (path format: data/screenshots/YYYY-MM-DD/CURRENCY/filename.png)
            path_parts = path.split(os.sep)
            currency_index = path_parts.index('screenshots') + 2  # The currency is after 'screenshots' and date
            if currency_index < len(path_parts):
                currency = path_parts[currency_index]
                if currency not in screenshots_by_currency:
                    screenshots_by_currency[currency] = []
                screenshots_by_currency[currency].append(path)
        
        logger.info(f"Grouped screenshots by currency: {screenshots_by_currency.keys()}")
        
        # Read document content once
        logger.info("Reading trade rules document...")
        document_content = read_document()
        logger.info("Document read successfully")
        
        # Collect all screenshots for all currencies
        all_screenshot_paths = []
        for currency, paths in screenshots_by_currency.items():
            all_screenshot_paths.extend(paths)
        
        if not all_screenshot_paths:
            logger.warning("No valid screenshots to process")
            if lark_notifier:
                lark_notifier.send_text_message("⚠️ 警告：没有有效的截图可处理")
            return
        
        logger.info(f"Sending all {len(all_screenshot_paths)} screenshots to DeepSeek API for comprehensive analysis...")
        
        try:
            # Get custom prompt from environment
            prompt = ANALYSIS_PROMPT_TEMPLATE
            
            # Send all screenshots and document to DeepSeek API for comprehensive analysis
            response = send_multiple_screenshots_to_deepseek(
                screenshot_paths=all_screenshot_paths, 
                document_content=document_content, 
                currency="COMPREHENSIVE", 
                prompt=prompt
            )
            logger.info("Comprehensive analysis response received from DeepSeek API")
            
            # Save response
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            response_filename = f'{timestamp}_comprehensive_analysis.txt'
            response_path = os.path.join(REPORT_OUTPUT_DIR, response_filename)
            
            saved_path = save_response(response, response_path)
            logger.info(f"Comprehensive analysis response saved to {saved_path}")
            
            # Send notification
            if lark_notifier:
                lark_notifier.send_text_message(f"✅ 综合分析任务已完成，报告已生成")
            
            logger.info("Comprehensive analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}", exc_info=True)
            # Send error notification
            if lark_notifier:
                lark_notifier.send_text_message(f"❌ 综合分析任务失败: {str(e)}")
        
        logger.info("Scheduled task completed successfully")
        
        # Send overall success notification
        if lark_notifier:
            lark_notifier.send_text_message(f"✅ 所有币种的币安期货综合分析任务已成功完成")
        
    except Exception as e:
        logger.error(f"Scheduled task failed: {str(e)}", exc_info=True)
        # Send error notification
        if lark_notifier:
            lark_notifier.send_text_message(f"❌ 币安期货分析任务失败: {str(e)}")


def start_scheduler(use_existing_chrome=False):  # 修改为默认不使用现有Chrome
    """
    Start the scheduler to run the analysis daily
    """
    scheduler = BlockingScheduler(timezone=pytz.timezone(TIMEZONE))
    
    # Parse schedule time
    # 处理全角冒号和半角冒号两种情况
    time_str = SCHEDULE_TIME.replace('：', ':')  # 将全角冒号替换为半角冒号
    hour, minute = map(int, time_str.split(':'))
    
    # Add job to scheduler
    scheduler.add_job(
        lambda: run_analysis(use_existing_chrome),
        CronTrigger(hour=hour, minute=minute, timezone=TIMEZONE),
        id='binance_analysis_job',
        name='Binance Contract Analysis',
        replace_existing=True
    )
    
    logger.info(f"Scheduler started. Next run scheduled for {SCHEDULE_TIME} ({TIMEZONE})")
    
    # Send startup notification
    if lark_notifier:
        lark_notifier.send_text_message(f"🚀 币安期货分析调度器已启动，下次执行时间: {SCHEDULE_TIME} ({TIMEZONE})")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        if lark_notifier:
            lark_notifier.send_text_message("⏹️ 币安期货分析调度器已被用户停止")
        scheduler.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Binance Trade Analyzer Scheduler")
    parser.add_argument(
        "--use-existing-chrome",
        action="store_true",
        default=False,  # 默认不使用现有Chrome
        help="Use existing Chrome instance with remote debugging instead of launching new browser"
    )
    parser.add_argument(
        "--new-browser",
        action="store_false",
        dest="use_existing_chrome",
        help="Launch new browser instance instead of using existing Chrome (default behavior)"
    )
    parser.add_argument(
        "--auto-start-chrome",
        action="store_true",
        default=False,
        help="Automatically start Chrome with debugging enabled and run analysis immediately"
    )
    
    args = parser.parse_args()
    
    # If auto-start-chrome is specified, start Chrome and then run analysis immediately
    if args.auto_start_chrome:
        from utils.screenshot import start_chrome_with_debugging_and_urls
        success = start_chrome_with_debugging_and_urls()
        if success:
            logger = logging.getLogger('binance_scheduler')
            logger.info("Chrome started with debugging, waiting 10 seconds before running analysis...")
            import time
            time.sleep(10)  # Wait for pages to load
            
            # Run analysis immediately instead of starting scheduler
            logger.info("Running analysis immediately...")
            run_analysis(use_existing_chrome=True)
        else:
            logger = logging.getLogger('binance_scheduler')
            logger.error("Failed to start Chrome with debugging, exiting...")
    else:
        start_scheduler(use_existing_chrome=args.use_existing_chrome)
