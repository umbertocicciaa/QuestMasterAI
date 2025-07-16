"""Utility functions for QuestMaster AI."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..core.exceptions import FileError


def extract_pddl_blocks(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract PDDL domain and problem blocks from text.
    
    Args:
        text: Text containing PDDL blocks
        
    Returns:
        Tuple of (domain_content, problem_content)
    """
    domain_pattern = r"<DOMAIN_PDDL>(.*?)</DOMAIN_PDDL>"
    problem_pattern = r"<PROBLEM_PDDL>(.*?)</PROBLEM_PDDL>"
    
    domain_match = re.search(domain_pattern, text, re.DOTALL)
    problem_match = re.search(problem_pattern, text, re.DOTALL)
    
    domain = domain_match.group(1).strip() if domain_match else None
    problem = problem_match.group(1).strip() if problem_match else None
    
    return domain, problem


def extract_xml_blocks(text: str, tag: str) -> List[str]:
    """Extract content from XML-like tags.
    
    Args:
        text: Text containing XML blocks
        tag: Tag name to extract
        
    Returns:
        List of extracted content blocks
    """
    pattern = f"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def ensure_file_extension(file_path: Path, extension: str) -> Path:
    """Ensure a file path has the correct extension.
    
    Args:
        file_path: Original file path
        extension: Required extension (with or without dot)
        
    Returns:
        File path with correct extension
    """
    if not extension.startswith('.'):
        extension = f'.{extension}'
    
    if not file_path.suffix == extension:
        return file_path.with_suffix(extension)
    
    return file_path


def validate_pddl_syntax(content: str) -> Tuple[bool, List[str]]:
    """Basic PDDL syntax validation.
    
    Args:
        content: PDDL content to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check balanced parentheses
    paren_count = 0
    for char in content:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
            if paren_count < 0:
                errors.append("Unbalanced closing parenthesis")
                break
    
    if paren_count > 0:
        errors.append("Unbalanced opening parenthesis")
    
    # Check for required sections (basic check)
    if '(define' not in content:
        errors.append("Missing (define section")
    
    # Check for common PDDL keywords
    lines = content.lower().split('\\n')
    has_domain_or_problem = any(
        ':domain' in line or '(domain' in line or '(problem' in line
        for line in lines
    )
    
    if not has_domain_or_problem:
        errors.append("Missing domain or problem declaration")
    
    return len(errors) == 0, errors


def create_backup_file(file_path: Path) -> Path:
    """Create a backup of a file.
    
    Args:
        file_path: Path to file to backup
        
    Returns:
        Path to backup file
        
    Raises:
        FileError: If backup creation fails
    """
    if not file_path.exists():
        raise FileError(f"Cannot backup non-existent file: {file_path}")
    
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    
    # If backup already exists, add a number
    counter = 1
    while backup_path.exists():
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{counter}")
        counter += 1
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        raise FileError(f"Failed to create backup: {e}") from e


def parse_plan_file(plan_content: str) -> List[Dict[str, str]]:
    """Parse a plan file into structured actions.
    
    Args:
        plan_content: Raw plan file content
        
    Returns:
        List of parsed actions with metadata
    """
    actions = []
    
    for line_num, line in enumerate(plan_content.split('\\n'), 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith(';'):
            continue
        
        # Parse action line (basic parsing)
        action_match = re.match(r'\\(([^)]+)\\)', line)
        if action_match:
            action_str = action_match.group(1)
            parts = action_str.split()
            
            action = {
                'line_number': line_num,
                'raw': line,
                'action': parts[0] if parts else '',
                'parameters': parts[1:] if len(parts) > 1 else [],
                'full_action': action_str,
            }
            actions.append(action)
    
    return actions


def format_time_duration(seconds: float) -> str:
    """Format time duration in a human-readable way.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
