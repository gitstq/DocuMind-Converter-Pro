"""
File utility functions for DocuMind Converter.
"""

import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import magic

from documind.models import DocumentFormat, DocumentInfo


# Mapping of extensions to document formats
FORMAT_MAP = {
    ".pdf": DocumentFormat.PDF,
    ".docx": DocumentFormat.DOCX,
    ".doc": DocumentFormat.DOC,
    ".pptx": DocumentFormat.PPTX,
    ".ppt": DocumentFormat.PPT,
    ".xlsx": DocumentFormat.XLSX,
    ".xls": DocumentFormat.XLS,
    ".md": DocumentFormat.MARKDOWN,
    ".markdown": DocumentFormat.MARKDOWN,
    ".html": DocumentFormat.HTML,
    ".htm": DocumentFormat.HTML,
    ".txt": DocumentFormat.TXT,
    ".json": DocumentFormat.JSON,
    ".csv": DocumentFormat.CSV,
    ".xml": DocumentFormat.XML,
    ".png": DocumentFormat.PNG,
    ".jpg": DocumentFormat.JPG,
    ".jpeg": DocumentFormat.JPEG,
    ".tiff": DocumentFormat.TIFF,
    ".bmp": DocumentFormat.BMP,
    ".gif": DocumentFormat.GIF,
    ".epub": DocumentFormat.EPUB,
    ".rtf": DocumentFormat.RTF,
    ".odt": DocumentFormat.ODT,
    ".ods": DocumentFormat.ODS,
    ".odp": DocumentFormat.ODP,
}


def detect_format(file_path: Path) -> Optional[DocumentFormat]:
    """Detect document format from file path.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Detected document format or None if unknown.
    """
    # First try extension
    ext = file_path.suffix.lower()
    if ext in FORMAT_MAP:
        return FORMAT_MAP[ext]
    
    # Try mime type detection
    try:
        mime = magic.from_file(str(file_path), mime=True)
        mime_map = {
            "application/pdf": DocumentFormat.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentFormat.DOCX,
            "application/msword": DocumentFormat.DOC,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": DocumentFormat.PPTX,
            "application/vnd.ms-powerpoint": DocumentFormat.PPT,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": DocumentFormat.XLSX,
            "application/vnd.ms-excel": DocumentFormat.XLS,
            "text/markdown": DocumentFormat.MARKDOWN,
            "text/html": DocumentFormat.HTML,
            "text/plain": DocumentFormat.TXT,
            "application/json": DocumentFormat.JSON,
            "text/csv": DocumentFormat.CSV,
            "application/xml": DocumentFormat.XML,
            "image/png": DocumentFormat.PNG,
            "image/jpeg": DocumentFormat.JPG,
            "image/tiff": DocumentFormat.TIFF,
            "image/bmp": DocumentFormat.BMP,
            "image/gif": DocumentFormat.GIF,
        }
        if mime in mime_map:
            return mime_map[mime]
    except Exception:
        pass
    
    return None


def get_file_info(file_path: Path) -> DocumentInfo:
    """Get information about a document file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        DocumentInfo object with file information.
    """
    info = DocumentInfo()
    info.path = file_path
    info.format = detect_format(file_path)
    
    if file_path.exists():
        stat = file_path.stat()
        info.size_bytes = stat.st_size
        info.created_at = datetime.fromtimestamp(stat.st_ctime)
        info.modified_at = datetime.fromtimestamp(stat.st_mtime)
    
    return info


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename for safe usage.
    
    Args:
        filename: Original filename.
        max_length: Maximum length of filename.
        
    Returns:
        Sanitized filename.
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > max_length:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:max_length - len(ext)] + ext
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = "document"
    
    return filename


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not.
    
    Args:
        path: Directory path.
        
    Returns:
        Path object.
    """
    path = Path(path).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(
    input_path: Path,
    output_dir: Optional[Path] = None,
    output_format: Optional[str] = None,
    suffix: Optional[str] = None,
) -> Path:
    """Generate output path for converted file.
    
    Args:
        input_path: Input file path.
        output_dir: Output directory (optional).
        output_format: Output format extension (optional).
        suffix: Additional suffix for filename (optional).
        
    Returns:
        Output file path.
    """
    # Determine output directory
    if output_dir:
        output_dir = ensure_dir(output_dir)
    else:
        output_dir = input_path.parent
    
    # Build filename
    stem = input_path.stem
    if suffix:
        stem = f"{stem}_{suffix}"
    
    # Determine extension
    if output_format:
        ext = output_format.lower()
        if not ext.startswith('.'):
            ext = f".{ext}"
    else:
        ext = ".md"
    
    output_path = output_dir / f"{stem}{ext}"
    
    # Handle duplicates
    counter = 1
    original_path = output_path
    while output_path.exists():
        output_path = original_path.parent / f"{stem}_{counter}{ext}"
        counter += 1
    
    return output_path


def is_supported_format(file_path: Path) -> bool:
    """Check if file format is supported.
    
    Args:
        file_path: Path to file.
        
    Returns:
        True if format is supported.
    """
    return detect_format(file_path) is not None


def get_format_from_string(format_str: str) -> Optional[DocumentFormat]:
    """Get DocumentFormat from string.
    
    Args:
        format_str: Format string (e.g., "pdf", "docx").
        
    Returns:
        DocumentFormat or None.
    """
    format_str = format_str.lower().strip('.')
    
    # Direct match
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
    
    if format_str in aliases:
        return aliases[format_str]
    
    return None
