"""Configuration management for QuestMaster AI."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    chatgpt_model: str = Field(
        default="gpt-4o-mini-2024-07-18", description="ChatGPT model to use"
    )
    openai_max_retries: int = Field(default=3, description="Max retries for OpenAI API")
    openai_timeout: int = Field(default=60, description="Timeout for OpenAI API calls")

    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")

    # Fast Downward Configuration
    fast_downward_path: Optional[Path] = Field(
        default=None, description="Path to Fast Downward installation"
    )
    fast_downward_timeout: int = Field(
        default=300, description="Timeout for Fast Downward execution"
    )

    # File Paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent,
        description="Base directory of the application",
    )
    data_dir_override: Optional[Path] = Field(default=None, description="Data directory override")
    resources_dir_override: Optional[Path] = Field(default=None, description="Resources directory override")

    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, description="Streamlit port")
    streamlit_host: str = Field(default="0.0.0.0", description="Streamlit host")

    def model_post_init(self, __context) -> None:
        """Post-init model validation."""
        # Set default Fast Downward path if not provided
        if self.fast_downward_path is None:
            self.fast_downward_path = self.base_dir / "fast-downward-24.06.1"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.resources_dir.mkdir(parents=True, exist_ok=True)

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.data_dir_override or self.base_dir / "data"

    @property
    def resources_dir(self) -> Path:
        """Get resources directory."""
        return self.resources_dir_override or self.base_dir / "resources"

    @property
    def lore_path(self) -> Path:
        """Path to the lore file."""
        return self.data_dir / "lore.json"

    @property
    def domain_path(self) -> Path:
        """Path to the domain PDDL file."""
        return self.data_dir / "domain.pddl"

    @property
    def problem_path(self) -> Path:
        """Path to the problem PDDL file."""
        return self.data_dir / "problem.pddl"

    @property
    def story_path(self) -> Path:
        """Path to the story JSON file."""
        return self.data_dir / "story.json"

    @property
    def plan_path(self) -> Path:
        """Path to the SAS plan file."""
        return self.base_dir / "sas_plan"

    @property
    def frontend_path(self) -> Path:
        """Path to the generated frontend file."""
        return self.base_dir / "src" / "questmaster" / "ui" / "generated_frontend.py"

    @property
    def example_domain_path(self) -> Path:
        """Path to the example domain file."""
        return self.resources_dir / "valid_domain.pddl"

    @property
    def example_problem_path(self) -> Path:
        """Path to the example problem file."""
        return self.resources_dir / "valid_problem.pddl"

    @property
    def example_story_path(self) -> Path:
        """Path to the example story file."""
        return self.resources_dir / "story_example.json"


def get_settings() -> Settings:
    """Get settings instance, creating it with appropriate defaults if needed."""
    try:
        return Settings()
    except Exception:
        # Fallback for development/testing without env vars
        import os
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "test-key"
        return Settings()
