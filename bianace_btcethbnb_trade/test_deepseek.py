#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 测试脚本
用于测试将截图、交易规范和关键词提交到 DeepSeek 的功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.deepseek_client import send_multiple_screenshots_to_deepseek, encode_image_to_base64, save_response
from utils.document_reader import read_document
from config.settings import TRADE_RULE_DOCX_PATH, ANALYSIS_PROMPT_TEMPLATE, REPORT_OUTPUT_DIR
import glob
from datetime import datetime


def find_latest_screenshots(date_str=None):
    """
    查找最新的截图文件
    :param date_str: 日期字符串，格式为 'YYYY-MM-DD'，如果为 None，则使用今天的日期
    :return: 截图文件路径列表
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 构建搜索路径
    search_pattern = os.path.join("data", "screenshots", date_str, "*", "*")
    
    # 查找所有截图文件
    screenshot_paths = []
    for file_path in glob.glob(search_pattern):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            screenshot_paths.append(file_path)
    
    # 按修改时间排序，获取最新的
    screenshot_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 只取最新的几个截图
    return screenshot_paths[:4]  # 返回最新的4个截图


def test_deepseek_api():
    """
    测试 DeepSeek API 功能
    """
    print("开始测试 DeepSeek API 功能...")
    
    # 1. 读取交易规则文档
    print("\n1. 读取交易规则文档...")
    try:
        if os.path.exists(TRADE_RULE_DOCX_PATH):
            document_content = read_document(TRADE_RULE_DOCX_PATH)
            print(f"✓ 成功读取交易规则文档: {TRADE_RULE_DOCX_PATH}")
            print(f"文档长度: {len(document_content)} 字符")
        else:
            print(f"✗ 交易规则文档不存在: {TRADE_RULE_DOCX_PATH}")
            # 使用模拟内容
            document_content = "这是一个模拟的交易规则文档内容，用于测试目的。"
            print("使用模拟文档内容进行测试。")
    except Exception as e:
        print(f"✗ 读取交易规则文档失败: {e}")
        document_content = "这是一个模拟的交易规则文档内容，用于测试目的。"
        print("使用模拟文档内容进行测试。")
    
    # 2. 查找截图文件
    print("\n2. 查找截图文件...")
    try:
        # 尝试获取今天的截图
        today_date = datetime.now().strftime('%Y-%m-%d')
        screenshot_paths = find_latest_screenshots(today_date)
        
        # 如果今天没有截图，尝试前几天的
        days_back = 0
        while len(screenshot_paths) == 0 and days_back < 7:
            days_back += 1
            check_date = (datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
            screenshot_paths = find_latest_screenshots(check_date)
        
        if len(screenshot_paths) > 0:
            print(f"✓ 找到 {len(screenshot_paths)} 个截图文件:")
            for path in screenshot_paths:
                print(f"  - {path}")
        else:
            print("✗ 没有找到截图文件，将使用模拟路径进行测试")
            # 创建一个模拟的截图路径列表用于测试
            screenshot_paths = [
                "data/screenshots/2025-01-01/BTCUSDT/20250101_120000_BTCUSDT_15m_trade.png",
                "data/screenshots/2025-01-01/BTCUSDT/20250101_120000_BTCUSDT_1h_trade.png",
                "data/screenshots/2025-01-01/BTCUSDT/20250101_120000_BTCUSDT_4h_trade.png",
                "data/screenshots/2025-01-01/BTCUSDT/20250101_120000_BTCUSDT_1d_trade.png"
            ]
    except Exception as e:
        print(f"✗ 查找截图文件失败: {e}")
        screenshot_paths = []
    
    # 3. 测试 DeepSeek API 调用
    print("\n3. 调用 DeepSeek API...")
    try:
        # 使用环境变量中的提示词模板
        prompt = ANALYSIS_PROMPT_TEMPLATE
        print(f"使用的提示词模板长度: {len(prompt)} 字符")
        
        # 调用 DeepSeek API
        response = send_multiple_screenshots_to_deepseek(
            screenshot_paths=screenshot_paths,
            document_content=document_content,
            currency="COMPREHENSIVE_TEST",
            prompt=prompt
        )
        
        print("✓ DeepSeek API 调用成功!")
        
        # 输出响应内容的前 500 个字符
        content = response['choices'][0]['message']['content']
        print(f"\nAPI 响应内容预览 (前500字符):")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)
        
        # 4. 保存响应
        print("\n4. 保存响应...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response_filename = f'{timestamp}_test_deepseek_analysis.txt'
        response_path = os.path.join(REPORT_OUTPUT_DIR, response_filename)
        
        saved_path = save_response(response, response_path)
        print(f"✓ 响应已保存到: {saved_path}")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"✗ DeepSeek API 调用失败: {e}")
        import traceback
        traceback.print_exc()


def test_image_encoding():
    """
    测试图像编码功能
    """
    print("\n\n测试图像编码功能...")
    
    # 尝试编码一个截图
    today_date = datetime.now().strftime('%Y-%m-%d')
    search_pattern = os.path.join("data", "screenshots", today_date, "*", "*")
    
    screenshot_paths = []
    for file_path in glob.glob(search_pattern):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            screenshot_paths.append(file_path)
    
    if screenshot_paths:
        test_image = screenshot_paths[0]
        print(f"尝试编码图像: {test_image}")
        try:
            encoded = encode_image_to_base64(test_image)
            print(f"✓ 图像编码成功，编码长度: {len(encoded)} 字符")
        except Exception as e:
            print(f"✗ 图像编码失败: {e}")
    else:
        print("没有找到图像文件进行编码测试")


if __name__ == "__main__":
    print("DeepSeek API 测试工具")
    print("=" * 60)
    
    # 运行图像编码测试
    test_image_encoding()
    
    # 运行主要的 DeepSeek API 测试
    test_deepseek_api()
    
    print("\n如需使用真实的 DeepSeek API，请在 .env 文件中设置 DEEPSEEK_API_KEY")
    print("当前使用的是模拟模式，会返回模拟响应。")