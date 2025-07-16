"""File operations service."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import get_settings
from ..core.exceptions import FileError
from ..models import Lore, PDDLDomain, PDDLProblem, StoryGraph


class FileService:
    """Service for file operations."""
    
    def __init__(self) -> None:
        """Initialize file service."""
        self.settings = get_settings()

    def load_lore(self, file_path: Optional[Path] = None) -> Lore:
        """Load lore from file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Loaded lore object
            
        Raises:
            FileError: If file cannot be loaded or parsed
        """
        path = file_path or self.settings.lore_path
        
        try:
            if not path.exists():
                raise FileError(f"Lore file not found: {path}")
            
            content = path.read_text(encoding="utf-8")
            
            # Try to parse as JSON first
            try:
                data = json.loads(content)
                return Lore.from_legacy_json(data)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text description
                return Lore.from_legacy_json(content)
                
        except Exception as e:
            raise FileError(f"Failed to load lore from {path}: {e}") from e

    def save_lore(self, lore: Lore, file_path: Optional[Path] = None) -> None:
        """Save lore to file.
        
        Args:
            lore: Lore object to save
            file_path: Optional custom file path
            
        Raises:
            FileError: If file cannot be saved
        """
        path = file_path or self.settings.lore_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(lore.model_dump_json(indent=2), encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to save lore to {path}: {e}") from e

    def load_domain(self, file_path: Optional[Path] = None) -> PDDLDomain:
        """Load PDDL domain from file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Loaded domain object
            
        Raises:
            FileError: If file cannot be loaded
        """
        path = file_path or self.settings.domain_path
        
        try:
            if not path.exists():
                raise FileError(f"Domain file not found: {path}")
            return PDDLDomain.from_file(path)
        except Exception as e:
            raise FileError(f"Failed to load domain from {path}: {e}") from e

    def save_domain(self, domain: PDDLDomain, file_path: Optional[Path] = None) -> None:
        """Save PDDL domain to file.
        
        Args:
            domain: Domain object to save
            file_path: Optional custom file path
            
        Raises:
            FileError: If file cannot be saved
        """
        path = file_path or self.settings.domain_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            domain.save_to_file(path)
        except Exception as e:
            raise FileError(f"Failed to save domain to {path}: {e}") from e

    def load_problem(self, file_path: Optional[Path] = None) -> PDDLProblem:
        """Load PDDL problem from file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Loaded problem object
            
        Raises:
            FileError: If file cannot be loaded
        """
        path = file_path or self.settings.problem_path
        
        try:
            if not path.exists():
                raise FileError(f"Problem file not found: {path}")
            return PDDLProblem.from_file(path)
        except Exception as e:
            raise FileError(f"Failed to load problem from {path}: {e}") from e

    def save_problem(self, problem: PDDLProblem, file_path: Optional[Path] = None) -> None:
        """Save PDDL problem to file.
        
        Args:
            problem: Problem object to save
            file_path: Optional custom file path
            
        Raises:
            FileError: If file cannot be saved
        """
        path = file_path or self.settings.problem_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            problem.save_to_file(path)
        except Exception as e:
            raise FileError(f"Failed to save problem to {path}: {e}") from e

    def load_story(self, file_path: Optional[Path] = None) -> StoryGraph:
        """Load story from file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Loaded story object
            
        Raises:
            FileError: If file cannot be loaded
        """
        path = file_path or self.settings.story_path
        
        try:
            if not path.exists():
                raise FileError(f"Story file not found: {path}")
            
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            
            # Check if it's already in the new format
            if "states" in data and "initial_state" in data:
                return StoryGraph.model_validate(data)
            else:
                # Convert from legacy format
                return StoryGraph.from_legacy_format(data)
                
        except Exception as e:
            raise FileError(f"Failed to load story from {path}: {e}") from e

    def save_story(self, story: StoryGraph, file_path: Optional[Path] = None) -> None:
        """Save story to file.
        
        Args:
            story: Story object to save
            file_path: Optional custom file path
            
        Raises:
            FileError: If file cannot be saved
        """
        path = file_path or self.settings.story_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(story.model_dump_json(indent=2), encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to save story to {path}: {e}") from e

    def load_plan(self, file_path: Optional[Path] = None) -> str:
        """Load plan from file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Plan content as string
            
        Raises:
            FileError: If file cannot be loaded
        """
        path = file_path or self.settings.plan_path
        
        try:
            if not path.exists():
                raise FileError(f"Plan file not found: {path}")
            return path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to load plan from {path}: {e}") from e

    def load_example_domain(self) -> str:
        """Load example domain content."""
        try:
            return self.settings.example_domain_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to load example domain: {e}") from e

    def load_example_problem(self) -> str:
        """Load example problem content."""
        try:
            return self.settings.example_problem_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to load example problem: {e}") from e

    def load_example_story(self) -> Dict[str, Any]:
        """Load example story content."""
        try:
            content = self.settings.example_story_path.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception as e:
            raise FileError(f"Failed to load example story: {e}") from e

    def save_frontend(self, content: str, file_path: Optional[Path] = None) -> None:
        """Save generated frontend code.
        
        Args:
            content: Frontend code content
            file_path: Optional custom file path
            
        Raises:
            FileError: If file cannot be saved
        """
        path = file_path or self.settings.frontend_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise FileError(f"Failed to save frontend to {path}: {e}") from e
