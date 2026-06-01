# 🧠 DocuMind Converter

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/version-1.0.0-orange.svg" alt="Version: 1.0.0">
</p>

<p align="center">
  <strong>🚀 Intelligent Document Converter & Analyzer</strong><br>
  Transform documents with AI-powered insights. Convert between multiple formats and extract meaningful information.
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## 🌐 Language / 语言

- [English](#english)
- [简体中文](#简体中文)
- [繁體中文](#繁體中文)

---

## English

### 🎉 Introduction

**DocuMind Converter** is a powerful, intelligent document conversion tool that goes beyond simple format conversion. Inspired by the popular [markitdown](https://github.com/microsoft/markitdown) project, DocuMind adds AI-powered analysis capabilities, batch processing, and a beautiful terminal interface.

#### ✨ Key Differentiators

- 🤖 **AI-Powered Analysis** - Extract insights, summaries, and key information
- 📦 **Multi-Format Support** - PDF, DOCX, PPTX, XLSX, HTML, Images, and more
- ⚡ **Batch Processing** - Convert multiple files in parallel
- 🎨 **Beautiful CLI** - Rich terminal interface with progress indicators
- 🔌 **Plugin System** - Extensible architecture for custom converters
- 📊 **Document Insights** - Metadata extraction and document statistics

### ✨ Features

#### Supported Formats

| Input Format | Output Formats | Features |
|-------------|----------------|----------|
| PDF | Markdown, TXT, HTML | OCR support for scanned documents |
| DOCX/DOC | Markdown, TXT, HTML | Preserves headings and tables |
| PPTX/PPT | Markdown, TXT | Slide structure extraction |
| XLSX/XLS | Markdown, CSV, JSON, TXT | Table conversion |
| HTML | Markdown, TXT | Clean extraction |
| Images | Markdown, TXT | OCR text extraction |
| TXT/JSON/XML | Markdown, TXT | Formatting and cleanup |

### 🚀 Quick Start

#### Installation

```bash
# Install from PyPI (when available)
pip install documind-converter

# Or install with all dependencies
pip install "documind-converter[all]"

# Install specific format support
pip install "documind-converter[pdf,docx]"
```

#### Basic Usage

```bash
# Convert a single file
documind convert document.pdf

# Convert to specific format
documind convert document.docx -f markdown

# Specify output path
documind convert document.pdf -o output.md

# Batch conversion
documind batch *.pdf -d ./output

# Get document info
documind info document.pdf
```

#### Python API

```python
from documind import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Convert a document
result = converter.convert("document.pdf", output_format="markdown")
print(result.content)

# Batch conversion
results = converter.convert_batch(
    ["file1.pdf", "file2.docx"],
    output_dir="./output"
)
```

### 📖 Usage Guide

#### Command-Line Interface

```bash
# Show help
documind --help

# Convert with options
documind convert document.pdf \
  --output output.md \
  --format markdown \
  --ocr-lang eng

# Batch with parallel processing
documind batch *.pdf \
  --output-dir ./converted \
  --jobs 4
```

#### Configuration

Create a `.env` file or set environment variables:

```bash
# AI Analysis (optional)
DOCUMIND_OPENAI_API_KEY=your-api-key
DOCUMIND_OPENAI_MODEL=gpt-4o-mini

# Default settings
DOCUMIND_OUTPUT_DIR=./output
DOCUMIND_LOG_LEVEL=INFO
```

### 💡 Design Philosophy

DocuMind Converter is built with these principles:

1. **Simplicity** - Easy to use with sensible defaults
2. **Extensibility** - Plugin architecture for custom needs
3. **Performance** - Parallel processing for batch operations
4. **Quality** - Preserve document structure and formatting
5. **AI-Ready** - Output optimized for LLM consumption

### 📦 Packaging & Deployment

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Build package
make build

# Upload to PyPI
make upload
```

### 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 简体中文

### 🎉 项目介绍

**DocuMind Converter** 是一款强大的智能文档转换工具，超越了简单的格式转换。受 [markitdown](https://github.com/microsoft/markitdown) 项目启发，DocuMind 增加了 AI 智能分析功能、批量处理和精美的终端界面。

#### ✨ 核心差异化亮点

- 🤖 **AI 智能分析** - 提取洞察、摘要和关键信息
- 📦 **多格式支持** - PDF、DOCX、PPTX、XLSX、HTML、图片等
- ⚡ **批量处理** - 并行转换多个文件
- 🎨 **精美 CLI** - 带有进度指示器的富终端界面
- 🔌 **插件系统** - 可扩展的自定义转换器架构
- 📊 **文档洞察** - 元数据提取和文档统计

### ✨ 核心特性

#### 支持格式

| 输入格式 | 输出格式 | 特性 |
|---------|---------|------|
| PDF | Markdown, TXT, HTML | 扫描文档 OCR 支持 |
| DOCX/DOC | Markdown, TXT, HTML | 保留标题和表格 |
| PPTX/PPT | Markdown, TXT | 幻灯片结构提取 |
| XLSX/XLS | Markdown, CSV, JSON, TXT | 表格转换 |
| HTML | Markdown, TXT | 干净提取 |
| 图片 | Markdown, TXT | OCR 文本提取 |
| TXT/JSON/XML | Markdown, TXT | 格式化和清理 |

### 🚀 快速开始

#### 安装

```bash
# 从 PyPI 安装（可用时）
pip install documind-converter

# 或安装所有依赖
pip install "documind-converter[all]"

# 安装特定格式支持
pip install "documind-converter[pdf,docx]"
```

#### 基本用法

```bash
# 转换单个文件
documind convert document.pdf

# 转换为特定格式
documind convert document.docx -f markdown

# 指定输出路径
documind convert document.pdf -o output.md

# 批量转换
documind batch *.pdf -d ./output

# 获取文档信息
documind info document.pdf
```

#### Python API

```python
from documind import DocumentConverter

# 初始化转换器
converter = DocumentConverter()

# 转换文档
result = converter.convert("document.pdf", output_format="markdown")
print(result.content)

# 批量转换
results = converter.convert_batch(
    ["file1.pdf", "file2.docx"],
    output_dir="./output"
)
```

### 📖 详细使用指南

#### 命令行界面

```bash
# 显示帮助
documind --help

# 带选项转换
documind convert document.pdf \
  --output output.md \
  --format markdown \
  --ocr-lang chi_sim

# 并行批量处理
documind batch *.pdf \
  --output-dir ./converted \
  --jobs 4
```

#### 配置

创建 `.env` 文件或设置环境变量：

```bash
# AI 分析（可选）
DOCUMIND_OPENAI_API_KEY=your-api-key
DOCUMIND_OPENAI_MODEL=gpt-4o-mini

# 默认设置
DOCUMIND_OUTPUT_DIR=./output
DOCUMIND_LOG_LEVEL=INFO
```

### 💡 设计理念

DocuMind Converter 遵循以下原则构建：

1. **简洁性** - 易于使用，合理默认设置
2. **可扩展性** - 插件架构满足自定义需求
3. **性能** - 批处理并行处理
4. **质量** - 保留文档结构和格式
5. **AI 就绪** - 针对 LLM 消费优化的输出

### 📦 打包与部署

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 构建包
make build

# 上传到 PyPI
make upload
```

### 🤝 贡献指南

我们欢迎贡献！请参阅我们的 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 运行测试和代码检查
5. 提交 Pull Request

### 📄 开源协议

本项目采用 MIT 协议 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

## 繁體中文

### 🎉 專案介紹

**DocuMind Converter** 是一款強大的智慧文件轉換工具，超越了簡單的格式轉換。受 [markitdown](https://github.com/microsoft/markitdown) 專案啟發，DocuMind 增加了 AI 智慧分析功能、批次處理和精美的終端機介面。

#### ✨ 核心差異化亮點

- 🤖 **AI 智慧分析** - 提取洞察、摘要和關鍵資訊
- 📦 **多格式支援** - PDF、DOCX、PPTX、XLSX、HTML、圖片等
- ⚡ **批次處理** - 平行轉換多個檔案
- 🎨 **精美 CLI** - 帶有進度指示器的豐富終端機介面
- 🔌 **外掛系統** - 可擴展的自訂轉換器架構
- 📊 **文件洞察** - 中繼資料提取和文件統計

### ✨ 核心特性

#### 支援格式

| 輸入格式 | 輸出格式 | 特性 |
|---------|---------|------|
| PDF | Markdown, TXT, HTML | 掃描文件 OCR 支援 |
| DOCX/DOC | Markdown, TXT, HTML | 保留標題和表格 |
| PPTX/PPT | Markdown, TXT | 幻燈片結構提取 |
| XLSX/XLS | Markdown, CSV, JSON, TXT | 表格轉換 |
| HTML | Markdown, TXT | 乾淨提取 |
| 圖片 | Markdown, TXT | OCR 文字提取 |
| TXT/JSON/XML | Markdown, TXT | 格式化和清理 |

### 🚀 快速開始

#### 安裝

```bash
# 從 PyPI 安裝（可用時）
pip install documind-converter

# 或安裝所有依賴
pip install "documind-converter[all]"

# 安裝特定格式支援
pip install "documind-converter[pdf,docx]"
```

#### 基本用法

```bash
# 轉換單個檔案
documind convert document.pdf

# 轉換為特定格式
documind convert document.docx -f markdown

# 指定輸出路徑
documind convert document.pdf -o output.md

# 批次轉換
documind batch *.pdf -d ./output

# 獲取文件資訊
documind info document.pdf
```

#### Python API

```python
from documind import DocumentConverter

# 初始化轉換器
converter = DocumentConverter()

# 轉換文件
result = converter.convert("document.pdf", output_format="markdown")
print(result.content)

# 批次轉換
results = converter.convert_batch(
    ["file1.pdf", "file2.docx"],
    output_dir="./output"
)
```

### 📖 詳細使用指南

#### 命令列介面

```bash
# 顯示說明
documind --help

# 帶選項轉換
documind convert document.pdf \
  --output output.md \
  --format markdown \
  --ocr-lang chi_tra

# 平行批次處理
documind batch *.pdf \
  --output-dir ./converted \
  --jobs 4
```

#### 配置

建立 `.env` 檔案或設定環境變數：

```bash
# AI 分析（可選）
DOCUMIND_OPENAI_API_KEY=your-api-key
DOCUMIND_OPENAI_MODEL=gpt-4o-mini

# 預設設定
DOCUMIND_OUTPUT_DIR=./output
DOCUMIND_LOG_LEVEL=INFO
```

### 💡 設計理念

DocuMind Converter 遵循以下原則構建：

1. **簡潔性** - 易於使用，合理預設設定
2. **可擴展性** - 外掛架構滿足自訂需求
3. **效能** - 批次處理平行處理
4. **品質** - 保留文件結構和格式
5. **AI 就緒** - 針對 LLM 消費優化的輸出

### 📦 打包與部署

```bash
# 安裝開發依賴
make install-dev

# 執行測試
make test

# 構建包
make build

# 上傳到 PyPI
make upload
```

### 🤝 貢獻指南

我們歡迎貢獻！請參閱我們的 [貢獻指南](CONTRIBUTING.md) 了解詳情。

1. Fork 倉庫
2. 建立功能分支
3. 進行更改
4. 執行測試和程式碼檢查
5. 提交 Pull Request

### 📄 開源協議

本專案採用 MIT 協議 - 詳情請參閱 [LICENSE](LICENSE) 檔案。

---

## 🔗 Links

- **Homepage**: https://github.com/gitstq/DocuMind-Converter
- **Documentation**: https://github.com/gitstq/DocuMind-Converter#readme
- **Issue Tracker**: https://github.com/gitstq/DocuMind-Converter/issues
- **Changelog**: https://github.com/gitstq/DocuMind-Converter/blob/main/CHANGELOG.md

---

<p align="center">
  Made with ❤️ by the DocuMind Team
</p>
