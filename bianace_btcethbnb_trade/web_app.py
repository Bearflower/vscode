from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from datetime import datetime
import json

app = Flask(__name__)

# Configuration
REPORT_DIR = "./reports"
SCREENSHOT_DIR = "./data/screenshots"
LOG_DIR = "./logs"

@app.route('/')
def index():
    """
    Main page with list of reports and screenshots
    """
    # Get all report files
    report_files = []
    if os.path.exists(REPORT_DIR):
        for filename in os.listdir(REPORT_DIR):
            if filename.endswith('.txt'):
                report_files.append({
                    'filename': filename,
                    'path': os.path.join(REPORT_DIR, filename),
                    'date': datetime.fromtimestamp(os.path.getmtime(os.path.join(REPORT_DIR, filename)))
                })
        
        # Sort by date (newest first)
        report_files.sort(key=lambda x: x['date'], reverse=True)
    
    # Get all screenshot files
    screenshot_files = []
    if os.path.exists(SCREENSHOT_DIR):
        for filename in os.listdir(SCREENSHOT_DIR):
            if filename.endswith('.png'):
                screenshot_files.append({
                    'filename': filename,
                    'path': os.path.join(SCREENSHOT_DIR, filename),
                    'date': datetime.fromtimestamp(os.path.getmtime(os.path.join(SCREENSHOT_DIR, filename)))
                })
        
        # Sort by date (newest first)
        screenshot_files.sort(key=lambda x: x['date'], reverse=True)
    
    # Get log files
    log_files = []
    if os.path.exists(LOG_DIR):
        for filename in os.listdir(LOG_DIR):
            if filename.endswith('.log'):
                log_files.append({
                    'filename': filename,
                    'path': os.path.join(LOG_DIR, filename),
                    'date': datetime.fromtimestamp(os.path.getmtime(os.path.join(LOG_DIR, filename)))
                })
        
        # Sort by date (newest first)
        log_files.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('index.html', 
                         reports=report_files, 
                         screenshots=screenshot_files, 
                         logs=log_files)

@app.route('/report/<filename>')
def view_report(filename):
    """
    View a specific report file
    """
    filepath = os.path.join(REPORT_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return render_template('report.html', 
                         filename=filename, 
                         content=content)

@app.route('/screenshot/<filename>')
def view_screenshot(filename):
    """
    View a specific screenshot
    """
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    
    return send_from_directory(SCREENSHOT_DIR, filename)

@app.route('/log/<filename>')
def view_log(filename):
    """
    View a specific log file
    """
    filepath = os.path.join(LOG_DIR, filename)
    if not os.path.exists(filepath):
        return "File not found", 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return render_template('log.html', 
                         filename=filename, 
                         content=content)

@app.route('/api/reports')
def api_reports():
    """
    API endpoint to get list of reports
    """
    report_files = []
    if os.path.exists(REPORT_DIR):
        for filename in os.listdir(REPORT_DIR):
            if filename.endswith('.txt'):
                report_files.append({
                    'filename': filename,
                    'date': datetime.fromtimestamp(os.path.getmtime(os.path.join(REPORT_DIR, filename))).isoformat()
                })
        
        # Sort by date (newest first)
        report_files.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify(report_files)

@app.route('/api/screenshot/<filename>')
def api_screenshot(filename):
    """
    API endpoint to get a screenshot
    """
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(SCREENSHOT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)