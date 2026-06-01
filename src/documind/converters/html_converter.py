"""
HTML converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from bs4 import BeautifulSoup
    import html2text
    HAS_HTML_DEPS = True
except ImportError:
    HAS_HTML_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class HTMLConverter(BaseConverter):
    """Converter for HTML documents."""
    
    supported_input_formats = [DocumentFormat.HTML]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize HTML converter."""
        super().__init__(config)
        
        if not HAS_HTML_DEPS:
            self.logger.warning("HTML dependencies not installed. Install with: pip install 'documind-converter[html]'")
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert HTML to target format.
        
        Args:
            input_path: Path to HTML file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_HTML_DEPS:
            return self._handle_error(
                Exception("HTML dependencies not installed. Install with: pip install 'documind-converter[html]'"),
                start_time=start_time
            )
        
        try:
            # Get document info
            source_info = self.get_info(input_path)
            
            # Read HTML content
            html_content = input_path.read_text(encoding="utf-8", errors="ignore")
            
            # Convert based on output format
            if output_format == DocumentFormat.TXT:
                content = self._html_to_text(html_content, **options)
            else:
                content = self._html_to_markdown(html_content, **options)
            
            # Write to file if output path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content, encoding="utf-8")
            
            processing_time = self._measure_time(start_time)
            
            return self._create_result(
                status=ConversionStatus.SUCCESS,
                content=content,
                output_path=output_path,
                source_info=source_info,
                target_format=output_format,
                processing_time_ms=processing_time,
            )
            
        except Exception as e:
            return self._handle_error(e, source_info=self.get_info(input_path), start_time=start_time)
    
    def _html_to_markdown(self, html_content: str, **options) -> str:
        """Convert HTML to Markdown.
        
        Args:
            html_content: HTML content.
            **options: Additional options.
            
        Returns:
            Markdown content.
        """
        # Configure html2text
        h = html2text.HTML2Text()
        h.ignore_links = options.get("ignore_links", False)
        h.ignore_images = options.get("ignore_images", True)
        h.ignore_tables = options.get("ignore_tables", False)
        h.body_width = 0  # Don't wrap lines
        
        # Convert
        markdown = h.handle(html_content)
        
        # Clean up
        lines = []
        prev_empty = False
        for line in markdown.split('\n'):
            stripped = line.strip()
            
            # Skip multiple consecutive empty lines
            if not stripped:
                if not prev_empty:
                    lines.append('')
                prev_empty = True
            else:
                lines.append(line)
                prev_empty = False
        
        return '\n'.join(lines).strip()
    
    def _html_to_text(self, html_content: str, **options) -> str:
        """Convert HTML to plain text.
        
        Args:
            html_content: HTML content.
            **options: Additional options.
            
        Returns:
            Plain text content.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_metadata(self, html_content: str) -> Dict[str, str]:
        """Extract metadata from HTML.
        
        Args:
            html_content: HTML content.
            
        Returns:
            Dictionary of metadata.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text()
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                metadata[name] = content
        
        return metadata
