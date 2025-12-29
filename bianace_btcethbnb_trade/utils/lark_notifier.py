import requests
import json
import os
from config.settings import LOG_DIR


class LarkNotifier:
    """
    飞书通知类，用于向飞书群聊发送消息
    """
    
    def __init__(self, webhook_url=None):
        """
        初始化飞书通知器
        
        Args:
            webhook_url (str): 飞书机器人的webhook URL
        """
        self.webhook_url = webhook_url or os.getenv('LARK_WEBHOOK_URL')
        
    def send_text_message(self, content):
        """
        发送文本消息到飞书
        
        Args:
            content (str): 消息内容
            
        Returns:
            dict: API响应结果
        """
        if not self.webhook_url:
            print("警告: 未配置飞书webhook URL，跳过消息发送")
            return {"status": "skipped", "reason": "webhook_url not configured"}
            
        headers = {'Content-Type': 'application/json'}
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        try:
            response = requests.post(self.webhook_url, headers=headers, data=json.dumps(payload))
            return response.json()
        except Exception as e:
            error_msg = f"发送飞书消息失败: {str(e)}"
            print(error_msg)
            return {"status": "error", "message": error_msg}
    
    def send_success_notification(self, currency, report_path, screenshot_path):
        """
        发送任务成功完成的通知
        
        Args:
            currency (str): 交易对
            report_path (str): 报告文件路径
            screenshot_path (str): 截图文件路径
        """
        message = f"""
✅ 币安期货分析任务已完成

交易对: {currency}
执行时间: {self._get_current_time()}
报告文件: {report_path}
截图文件: {screenshot_path}

请查看分析结果并采取相应行动。
        """
        return self.send_text_message(message)
    
    def send_error_notification(self, currency, error_message):
        """
        发送任务错误通知
        
        Args:
            currency (str): 交易对
            error_message (str): 错误信息
        """
        message = f"""
❌ 币安期货分析任务执行失败

交易对: {currency}
执行时间: {self._get_current_time()}
错误信息: {error_message}

请检查系统状态和日志文件。
        """
        return self.send_text_message(message)
    
    def _get_current_time(self):
        """
        获取当前时间字符串
        
        Returns:
            str: 格式化的时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def notify_completion(currency, report_path, screenshot_path):
    """
    通知任务完成的便捷函数
    
    Args:
        currency (str): 交易对
        report_path (str): 报告文件路径
        screenshot_path (str): 截图文件路径
    """
    notifier = LarkNotifier()
    return notifier.send_success_notification(currency, report_path, screenshot_path)


def notify_error(currency, error_message):
    """
    通知任务错误的便捷函数
    
    Args:
        currency (str): 交易对
        error_message (str): 错误信息
    """
    notifier = LarkNotifier()
    return notifier.send_error_notification(currency, error_message)