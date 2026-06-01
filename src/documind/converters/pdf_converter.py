"""
PDF converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import fitz  # PyMuPDF
    from pdf2image import convert_from_path
    import pytesseract
    HAS_PDF_DEPS = True
except ImportError:
    HAS_PDF_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class PDFConverter(BaseConverter):
    """Converter for PDF documents."""
    
    supported_input_formats = [DocumentFormat.PDF]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
        DocumentFormat.HTML,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PDF converter."""
        super().__init__(config)
        
        if not HAS_PDF_DEPS:
            self.logger.warning("PDF dependencies not installed. Install with: pip install 'documind-converter[pdf]'")
        
        self.ocr_enabled = config.get("ocr_enabled", True) if config else True
        self.ocr_language = config.get("ocr_language", "eng") if config else "eng"
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert PDF to target format.
        
        Args:
            input_path: Path to PDF file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_PDF_DEPS:
            return self._handle_error(
                Exception("PDF dependencies not installed. Install with: pip install 'documind-converter[pdf]'"),
                start_time=start_time
            )
        
        try:
            # Get document info
            source_info = self.get_info(input_path)
            
            # Extract text from PDF
            content = self._extract_text(input_path, **options)
            
            if not content.strip():
                # Try OCR if no text found
                content = self._extract_with_ocr(input_path, **options)
            
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
                metadata={"ocr_used": not content.strip()},
            )
            
        except Exception as e:
            return self._handle_error(e, source_info=self.get_info(input_path), start_time=start_time)
    
    def _extract_text(self, input_path: Path, **options) -> str:
        """Extract text from PDF using PyMuPDF.
        
        Args:
            input_path: Path to PDF file.
            **options: Additional options.
            
        Returns:
            Extracted text.
        """
        content_parts = []
        
        with fitz.open(input_path) as doc:
            for page_num, page in enumerate(doc, 1):
                # Extract text
                text = page.get_text()
                
                if text.strip():
                    content_parts.append(f"## Page {page_num}\n\n{text}\n")
                
                # Extract images if enabled
                if options.get("extract_images", False):
                    images = page.get_images()
                    if images:
                        content_parts.append(f"\n*[Images on page {page_num}: {len(images)}]*\n")
        
        return "\n".join(content_parts)
    
    def _extract_with_ocr(self, input_path: Path, **options) -> str:
        """Extract text using OCR for scanned PDFs.
        
        Args:
            input_path: Path to PDF file.
            **options: Additional options.
            
        Returns:
            Extracted text.
        """
        if not self.ocr_enabled:
            return ""
        
        try:
            content_parts = []
            images = convert_from_path(input_path)
            
            for page_num, image in enumerate(images, 1):
                text = pytesseract.image_to_string(image, lang=self.ocr_language)
                if text.strip():
                    content_parts.append(f"## Page {page_num}\n\n{text}\n")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            self.logger.warning("OCR extraction failed", error=str(e))
            return ""
    
    def get_detailed_info(self, file_path: Path) -> DocumentInfo:
        """Get detailed PDF information.
        
        Args:
            file_path: Path to PDF file.
            
        Returns:
            DocumentInfo with PDF details.
        """
        info = self.get_info(file_path)
        
        if not HAS_PDF_DEPS:
            return info
        
        try:
            with fitz.open(file_path) as doc:
                info.page_count = len(doc)
                
                # Extract metadata
                metadata = doc.metadata
                if metadata:
                    info.title = metadata.get("title")
                    info.author = metadata.get("author")
                    info.subject = metadata.get("subject")
                    info.keywords = metadata.get("keywords", "").split(",") if metadata.get("keywords") else []
                
                # Count words
                word_count = 0
                for page in doc:
                    word_count += len(page.get_text().split())
                info.word_count = word_count
                
        except Exception as e:
            self.logger.warning("Failed to get detailed PDF info", error=str(e))
        
        return info
