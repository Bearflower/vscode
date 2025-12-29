#!/usr/bin/env python3
"""
示例脚本：使用指定路径的截图进行分析

此脚本演示如何使用指定路径的截图文件和trade_rule.docx文档
通过DeepSeek API进行分析。
"""

import os
import sys
from datetime import datetime
from main import analyze_screenshots_from_path


def main():
    """
    示例：使用指定路径的截图进行分析
    """
    print("币安期货截图分析示例")
    print("="*50)
    
    # 示例1：分析单个截图
    print("\n示例1: 分析单个截图")
    screenshot_path = "./data/screenshots/2025-01-01/BTCUSDT/20250101_100000_BTCUSDT_trade.png"  # 替换为实际路径
    
    if os.path.exists(screenshot_path):
        custom_prompt = "请根据交易规则文档和提供的截图，分析当前BTC/USDT合约的市场情况、技术指标和可能的交易机会。"
        
        try:
            analyze_screenshots_from_path(
                screenshot_paths=screenshot_path,  # 单个路径
                prompt=custom_prompt,
                currency="BTCUSDT"
            )
            print("单个截图分析完成")
        except Exception as e:
            print(f"分析失败: {e}")
    else:
        print(f"截图文件不存在: {screenshot_path}")
        print("请确保截图文件存在或修改路径后重试")
    
    # 示例2：分析多个截图
    print("\n示例2: 分析多个截图")
    screenshot_paths = [
        "./data/screenshots/2025-01-01/BTCUSDT/20250101_100000_BTCUSDT_trade.png",  # 替换为实际路径
        "./data/screenshots/2025-01-01/BTCUSDT/20250101_110000_BTCUSDT_trade.png",  # 替换为实际路径
        "./data/screenshots/2025-01-01/BTCUSDT/20250101_120000_BTCUSDT_trade.png"   # 替换为实际路径
    ]
    
    # 检查所有路径是否存在
    existing_paths = [path for path in screenshot_paths if os.path.exists(path)]
    
    if existing_paths:
        custom_prompt = """请根据交易规则文档和提供的多张截图，分析BTC/USDT合约在不同时间点的变化趋势、技术指标变化以及潜在的交易机会。
        
        请特别关注:
        1. 价格变化趋势
        2. 技术指标的变化
        3. 交易量的变化
        4. 根据交易规则判断可能的交易信号
        5. 综合分析并给出交易建议"""
        
        try:
            analyze_screenshots_from_path(
                screenshot_paths=existing_paths,  # 多个路径
                prompt=custom_prompt,
                currency="BTCUSDT_MULTI"
            )
            print("多个截图分析完成")
        except Exception as e:
            print(f"分析失败: {e}")
    else:
        print("没有找到存在的截图文件，请确保截图文件存在或修改路径后重试")
    
    print("\n提示:")
    print("- 使用 --screenshot-paths 参数可以从命令行直接指定截图路径进行分析")
    print("- 使用 --prompt 参数可以指定自定义提示词")
    print("- 使用 --currency-name 参数可以指定货币对名称")


if __name__ == "__main__":
    main()