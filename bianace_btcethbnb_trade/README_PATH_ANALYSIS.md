# 指定截图路径分析功能

## 功能说明

新增功能允许用户指定截图文件路径，将这些截图和`trade_rule.docx`文档一起发送到DeepSeek API进行分析。

## 使用方法

### 1. 命令行使用

```bash
# 分析单个截图
python3 main.py --screenshot-paths /path/to/screenshot.png --prompt "你的自定义提示词"

# 分析多个截图
python3 main.py --screenshot-paths /path/to/screenshot1.png /path/to/screenshot2.png --prompt "你的自定义提示词" --currency-name "BTCUSDT_CUSTOM"

# 使用自定义货币对名称
python3 main.py --screenshot-paths /path/to/screenshot.png --prompt "你的自定义提示词" --currency-name "ETHUSDT_ANALYSIS"
```

### 2. 作为模块使用

```python
from main import analyze_screenshots_from_path

# 分析单个截图
analyze_screenshots_from_path(
    screenshot_paths="/path/to/screenshot.png",
    prompt="请分析这张图中的交易信号",
    currency="BTCUSDT"
)

# 分析多个截图
analyze_screenshots_from_path(
    screenshot_paths=[
        "/path/to/screenshot1.png",
        "/path/to/screenshot2.png",
        "/path/to/screenshot3.png"
    ],
    prompt="请分析这些图中的交易信号变化",
    currency="BTCUSDT_MULTI"
)
```

### 3. 运行示例脚本

```bash
python3 example_path_analysis.py
```

## 定时任务运行方式更新

现在，定时任务（scheduler.py）将在执行时启动新的浏览器实例，而不是依赖持续运行的Chrome调试实例。

### 运行定时任务

```bash
# 使用新浏览器实例（推荐）
python3 scheduler.py

# 或者仍然使用现有Chrome实例
python3 scheduler.py --use-existing-chrome
```

## 参数说明

- `--screenshot-paths`: 指定要分析的截图文件路径列表（必需，当使用此选项时）
- `--prompt`: 自定义提示词，用于指导DeepSeek API的分析（可选）
- `--currency-name`: 自定义货币对名称，用于报告命名和通知（可选，默认为"CUSTOM"）

## 注意事项

1. 确保指定的截图文件路径存在且可访问
2. 提示词越具体，分析结果越符合需求
3. 支持多种图片格式（PNG、JPG等）
4. 所有指定的截图将与`trade_rule.docx`文档一起发送到DeepSeek API进行综合分析
5. 分析结果将保存到`reports/`目录下，并通过飞书发送通知

## 应用场景

1. 分析历史截图数据
2. 分析特定事件的截图
3. 对比不同时间点的截图
4. 手动收集的截图分析