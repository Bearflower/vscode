# Binance Futures Trade Analyzer

Automated tool to capture Binance futures contract screenshots, analyze them with DeepSeek AI, and save the results.

## Features

- Automatically captures screenshots of Binance futures contract pages
- Reads trading rules from a local DOCX document
- Sends both to DeepSeek AI for analysis
- Saves the results in organized folders
- Runs on a daily schedule
- Sends notifications via Lark (Feishu) when tasks complete or fail

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```
   playwright install chromium
   ```

3. Configure environment variables in `.env`:
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key
   - `LARK_WEBHOOK_URL`: (Optional) Lark webhook URL for notifications
   - Other settings as needed

## Usage

### Manual run:
```
python main.py [--currencies CURRENCY_PAIRS] [--prompt CUSTOM_PROMPT] [--use-existing-chrome] [--new-browser]
```

Example:
```
python main.py --currencies BTCUSDT --use-existing-chrome
```

### Scheduled run:
```
python scheduler.py [--use-existing-chrome] [--new-browser]
```

This will start the scheduler which will automatically run the analysis daily at the configured time.

## Project Structure

- `main.py`: Main entry point
- `scheduler.py`: Scheduling functionality
- `config/settings.py`: Configuration loading
- `utils/screenshot.py`: Screenshot functionality
- `utils/document_reader.py`: Document reading functionality
- `utils/deepseek_client.py`: DeepSeek API client
- `utils/lark_notifier.py`: Lark notification functionality
- `.env`: Environment variables
- `requirements.txt`: Python dependencies

## Output

- Screenshots are saved in `data/screenshots/YYYY-MM-DD/` (subdirectories by date)
- Analysis results are saved in `reports/`
- Logs are saved in `logs/`

## Lark Notifications

To enable Lark notifications:

1. Create a group chat in Lark
2. Add a bot to the group chat
3. Get the webhook URL for the bot
4. Add the URL to your `.env` file as `LARK_WEBHOOK_URL`

Notifications will be sent when:
- The scheduler starts
- A task completes successfully
- A task fails with an error

## Browser Configuration

To use your existing Chrome browser for screenshots:

1. Close all Chrome windows
2. Open Terminal and run this command:
   ```
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug
   ```
3. When Chrome opens, log in to Binance and set your preferences
4. Then run the screenshot function as usual

Note: Using a separate user-data-dir prevents conflicts with your normal Chrome usage.

## Advanced Screenshot Features

### Multiple Currencies and Repeated Captures

You can capture screenshots for multiple currencies at once:

```python
from utils.screenshot import capture_multiple_screenshots

# Capture BTCUSDT, ETHUSDT and BNBUSDT once each
currencies = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
capture_multiple_screenshots(currencies)

# Capture BTCUSDT 3 times and ETHUSDT 2 times
currencies = ['BTCUSDT', 'ETHUSDT']
capture_multiple_screenshots(['BTCUSDT'] * 3 + ['ETHUSDT'] * 2)
```

This feature requires Chrome to be running with remote debugging enabled.

### Organized File Storage

All screenshots are now stored in date-based subdirectories:
- Path format: `data/screenshots/YYYY-MM-DD/filename.png`
- Each day's screenshots are grouped in their own subdirectory
- Files are named with timestamps to prevent conflicts

## Complete Run Methods

### 1. Start Chrome with Remote Debugging
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug
```

### 2. Run Manual Analysis with Existing Chrome (Default)
```bash
cd /Users/yl/vscode/bianace_btcethbnb_trade
python3 main.py --currencies BTCUSDT ETHUSDT BNBUSDT
```

### 3. Run Scheduled Analysis with Existing Chrome (Default)
```bash
python3 scheduler.py
```

### 4. Run with New Browser Instance (Optional)
```bash
python3 main.py --currencies BTCUSDT --new-browser
python3 scheduler.py --new-browser
```

The default behavior now uses your existing Chrome instance for better consistency with your configured settings.