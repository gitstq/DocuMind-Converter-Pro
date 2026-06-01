"""
PPTX converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    HAS_PPTX_DEPS = True
except ImportError:
    HAS_PPTX_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class PptxConverter(BaseConverter):
    """Converter for PowerPoint presentations."""
    
    supported_input_formats = [DocumentFormat.PPTX, DocumentFormat.PPT]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PPTX converter."""
        super().__init__(config)
        
        if not HAS_PPTX_DEPS:
            self.logger.warning("PPTX dependencies not installed. Install with: pip install 'documind-converter[pptx]'")
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert PPTX to target format.
        
        Args:
            input_path: Path to PPTX file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_PPTX_DEPS:
            return self._handle_error(
                Exception("PPTX dependencies not installed. Install with: pip install 'documind-converter[pptx]'"),
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
        """Convert PPTX to Markdown.
        
        Args:
            input_path: Path to PPTX file.
            **options: Additional options.
            
        Returns:
            Markdown content.
        """
        prs = Presentation(input_path)
        content_parts = []
        
        # Add presentation title if available
        if prs.core_properties.title:
            content_parts.append(f"# {prs.core_properties.title}\n")
        
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_content = self._extract_slide_content(slide, slide_num)
            if slide_content:
                content_parts.append(slide_content)
        
        return "\n\n".join(content_parts)
    
    def _extract_slide_content(self, slide, slide_num: int) -> str:
        """Extract content from a slide.
        
        Args:
            slide: PPTX slide object.
            slide_num: Slide number.
            
        Returns:
            Markdown content for the slide.
        """
        parts = [f"## Slide {slide_num}\n"]
        
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            
            for paragraph in shape.text_frame.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue
                
                # Determine if it's a title based on font size
                is_title = False
                for run in paragraph.runs:
                    if run.font.size and run.font.size >= Pt(24):
                        is_title = True
                        break
                
                if is_title:
                    parts.append(f"### {text}\n")
                else:
                    parts.append(text)
        
        # Add notes if present
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                parts.append(f"\n**Notes:** {notes}")
        
        return "\n".join(parts)
    
    def get_detailed_info(self, file_path: Path) -> DocumentInfo:
        """Get detailed PPTX information.
        
        Args:
            file_path: Path to PPTX file.
            
        Returns:
            DocumentInfo with PPTX details.
        """
        info = self.get_info(file_path)
        
        if not HAS_PPTX_DEPS:
            return info
        
        try:
            prs = Presentation(file_path)
            
            # Extract metadata
            core_props = prs.core_properties
            info.title = core_props.title
            info.author = core_props.author
            info.subject = core_props.subject
            info.keywords = core_props.keywords.split(",") if core_props.keywords else []
            info.created_at = core_props.created
            info.modified_at = core_props.modified
            
            # Count slides
            info.page_count = len(prs.slides)
            
        except Exception as e:
            self.logger.warning("Failed to get detailed PPTX info", error=str(e))
        
        return info
