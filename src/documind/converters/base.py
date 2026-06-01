"""
Base converter class for DocuMind Converter.
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from documind.models import (
    ConversionResult,
    ConversionStatus,
    DocumentFormat,
    DocumentInfo,
)
from documind.utils import get_file_info, get_logger

logger = get_logger(__name__)


class BaseConverter(ABC):
    """Base class for document converters."""
    
    # Override in subclasses
    supported_input_formats: List[DocumentFormat] = []
    supported_output_formats: List[DocumentFormat] = [DocumentFormat.MARKDOWN]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize converter.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.logger = logger.bind(converter=self.__class__.__name__)
    
    @abstractmethod
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        **options
    ) -> ConversionResult:
        """Convert a document.
        
        Args:
            input_path: Path to input file.
            output_path: Optional path for output file.
            **options: Additional conversion options.
            
        Returns:
            ConversionResult with conversion details.
        """
        pass
    
    def can_convert(self, input_format: DocumentFormat, output_format: DocumentFormat) -> bool:
        """Check if converter can handle the conversion.
        
        Args:
            input_format: Input document format.
            output_format: Desired output format.
            
        Returns:
            True if conversion is supported.
        """
        return (
            input_format in self.supported_input_formats
            and output_format in self.supported_output_formats
        )
    
    def get_info(self, file_path: Path) -> DocumentInfo:
        """Get document information.
        
        Args:
            file_path: Path to document.
            
        Returns:
            DocumentInfo with document details.
        """
        return get_file_info(file_path)
    
    def _create_result(
        self,
        status: ConversionStatus,
        content: str = "",
        output_path: Optional[Path] = None,
        source_info: Optional[DocumentInfo] = None,
        target_format: Optional[DocumentFormat] = None,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        processing_time_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversionResult:
        """Create a conversion result.
        
        Args:
            status: Conversion status.
            content: Converted content.
            output_path: Output file path.
            source_info: Source document info.
            target_format: Target format.
            errors: List of errors.
            warnings: List of warnings.
            processing_time_ms: Processing time in milliseconds.
            metadata: Additional metadata.
            
        Returns:
            ConversionResult.
        """
        return ConversionResult(
            status=status,
            content=content,
            output_path=output_path,
            source_info=source_info or DocumentInfo(),
            target_format=target_format,
            errors=errors or [],
            warnings=warnings or [],
            processing_time_ms=processing_time_ms,
            metadata=metadata or {},
        )
    
    def _handle_error(
        self,
        error: Exception,
        source_info: Optional[DocumentInfo] = None,
        start_time: Optional[float] = None,
    ) -> ConversionResult:
        """Handle conversion error.
        
        Args:
            error: Exception that occurred.
            source_info: Source document info.
            start_time: Start time for timing.
            
        Returns:
            ConversionResult with error details.
        """
        self.logger.error("Conversion failed", error=str(error))
        
        processing_time = 0.0
        if start_time:
            processing_time = (time.time() - start_time) * 1000
        
        return self._create_result(
            status=ConversionStatus.FAILED,
            source_info=source_info,
            errors=[str(error)],
            processing_time_ms=processing_time,
        )
    
    def _measure_time(self, start_time: float) -> float:
        """Calculate elapsed time in milliseconds.
        
        Args:
            start_time: Start time from time.time().
            
        Returns:
            Elapsed time in milliseconds.
        """
        return (time.time() - start_time) * 1000
