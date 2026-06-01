"""
Text converter for DocuMind Converter.
"""

import time
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger, clean_text

logger = get_logger(__name__)


class TextConverter(BaseConverter):
    """Converter for plain text and other simple formats."""
    
    supported_input_formats = [
        DocumentFormat.TXT,
        DocumentFormat.JSON,
        DocumentFormat.CSV,
        DocumentFormat.XML,
        DocumentFormat.MARKDOWN,
        DocumentFormat.MD,
    ]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
    ]
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert text file to target format.
        
        Args:
            input_path: Path to text file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        try:
            # Get document info
            source_info = self.get_info(input_path)
            
            # Read content
            content = input_path.read_text(encoding="utf-8", errors="ignore")
            
            # Convert based on input format
            input_format = source_info.format
            
            if input_format == DocumentFormat.JSON:
                content = self._format_json(content, **options)
            elif input_format == DocumentFormat.CSV:
                content = self._format_csv(content, **options)
            elif input_format == DocumentFormat.XML:
                content = self._format_xml(content, **options)
            elif input_format in (DocumentFormat.MARKDOWN, DocumentFormat.MD):
                # Markdown is already in target format
                pass
            else:
                # Plain text - clean it up
                content = clean_text(content)
            
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
    
    def _format_json(self, content: str, **options) -> str:
        """Format JSON content as Markdown.
        
        Args:
            content: JSON content.
            **options: Additional options.
            
        Returns:
            Formatted Markdown.
        """
        try:
            data = json.loads(content)
            
            # Pretty print JSON
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Wrap in code block
            return f"## JSON Document\n\n```json\n{formatted}\n```"
            
        except json.JSONDecodeError:
            # Not valid JSON, return as plain text
            return f"## Text Document\n\n```\n{content}\n```"
    
    def _format_csv(self, content: str, **options) -> str:
        """Format CSV content as Markdown table.
        
        Args:
            content: CSV content.
            **options: Additional options.
            
        Returns:
            Markdown table.
        """
        import csv
        import io
        
        try:
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            
            if not rows:
                return ""
            
            lines = []
            
            # Header row
            header = rows[0]
            lines.append("| " + " | ".join(header) + " |")
            lines.append("|" + "|".join([" --- " for _ in header]) + "|")
            
            # Data rows
            for row in rows[1:]:
                lines.append("| " + " | ".join(row) + " |")
            
            return "## CSV Document\n\n" + "\n".join(lines)
            
        except Exception:
            # Return as plain text if parsing fails
            return f"## Text Document\n\n```\n{content}\n```"
    
    def _format_xml(self, content: str, **options) -> str:
        """Format XML content as Markdown.
        
        Args:
            content: XML content.
            **options: Additional options.
            
        Returns:
            Formatted Markdown.
        """
        try:
            import xml.dom.minidom
            
            # Parse and pretty print XML
            dom = xml.dom.minidom.parseString(content)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            # Remove XML declaration and empty lines
            lines = pretty_xml.split('\n')
            lines = [line for line in lines if line.strip() and not line.strip().startswith('<?xml')]
            pretty_xml = '\n'.join(lines)
            
            return f"## XML Document\n\n```xml\n{pretty_xml}\n```"
            
        except Exception:
            # Return as plain text if parsing fails
            return f"## Text Document\n\n```\n{content}\n```"
