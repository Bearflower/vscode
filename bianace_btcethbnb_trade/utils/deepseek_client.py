import requests
import json
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL
import base64
import os
import time
from typing import Optional


def encode_image_to_base64(image_path):
    """
    Encode image to base64 string
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Base64 encoded image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def send_to_deepseek(screenshot_path, document_content, prompt=None, max_retries=3):
    """
    Send screenshot and document content to DeepSeek API with retry mechanism
    
    Args:
        screenshot_path (str): Path to the screenshot image
        document_content (str): Content of the trade rules document
        prompt (str): Custom prompt to send with the request
        max_retries (int): Maximum number of retries for failed requests
    
    Returns:
        dict: Response from DeepSeek API
    """
    if not prompt:
        prompt = "Based on the trading rules document and the Binance futures contract screenshot, please analyze and provide insights."
    
    # Check if we're in test mode (no API key)
    if DEEPSEEK_API_KEY == "your_api_key_here" or not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.strip() == "":
        # Return mock response for testing
        return {
            "choices": [{
                "message": {
                    "content": f"[Mock Response] Analysis of the Binance futures contract with the provided trading rules would go here. In actual implementation, this would be processed by DeepSeek AI.\n\nDocument Content Preview:\n{document_content[:500]}..."
                }
            }]
        }
    
    # For DeepSeek, we'll send only the text content since it doesn't support image inputs
    # We'll describe the image content instead
    image_description = f"Screenshot of Binance futures contract page saved at: {screenshot_path}"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n{image_description}\n\nTrading Rules Document:\n{document_content}"
            }
        ],
        "max_tokens": 2048
    }
    
    # Retry mechanism
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{DEEPSEEK_API_BASE}/chat/completions", headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit hit, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            elif response.status_code == 401:  # Unauthorized
                raise Exception("Invalid API key")
            elif response.status_code == 402:  # Insufficient balance
                raise Exception("Insufficient balance")
            elif response.status_code == 404:  # Not found
                raise Exception("Model not found")
            else:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Error: {error_msg}, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Network error: {str(e)}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Network error after {max_retries} attempts: {str(e)}")
    
    # This should never be reached due to the retry logic
    raise Exception("Unexpected error")


def send_multiple_screenshots_to_deepseek(screenshot_paths, document_content, currency, prompt=None, max_retries=3):
    """
    Send multiple screenshots and document content to DeepSeek API with retry mechanism
    
    Args:
        screenshot_paths (list): List of paths to the screenshot images
        document_content (str): Content of the trade rules document
        currency (str): Currency pair being analyzed
        prompt (str): Custom prompt to send with the request
        max_retries (int): Maximum number of retries for failed requests
    
    Returns:
        dict: Response from DeepSeek API
    """
    if not prompt:
        prompt = f"Based on the trading rules document and multiple Binance futures contract screenshots for {currency}, please analyze and provide comprehensive insights."
    
    # Check if we're in test mode (no API key)
    if DEEPSEEK_API_KEY == "your_api_key_here" or not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.strip() == "":
        # Return mock response for testing
        return {
            "choices": [{
                "message": {
                    "content": f"[Mock Response] Comprehensive analysis of {len(screenshot_paths)} Binance futures contract screenshots for {currency} with the provided trading rules would go here. In actual implementation, this would be processed by DeepSeek AI.\n\nDocument Content Preview:\n{document_content[:500]}...\n\nScreenshots processed: {screenshot_paths}"
                }
            }]
        }
    
    # Prepare both image encodings and text descriptions for future multi-modal support
    encoded_images = []
    screenshots_description = f"Multiple screenshots of Binance futures contract pages for {currency}:\n"
    
    for i, path in enumerate(screenshot_paths, 1):
        try:
            # Encode image to base64
            encoded_image = encode_image_to_base64(path)
            encoded_images.append({
                'index': i,
                'path': path,
                'encoded': encoded_image,
                'mime_type': 'image/png'  # Assuming PNG format, adjust as needed
            })
            screenshots_description += f"  - Screenshot {i}: {path}\n"
        except Exception as e:
            print(f"Warning: Could not encode image {path}: {str(e)}")
            screenshots_description += f"  - Screenshot {i}: {path} [Could not encode]\n"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build message content - currently using text description since DeepSeek doesn't support image inputs
    # But we're structuring it to be ready for multi-modal support in the future
    content_text = f"{prompt}\n\n{screenshots_description}\n\nTrading Rules Document:\n{document_content}"
    
    # Note: When DeepSeek adds image support, we can modify this to include base64-encoded images
    # Example format for future use:
    # content = [
    #     {"type": "text", "text": prompt},
    #     * [{"type": "image_url", "image_url": {"url": f"data:{img['mime_type']};base64,{img['encoded']}"} for img in encoded_images],
    #     {"type": "text", "text": f"Trading Rules Document:\n{document_content}"}
    # ]
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "user",
                "content": content_text
            }
        ],
        "max_tokens": 4096  # Increase tokens for multiple screenshots analysis
    }
    
    # Retry mechanism
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{DEEPSEEK_API_BASE}/chat/completions", headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit hit, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            elif response.status_code == 401:  # Unauthorized
                raise Exception("Invalid API key")
            elif response.status_code == 402:  # Insufficient balance
                raise Exception("Insufficient balance")
            elif response.status_code == 404:  # Not found
                raise Exception("Model not found")
            else:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Error: {error_msg}, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Network error: {str(e)}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Network error after {max_retries} attempts: {str(e)}")
    
    # This should never be reached due to the retry logic
    raise Exception("Unexpected error")


def save_response(response, output_path):
    """
    Save DeepSeek response to a text file
    
    Args:
        response (dict): Response from DeepSeek API
        output_path (str): Path to save the response
    
    Returns:
        str: Path to the saved file
    """
    # Extract text content from response
    content = response['choices'][0]['message']['content']
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write content to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path