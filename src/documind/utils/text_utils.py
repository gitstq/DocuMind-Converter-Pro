"""
Text utility functions for DocuMind Converter.
"""

import re
from typing import List, Optional


def clean_text(text: str, preserve_linebreaks: bool = True) -> str:
    """Clean and normalize text.
    
    Args:
        text: Input text.
        preserve_linebreaks: Whether to preserve line breaks.
        
    Returns:
        Cleaned text.
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    if preserve_linebreaks:
        # Replace multiple spaces with single space, but preserve line breaks
        lines = text.split('\n')
        lines = [' '.join(line.split()) for line in lines]
        text = '\n'.join(lines)
    else:
        # Replace all whitespace with single space
        text = ' '.join(text.split())
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char >= ' ' or char in '\n\t')
    
    return text.strip()


def extract_text_chunks(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Extract text chunks for processing.
    
    Args:
        text: Input text.
        chunk_size: Size of each chunk.
        overlap: Overlap between chunks.
        
    Returns:
        List of text chunks.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        # Try to break at sentence boundary
        if end < text_len:
            # Look for sentence ending
            for i in range(end, max(start + chunk_size - 200, start), -1):
                if text[i-1:i+1] in ['. ', '! ', '? ', '。', '！', '？']:
                    end = i + 1
                    break
        
        chunks.append(text[start:end].strip())
        start = end - overlap
    
    return chunks


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """Estimate reading time in minutes.
    
    Args:
        text: Input text.
        words_per_minute: Average reading speed.
        
    Returns:
        Estimated reading time in minutes.
    """
    if not text:
        return 0.0
    
    # Count words
    words = len(text.split())
    
    # Calculate reading time
    reading_time = words / words_per_minute
    
    return round(reading_time, 1)


def calculate_complexity(text: str) -> float:
    """Calculate text complexity score (0-100).
    
    Args:
        text: Input text.
        
    Returns:
        Complexity score between 0 and 100.
    """
    if not text:
        return 0.0
    
    # Simple complexity metrics
    words = text.split()
    if not words:
        return 0.0
    
    sentences = re.split(r'[.!?。！？]+', text)
    sentences = [s for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Average sentence length
    avg_sentence_length = len(words) / len(sentences)
    
    # Complex words (more than 3 syllables, approximated by length > 6)
    complex_words = [w for w in words if len(w) > 6]
    complex_word_ratio = len(complex_words) / len(words)
    
    # Calculate score (simplified Flesch-Kincaid inspired)
    score = (
        (avg_word_length * 5) +
        (avg_sentence_length * 0.5) +
        (complex_word_ratio * 30)
    )
    
    # Normalize to 0-100
    score = min(100, max(0, score))
    
    return round(score, 1)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Input text.
        max_length: Maximum length.
        suffix: Suffix to add if truncated.
        
    Returns:
        Truncated text.
    """
    if not text or len(text) <= max_length:
        return text
    
    # Account for suffix length
    truncate_at = max_length - len(suffix)
    
    # Try to break at word boundary
    truncated = text[:truncate_at]
    last_space = truncated.rfind(' ')
    
    if last_space > truncate_at * 0.8:  # If word boundary is close
        truncated = truncated[:last_space]
    
    return truncated.strip() + suffix


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text.
    
    Args:
        text: Input text.
        
    Returns:
        List of URLs.
    """
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text.
    
    Args:
        text: Input text.
        
    Returns:
        List of email addresses.
    """
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return email_pattern.findall(text)


def count_words(text: str) -> int:
    """Count words in text.
    
    Args:
        text: Input text.
        
    Returns:
        Word count.
    """
    if not text:
        return 0
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count sentences in text.
    
    Args:
        text: Input text.
        
    Returns:
        Sentence count.
    """
    if not text:
        return 0
    
    # Split by sentence terminators
    sentences = re.split(r'[.!?。！？]+', text)
    return len([s for s in sentences if s.strip()])


def detect_language(text: str) -> Optional[str]:
    """Detect language of text (simple heuristic).
    
    Args:
        text: Input text.
        
    Returns:
        Language code or None.
    """
    if not text:
        return None
    
    # Simple heuristics for common languages
    text_sample = text[:1000].lower()
    
    # Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text_sample):
        return "zh"
    
    # Japanese characters
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text_sample):
        return "ja"
    
    # Korean characters
    if re.search(r'[\uac00-\ud7af]', text_sample):
        return "ko"
    
    # Arabic characters
    if re.search(r'[\u0600-\u06ff]', text_sample):
        return "ar"
    
    # Cyrillic characters
    if re.search(r'[\u0400-\u04ff]', text_sample):
        return "ru"
    
    # Default to English for Latin script
    return "en"


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text.
    
    Args:
        text: Input text with HTML.
        
    Returns:
        Text without HTML tags.
    """
    if not text:
        return ""
    
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    import html
    text = html.unescape(text)
    
    return clean_text(text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.
    
    Args:
        text: Input text.
        
    Returns:
        Text with normalized whitespace.
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
