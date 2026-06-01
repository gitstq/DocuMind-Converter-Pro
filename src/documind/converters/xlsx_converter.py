"""
XLSX converter for DocuMind Converter.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
    HAS_XLSX_DEPS = True
except ImportError:
    HAS_XLSX_DEPS = False

from documind.converters.base import BaseConverter
from documind.models import ConversionResult, ConversionStatus, DocumentFormat, DocumentInfo
from documind.utils import get_logger

logger = get_logger(__name__)


class XlsxConverter(BaseConverter):
    """Converter for Excel spreadsheets."""
    
    supported_input_formats = [DocumentFormat.XLSX, DocumentFormat.XLS]
    supported_output_formats = [
        DocumentFormat.MARKDOWN,
        DocumentFormat.CSV,
        DocumentFormat.JSON,
        DocumentFormat.TXT,
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize XLSX converter."""
        super().__init__(config)
        
        if not HAS_XLSX_DEPS:
            self.logger.warning("XLSX dependencies not installed. Install with: pip install 'documind-converter[xlsx]'")
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: DocumentFormat = DocumentFormat.MARKDOWN,
        **options
    ) -> ConversionResult:
        """Convert XLSX to target format.
        
        Args:
            input_path: Path to XLSX file.
            output_path: Optional output path.
            output_format: Target output format.
            **options: Additional options.
            
        Returns:
            ConversionResult.
        """
        start_time = time.time()
        
        if not HAS_XLSX_DEPS:
            return self._handle_error(
                Exception("XLSX dependencies not installed. Install with: pip install 'documind-converter[xlsx]'"),
                start_time=start_time
            )
        
        try:
            # Get document info
            source_info = self.get_detailed_info(input_path)
            
            # Convert based on output format
            if output_format == DocumentFormat.CSV:
                content = self._convert_to_csv(input_path, **options)
            elif output_format == DocumentFormat.JSON:
                content = self._convert_to_json(input_path, **options)
            else:
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
        """Convert XLSX to Markdown.
        
        Args:
            input_path: Path to XLSX file.
            **options: Additional options.
            
        Returns:
            Markdown content.
        """
        wb = openpyxl.load_workbook(input_path, data_only=True)
        content_parts = []
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            content_parts.append(f"## Sheet: {sheet_name}\n")
            
            # Convert sheet to markdown table
            table_content = self._sheet_to_markdown_table(ws)
            if table_content:
                content_parts.append(table_content)
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _sheet_to_markdown_table(self, worksheet) -> str:
        """Convert worksheet to Markdown table.
        
        Args:
            worksheet: OpenPyXL worksheet.
            
        Returns:
            Markdown table.
        """
        rows = []
        max_col = 0
        
        # Collect all cell values
        for row in worksheet.iter_rows():
            row_data = []
            for cell in row:
                value = cell.value
                if value is not None:
                    # Convert to string and escape pipe characters
                    value = str(value).replace("|", "\\|")
                    row_data.append(value)
                    max_col = max(max_col, len(row_data))
                else:
                    row_data.append("")
            
            # Only add non-empty rows
            if any(cell for cell in row_data):
                # Pad row to max column count
                while len(row_data) < max_col:
                    row_data.append("")
                rows.append(row_data)
        
        if not rows:
            return ""
        
        # Build markdown table
        lines = []
        
        # Header row
        header = rows[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "|".join([" --- " for _ in header]) + "|")
        
        # Data rows
        for row in rows[1:]:
            lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(lines)
    
    def _convert_to_csv(self, input_path: Path, **options) -> str:
        """Convert XLSX to CSV (first sheet only).
        
        Args:
            input_path: Path to XLSX file.
            **options: Additional options.
            
        Returns:
            CSV content.
        """
        import csv
        import io
        
        wb = openpyxl.load_workbook(input_path, data_only=True)
        ws = wb.active
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        for row in ws.iter_rows():
            row_data = [cell.value if cell.value is not None else "" for cell in row]
            writer.writerow(row_data)
        
        return output.getvalue()
    
    def _convert_to_json(self, input_path: Path, **options) -> str:
        """Convert XLSX to JSON.
        
        Args:
            input_path: Path to XLSX file.
            **options: Additional options.
            
        Returns:
            JSON content.
        """
        import json
        
        wb = openpyxl.load_workbook(input_path, data_only=True)
        result = {}
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = []
            headers = []
            
            for idx, row in enumerate(ws.iter_rows()):
                row_data = [cell.value if cell.value is not None else "" for cell in row]
                
                if idx == 0:
                    headers = row_data
                else:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row_data):
                            row_dict[header] = row_data[i]
                        else:
                            row_dict[header] = ""
                    rows.append(row_dict)
            
            result[sheet_name] = rows
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def get_detailed_info(self, file_path: Path) -> DocumentInfo:
        """Get detailed XLSX information.
        
        Args:
            file_path: Path to XLSX file.
            
        Returns:
            DocumentInfo with XLSX details.
        """
        info = self.get_info(file_path)
        
        if not HAS_XLSX_DEPS:
            return info
        
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            
            # Extract metadata
            core_props = wb.properties
            info.title = core_props.title
            info.author = core_props.creator
            info.subject = core_props.subject
            info.keywords = core_props.keywords.split(",") if core_props.keywords else []
            info.created_at = core_props.created
            info.modified_at = core_props.modified
            
            # Count sheets
            info.page_count = len(wb.sheetnames)
            
            wb.close()
            
        except Exception as e:
            self.logger.warning("Failed to get detailed XLSX info", error=str(e))
        
        return info
