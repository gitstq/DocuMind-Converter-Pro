"""
Image converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from PIL import Image
    import pytesseract
    HAS_IMAGE_DEPS = True
except ImportError:
    HAS_IMAGE_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class ImageConverter(BaseConverter):
    """Converter for image documents (OCR)."""
    
    supported_input_formats = [
        DocumentFormat.PNG,
        DocumentFormat.JPG,
        DocumentFormat.JPEG,
        DocumentFormat.TIFF,
        DocumentFormat.BMP,
        DocumentFormat.GIF,
        DocumentFormat.IMAGE,
    ]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.TXT,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize image converter."""
        super().__init__(config)
        
        if not HAS_IMAGE_DEPS:
            self.logger.warning("Image dependencies not installed. Install with: pip install 'documind-converter[image]'")
        
        self.ocr_language = config.get("ocr_language", "eng") if config else "eng"
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert image to text using OCR.
        
        Args:
            input_path: Path to image file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_IMAGE_DEPS:
            return self._handle_error(
                Exception("Image dependencies not installed. Install with: pip install 'documind-converter[image]'"),
                start_time=start_time
            )
        
        try:
            # Get document info
            source_info = self.get_detailed_info(input_path)
            
            # Extract text using OCR
            content = self._extract_text(input_path, **options)
            
            # Format output
            if output_format == DocumentFormat.MARKDOWN:
                content = f"## Image: {input_path.name}\n\n```\n{content}\n```"
            
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
    
    def _extract_text(self, input_path: Path, **options) -> str:
        """Extract text from image using OCR.
        
        Args:
            input_path: Path to image file.
            **options: Additional options.
            
        Returns:
            Extracted text.
        """
        # Open image
        image = Image.open(input_path)
        
        # Preprocess if needed
        if options.get("preprocess", False):
            image = self._preprocess_image(image)
        
        # Perform OCR
        lang = options.get("language", self.ocr_language)
        text = pytesseract.image_to_string(image, lang=lang)
        
        return text.strip()
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR.
        
        Args:
            image: PIL Image.
            
        Returns:
            Preprocessed image.
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def get_detailed_info(self, file_path: Path) -> DocumentInfo:
        """Get detailed image information.
        
        Args:
            file_path: Path to image file.
            
        Returns:
            DocumentInfo with image details.
        """
        info = self.get_info(file_path)
        
        if not HAS_IMAGE_DEPS:
            return info
        
        try:
            with Image.open(file_path) as img:
                info.metadata["width"] = img.width
                info.metadata["height"] = img.height
                info.metadata["mode"] = img.mode
                info.metadata["format"] = img.format
        except Exception as e:
            self.logger.warning("Failed to get detailed image info", error=str(e))
        
        return info
