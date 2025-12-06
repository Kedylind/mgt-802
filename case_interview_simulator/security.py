"""
Security utilities for input sanitization and prompt injection protection.
"""
import re
from typing import Optional


class SecurityValidator:
    """Validates and sanitizes user input."""
    
    # Patterns that might indicate prompt injection attempts
    SUSPICIOUS_PATTERNS = [
        r'ignore\s+(previous|all)\s+instructions?',
        r'system\s*:',
        r'<\|.*?\|>',
        r'###\s*instruction',
        r'forget\s+everything',
        r'you\s+are\s+now',
        r'new\s+role',
        r'disregard',
        r'override',
    ]
    
    @classmethod
    def sanitize_input(cls, text: str, max_length: int = 5000) -> str:
        """
        Sanitize user input.
        
        Args:
            text: The input text
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        # Limit length
        text = text[:max_length]
        
        # Remove potential HTML/script tags
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<.*?>', '', text)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @classmethod
    def detect_prompt_injection(cls, text: str) -> tuple[bool, Optional[str]]:
        """
        Detect potential prompt injection attempts.
        
        Args:
            text: The input text
            
        Returns:
            tuple: (is_suspicious, reason)
        """
        text_lower = text.lower()
        
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, f"Suspicious pattern detected: {pattern}"
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        if special_char_ratio > 0.3:
            return True, "Excessive special characters"
        
        return False, None
    
    @classmethod
    def validate_message(cls, message: str) -> tuple[bool, str, Optional[str]]:
        """
        Validate a chat message.
        
        Args:
            message: The message to validate
            
        Returns:
            tuple: (is_valid, sanitized_message, error_message)
        """
        # Check length
        if len(message) > 5000:
            return False, "", "Message too long (max 5000 characters)"
        
        if len(message.strip()) == 0:
            return False, "", "Message cannot be empty"
        
        # Sanitize
        sanitized = cls.sanitize_input(message)
        
        # Check for prompt injection
        is_suspicious, reason = cls.detect_prompt_injection(sanitized)
        if is_suspicious:
            return False, "", f"Message blocked: {reason}"
        
        return True, sanitized, None


def sanitize_exhibit_data(exhibit: dict) -> dict:
    """
    Sanitize exhibit data to prevent injection.
    
    Args:
        exhibit: The exhibit dictionary
        
    Returns:
        dict: Sanitized exhibit
    """
    if not isinstance(exhibit, dict):
        return {}
    
    sanitized = {}
    
    # Only allow specific keys
    allowed_keys = ['title', 'type', 'data', 'description']
    
    for key in allowed_keys:
        if key in exhibit:
            value = exhibit[key]
            
            if isinstance(value, str):
                sanitized[key] = SecurityValidator.sanitize_input(value, max_length=10000)
            elif isinstance(value, (dict, list)):
                # For data structures, convert to string and back to ensure safety
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
    
    return sanitized
