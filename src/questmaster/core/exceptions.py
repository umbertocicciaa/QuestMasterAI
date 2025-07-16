"""Custom exceptions for QuestMaster AI."""

from typing import Optional


class QuestMasterError(Exception):
    """Base exception for QuestMaster AI."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """Initialize exception.
        
        Args:
            message: Error message
            cause: Optional underlying exception
        """
        super().__init__(message)
        self.message = message
        self.cause = cause


class ConfigurationError(QuestMasterError):
    """Configuration-related errors."""
    pass


class PDDLError(QuestMasterError):
    """PDDL-related errors."""
    pass


class ValidationError(PDDLError):
    """PDDL validation errors."""
    pass


class PlannerError(PDDLError):
    """Fast Downward planner errors."""
    pass


class LLMError(QuestMasterError):
    """LLM-related errors."""
    pass


class FileError(QuestMasterError):
    """File operation errors."""
    pass


class StoryError(QuestMasterError):
    """Story generation/parsing errors."""
    pass
