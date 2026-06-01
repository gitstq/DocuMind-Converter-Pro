"""
Configuration management for DocuMind Converter.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConverterConfig(BaseSettings):
    """Configuration for document converter."""
    
    model_config = SettingsConfigDict(
        env_prefix="DOCUMIND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # General settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # AI settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    openai_base_url: Optional[str] = Field(default=None, description="OpenAI base URL")
    enable_ai_analysis: bool = Field(default=True, description="Enable AI analysis features")
    
    # Conversion settings
    default_output_format: str = Field(default="markdown", description="Default output format")
    preserve_formatting: bool = Field(default=True, description="Preserve original formatting")
    extract_images: bool = Field(default=False, description="Extract images from documents")
    ocr_enabled: bool = Field(default=True, description="Enable OCR for images")
    
    # OCR settings
    tesseract_cmd: Optional[str] = Field(default=None, description="Tesseract command path")
    ocr_language: str = Field(default="eng", description="OCR language")
    
    # Batch processing
    max_workers: int = Field(default=4, description="Maximum number of worker threads")
    chunk_size: int = Field(default=1000, description="Text chunk size for processing")
    
    # Output settings
    output_dir: Optional[Path] = Field(default=None, description="Default output directory")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing files")
    
    # Plugin settings
    plugin_dir: Optional[Path] = Field(default=None, description="Plugin directory")
    enabled_plugins: List[str] = Field(default_factory=list, description="List of enabled plugins")
    
    # Watch settings
    watch_interval: float = Field(default=1.0, description="Watch interval in seconds")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper
    
    @field_validator("output_dir", "plugin_dir")
    @classmethod
    def validate_path(cls, v: Optional[Path]) -> Optional[Path]:
        """Validate and expand path."""
        if v is None:
            return None
        path = Path(v).expanduser().resolve()
        return path
    
    @field_validator("max_workers")
    @classmethod
    def validate_workers(cls, v: int) -> int:
        """Validate worker count."""
        if v < 1:
            return 1
        if v > 16:
            return 16
        return v


class Config:
    """Global configuration singleton."""
    
    _instance: Optional[ConverterConfig] = None
    
    @classmethod
    def get_instance(cls) -> ConverterConfig:
        """Get configuration instance."""
        if cls._instance is None:
            cls._instance = ConverterConfig()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset configuration instance."""
        cls._instance = None
    
    @classmethod
    def load_from_file(cls, path: Path) -> ConverterConfig:
        """Load configuration from file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        # Set environment variables from file
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        
        cls._instance = ConverterConfig()
        return cls._instance


# Global config instance
config = Config.get_instance()
