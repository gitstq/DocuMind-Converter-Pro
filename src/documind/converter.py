"""
Main document converter for DocuMind Converter.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from documind.config import config
from documind.converters import (
    BaseConverter,
    PDFConverter,
    DocxConverter,
    PptxConverter,
    XlsxConverter,
    HTMLConverter,
    ImageConverter,
    TextConverter,
)
from documind.models import (
    BatchConversionResult,
    ConversionResult,
    ConversionStatus,
    DocumentFormat,
    DocumentInfo,
)
from documind.utils import (
    detect_format,
    get_file_info,
    get_output_path,
    get_logger,
)

logger = get_logger(__name__)


class DocumentConverter:
    """Main document converter class."""
    
    def __init__(self, converter_config: Optional[Dict[str, Any]] = None):
        """Initialize document converter.
        
        Args:
            converter_config: Optional configuration dictionary.
        """
        self.config = converter_config or {}
        self.logger = logger.bind(component="DocumentConverter")
        
        # Initialize converters
        self._converters: Dict[DocumentFormat, BaseConverter] = {}
        self._register_default_converters()
    
    def _register_default_converters(self) -> None:
        """Register default converters."""
        converter_classes = [
            PDFConverter,
            DocxConverter,
            PptxConverter,
            XlsxConverter,
            HTMLConverter,
            ImageConverter,
            TextConverter,
        ]
        
        for converter_class in converter_classes:
            try:
                instance = converter_class(self.config)
                for fmt in converter_class.supported_input_formats:
                    if fmt not in self._converters:
                        self._converters[fmt] = instance
                        self.logger.debug(f"Registered converter for {fmt.value}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize {converter_class.__name__}", error=str(e))
    
    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        output_format: str = "markdown",
        **options
    ) -> ConversionResult:
        """Convert a document.
        
        Args:
            input_path: Path to input file.
            output_path: Optional path for output file.
            output_format: Target output format (default: markdown).
            **options: Additional conversion options.
            
        Returns:
            ConversionResult with conversion details.
        """
        input_path = Path(input_path).expanduser().resolve()
        
        if output_path:
            output_path = Path(output_path).expanduser().resolve()
        
        # Detect input format
        input_format = detect_format(input_path)
        if not input_format:
            return ConversionResult(
                status=ConversionStatus.FAILED,
                errors=[f"Unsupported file format: {input_path.suffix}"],
            )
        
        # Get target format
        target_format = self._get_format_from_string(output_format)
        if not target_format:
            return ConversionResult(
                status=ConversionStatus.FAILED,
                errors=[f"Unsupported output format: {output_format}"],
            )
        
        # Get appropriate converter
        converter = self._converters.get(input_format)
        if not converter:
            return ConversionResult(
                status=ConversionStatus.FAILED,
                errors=[f"No converter available for format: {input_format.value}"],
            )
        
        # Check if conversion is supported
        if not converter.can_convert(input_format, target_format):
            return ConversionResult(
                status=ConversionStatus.FAILED,
                errors=[f"Conversion from {input_format.value} to {target_format.value} is not supported"],
            )
        
        # Generate output path if not provided
        if not output_path:
            output_dir = options.get("output_dir") or config.output_dir
            output_path = get_output_path(
                input_path,
                output_dir=output_dir,
                output_format=output_format,
            )
        
        # Perform conversion
        self.logger.info(
            "Converting document",
            input=input_path,
            output=output_path,
            from_format=input_format.value,
            to_format=target_format.value,
        )
        
        result = converter.convert(
            input_path=input_path,
            output_path=output_path,
            output_format=target_format,
            **options
        )
        
        if result.success:
            self.logger.info(
                "Conversion successful",
                input=input_path,
                output=output_path,
                processing_time_ms=result.processing_time_ms,
            )
        else:
            self.logger.error(
                "Conversion failed",
                input=input_path,
                errors=result.errors,
            )
        
        return result
    
    def convert_batch(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        output_format: str = "markdown",
        max_workers: Optional[int] = None,
        **options
    ) -> BatchConversionResult:
        """Convert multiple documents in batch.
        
        Args:
            input_paths: List of input file paths.
            output_dir: Optional output directory.
            output_format: Target output format.
            max_workers: Maximum number of parallel workers.
            **options: Additional conversion options.
            
        Returns:
            BatchConversionResult with all conversion results.
        """
        start_time = time.time()
        
        if max_workers is None:
            max_workers = config.max_workers
        
        if output_dir:
            output_dir = Path(output_dir).expanduser().resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
        
        batch_result = BatchConversionResult(
            total_files=len(input_paths),
        )
        
        self.logger.info(
            "Starting batch conversion",
            total_files=len(input_paths),
            max_workers=max_workers,
        )
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(
                    self.convert,
                    input_path,
                    output_dir=output_dir,
                    output_format=output_format,
                    **options
                ): input_path
                for input_path in input_paths
            }
            
            for future in as_completed(future_to_path):
                input_path = future_to_path[future]
                try:
                    result = future.result()
                    batch_result.results.append(result)
                    
                    if result.status == ConversionStatus.SUCCESS:
                        batch_result.successful += 1
                    elif result.status == ConversionStatus.PARTIAL:
                        batch_result.partial += 1
                    else:
                        batch_result.failed += 1
                        
                except Exception as e:
                    batch_result.failed += 1
                    batch_result.errors.append(f"{input_path}: {str(e)}")
                    self.logger.error("Batch conversion error", input=input_path, error=str(e))
        
        batch_result.total_processing_time_ms = (time.time() - start_time) * 1000
        
        self.logger.info(
            "Batch conversion completed",
            total=batch_result.total_files,
            successful=batch_result.successful,
            failed=batch_result.failed,
            success_rate=f"{batch_result.success_rate:.1f}%",
        )
        
        return batch_result
    
    def get_info(self, input_path: Union[str, Path]) -> DocumentInfo:
        """Get document information.
        
        Args:
            input_path: Path to document.
            
        Returns:
            DocumentInfo with document details.
        """
        input_path = Path(input_path).expanduser().resolve()
        return get_file_info(input_path)
    
    def _get_format_from_string(self, format_str: str) -> Optional[DocumentFormat]:
        """Get DocumentFormat from string.
        
        Args:
            format_str: Format string.
            
        Returns:
            DocumentFormat or None.
        """
        format_str = format_str.lower().strip('.')
        
        for fmt in DocumentFormat:
            if fmt.value == format_str:
                return fmt
        
        # Aliases
        aliases = {
            "markdown": DocumentFormat.MARKDOWN,
            "md": DocumentFormat.MARKDOWN,
            "word": DocumentFormat.DOCX,
            "excel": DocumentFormat.XLSX,
            "powerpoint": DocumentFormat.PPTX,
            "image": DocumentFormat.IMAGE,
        }
        
        return aliases.get(format_str)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported formats.
        
        Returns:
            Dictionary with input and output formats.
        """
        input_formats = set()
        output_formats = set()
        
        for converter in set(self._converters.values()):
            for fmt in converter.supported_input_formats:
                input_formats.add(fmt.value)
            for fmt in converter.supported_output_formats:
                output_formats.add(fmt.value)
        
        return {
            "input": sorted(input_formats),
            "output": sorted(output_formats),
        }
