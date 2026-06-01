"""
Data models for DocuMind Converter.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    PPTX = "pptx"
    PPT = "ppt"
    XLSX = "xlsx"
    XLS = "xls"
    MARKDOWN = "markdown"
    MD = "md"
    HTML = "html"
    TXT = "txt"
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    IMAGE = "image"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    EPUB = "epub"
    RTF = "rtf"
    ODT = "odt"
    ODS = "ods"
    ODP = "odp"


class ConversionStatus(Enum):
    """Conversion operation status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class DocumentInfo:
    """Information about a document."""
    path: Optional[Path] = None
    format: Optional[DocumentFormat] = None
    size_bytes: int = 0
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": str(self.path) if self.path else None,
            "format": self.format.value if self.format else None,
            "size_bytes": self.size_bytes,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "author": self.author,
            "title": self.title,
            "subject": self.subject,
            "keywords": self.keywords,
            "metadata": self.metadata,
        }


@dataclass
class ConversionResult:
    """Result of a document conversion operation."""
    status: ConversionStatus
    content: str = ""
    output_path: Optional[Path] = None
    source_info: DocumentInfo = field(default_factory=DocumentInfo)
    target_format: Optional[DocumentFormat] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate status and content consistency."""
        if self.status == ConversionStatus.SUCCESS and not self.content:
            self.warnings.append("Conversion succeeded but content is empty")

    @property
    def success(self) -> bool:
        """Check if conversion was successful."""
        return self.status == ConversionStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if conversion failed."""
        return self.status == ConversionStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "content": self.content,
            "output_path": str(self.output_path) if self.output_path else None,
            "source_info": self.source_info.to_dict(),
            "target_format": self.target_format.value if self.target_format else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
        }


@dataclass
class AnalysisResult:
    """Result of document analysis."""
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    reading_time_minutes: Optional[float] = None
    complexity_score: Optional[float] = None
    language: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "key_points": self.key_points,
            "entities": self.entities,
            "sentiment": self.sentiment,
            "topics": self.topics,
            "reading_time_minutes": self.reading_time_minutes,
            "complexity_score": self.complexity_score,
            "language": self.language,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class BatchConversionResult:
    """Result of batch conversion operation."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    partial: int = 0
    results: List[ConversionResult] = field(default_factory=list)
    total_processing_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_files == 0:
            return 0.0
        return (self.successful / self.total_files) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "successful": self.successful,
            "failed": self.failed,
            "partial": self.partial,
            "success_rate": self.success_rate,
            "total_processing_time_ms": self.total_processing_time_ms,
            "results": [r.to_dict() for r in self.results],
            "errors": self.errors,
        }


@dataclass
class WatchConfig:
    """Configuration for directory watching."""
    watch_path: Path
    output_path: Path
    recursive: bool = True
    formats: List[DocumentFormat] = field(default_factory=list)
    auto_convert: bool = True
    auto_analyze: bool = False
    delete_after_convert: bool = False
    move_to_processed: bool = True
    processed_folder: str = "processed"


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    supported_formats: List[DocumentFormat] = field(default_factory=list)
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
