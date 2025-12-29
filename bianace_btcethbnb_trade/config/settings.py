import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your_api_key_here')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')

# Binance Configuration - Default URLs
BINANCE_CONTRACT_URLS = {
    'BTCUSDT': 'https://www.binance.com/en/futures/BTCUSDT',
    'ETHUSDT': 'https://www.binance.com/en/futures/ETHUSDT',
    'BNBUSDT': 'https://www.binance.com/en/futures/BNBUSDT'
}

# Scheduling Configuration
SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '08:30')
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')

# Analysis Prompt Template
ANALYSIS_PROMPT_TEMPLATE = os.getenv('ANALYSIS_PROMPT_TEMPLATE', """请根据交易规则文档和提供的{currency}期货合约截图，进行以下分析：

1. 技术指标分析：分析当前技术指标（如RSI、MACD、移动平均线等）的状态
2. 价格趋势：评估当前价格趋势和可能的支撑/阻力位
3. 交易信号：根据截图中的数据和交易规则，识别潜在的买入/卖出信号
4. 风险评估：基于当前市场情况评估潜在风险
5. 交易建议：提供具体的交易建议（如开仓、平仓、止损位置等）

请提供详细的专业分析，并结合交易规则文档中的策略。""")

# File Paths
TRADE_RULE_DOCX_PATH = os.getenv('TRADE_RULE_DOCX_PATH', './trade_rule.docx')
SCREENSHOT_OUTPUT_DIR = os.getenv('SCREENSHOT_OUTPUT_DIR', './data/screenshots')
REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', './reports')
LOG_DIR = os.getenv('LOG_DIR', './logs')

# Lark Notification
LARK_WEBHOOK_URL = os.getenv('LARK_WEBHOOK_URL', '')

# Supported currencies
SUPPORTED_CURRENCIES = os.getenv('SUPPORTED_CURRENCIES', 'BTCUSDT,ETHUSDT,BNBUSDT').split(',')
