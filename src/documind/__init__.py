"""
🧠 DocuMind Converter - Intelligent Document Converter & Analyzer

Transform documents with AI-powered insights. Convert between multiple formats
and extract meaningful information using advanced AI capabilities.

Example:
    >>> from documind import DocumentConverter
    >>> converter = DocumentConverter()
    >>> result = converter.convert("document.pdf", output_format="markdown")
    >>> print(result.content)
"""

__version__ = "1.0.0"
__author__ = "DocuMind Team"
__license__ = "MIT"

from documind.converter import DocumentConverter
from documind.config import Config, ConverterConfig
from documind.models import ConversionResult, DocumentInfo, AnalysisResult

__all__ = [
    "DocumentConverter",
    "Config",
    "ConverterConfig",
    "ConversionResult",
    "DocumentInfo",
    "AnalysisResult",
]
