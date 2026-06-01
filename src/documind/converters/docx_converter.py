"""
DOCX converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    HAS_DOCX_DEPS = True
except ImportError:
    HAS_DOCX_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class DocxConverter(BaseConverter):
    """Converter for Word documents."""
    
    supported_input_formats = [DocumentFormat.DOCX, DocumentFormat.DOC]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
        DocumentFormat.HTML,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DOCX converter."""
        super().__init__(config)
        
        if not HAS_DOCX_DEPS:
            self.logger.warning("DOCX dependencies not installed. Install with: pip install 'documind-converter[docx]'")
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert DOCX to target format.
        
        Args:
            input_path: Path to DOCX file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_DOCX_DEPS:
            return self._handle_error(
                Exception("DOCX dependencies not installed. Install with: pip install 'documind-converter[docx]'"),
                start_time=start_time
            )
        
        try:
            # Get document info
            source_info = self.get_detailed_info(input_path)
            
            # Convert document
            content = self._convert_to_markdown(input_path, **options)
            
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
    
    def _convert_to_markdown(self, input_path: Path, **options) -> str:
        """Convert DOCX to Markdown.
        
        Args:
            input_path: Path to DOCX file.
            **options: Additional options.
            
        Returns:
            Markdown content.
        """
        doc = docx.Document(input_path)
        content_parts = []
        
        for element in doc.element.body:
            if element.tag.endswith('p'):  # Paragraph
                paragraph = Paragraph(element, doc)
                md_text = self._paragraph_to_markdown(paragraph)
                if md_text:
                    content_parts.append(md_text)
                    
            elif element.tag.endswith('tbl'):  # Table
                table = Table(element, doc)
                md_table = self._table_to_markdown(table)
                if md_table:
                    content_parts.append(md_table)
        
        return "\n\n".join(content_parts)
    
    def _paragraph_to_markdown(self, paragraph: Paragraph) -> str:
        """Convert paragraph to Markdown.
        
        Args:
            paragraph: DOCX paragraph.
            
        Returns:
            Markdown text.
        """
        text = paragraph.text.strip()
        if not text:
            return ""
        
        # Determine heading level from style
        style_name = paragraph.style.name.lower() if paragraph.style else ""
        
        if "heading 1" in style_name or style_name == "title":
            return f"# {text}"
        elif "heading 2" in style_name:
            return f"## {text}"
        elif "heading 3" in style_name:
            return f"### {text}"
        elif "heading 4" in style_name:
            return f"#### {text}"
        elif "heading 5" in style_name:
            return f"##### {text}"
        elif "heading 6" in style_name:
            return f"###### {text}"
        
        # Check for list items
        if paragraph._p.pPr is not None:
            numPr = paragraph._p.pPr.numPr
            if numPr is not None:
                # It's a list item
                return f"- {text}"
        
        # Regular paragraph
        # Handle bold and italic
        md_text = text
        for run in paragraph.runs:
            if run.bold and run.text:
                md_text = md_text.replace(run.text, f"**{run.text}**")
            if run.italic and run.text:
                md_text = md_text.replace(run.text, f"*{run.text}*")
        
        return md_text
    
    def _table_to_markdown(self, table: Table) -> str:
        """Convert table to Markdown.
        
        Args:
            table: DOCX table.
            
        Returns:
            Markdown table.
        """
        if not table.rows:
            return ""
        
        lines = []
        
        # Header row
        header_cells = [cell.text.strip() for cell in table.rows[0].cells]
        lines.append("| " + " | ".join(header_cells) + " |")
        lines.append("|" + "|".join([" --- " for _ in header_cells]) + "|")
        
        # Data rows
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            lines.append("| " + " | ".join(cells) + " |")
        
        return "\n".join(lines)
    
    def get_detailed_info(self, file_path: Path) -> DocumentInfo:
        """Get detailed DOCX information.
        
        Args:
            file_path: Path to DOCX file.
            
        Returns:
            DocumentInfo with DOCX details.
        """
        info = self.get_info(file_path)
        
        if not HAS_DOCX_DEPS:
            return info
        
        try:
            doc = docx.Document(file_path)
            
            # Extract metadata
            core_props = doc.core_properties
            info.title = core_props.title
            info.author = core_props.author
            info.subject = core_props.subject
            info.keywords = core_props.keywords.split(",") if core_props.keywords else []
            info.created_at = core_props.created
            info.modified_at = core_props.modified
            
            # Count paragraphs and words
            word_count = 0
            for para in doc.paragraphs:
                word_count += len(para.text.split())
            info.word_count = word_count
            
        except Exception as e:
            self.logger.warning("Failed to get detailed DOCX info", error=str(e))
        
        return info
