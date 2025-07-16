"""Data models for QuestMaster AI."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator, model_validator


class QuestState(str, Enum):
    """Quest state enumeration."""
    
    INITIAL = "initial"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionChoice(BaseModel):
    """Represents a choice the user can make."""
    
    id: str = Field(..., description="Unique identifier for the choice")
    text: str = Field(..., description="Display text for the choice")
    target_state: str = Field(..., description="Target state ID")
    description: Optional[str] = Field(default=None, description="Additional description")


class StoryState(BaseModel):
    """Represents a state in the interactive story."""
    
    id: str = Field(..., description="Unique identifier for the state")
    text: str = Field(..., description="Main narrative text")
    actions: List[ActionChoice] = Field(default_factory=list, description="Available actions")
    is_terminal: bool = Field(default=False, description="Whether this is an ending state")
    image_url: Optional[str] = Field(default=None, description="Optional image URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StoryGraph(BaseModel):
    """Complete story representation as a state machine."""
    
    title: str = Field(..., description="Story title")
    description: str = Field(..., description="Story description")
    initial_state: str = Field(..., description="ID of the initial state")
    states: Dict[str, StoryState] = Field(..., description="All story states")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Story metadata")

    @model_validator(mode='after')
    def validate_initial_state(self) -> 'StoryGraph':
        """Validate that initial_state exists in states."""
        if self.initial_state not in self.states:
            raise ValueError(f"Initial state '{self.initial_state}' not found in states")
        return self

    def get_state(self, state_id: str) -> Optional[StoryState]:
        """Get a state by ID."""
        return self.states.get(state_id)

    def get_terminal_states(self) -> List[StoryState]:
        """Get all terminal states."""
        return [state for state in self.states.values() if state.is_terminal]

    @classmethod
    def from_legacy_format(cls, data: Dict[str, Any]) -> StoryGraph:
        """Create StoryGraph from legacy JSON format."""
        states = {}
        
        for state_id, state_data in data.items():
            actions = []
            for action_text, target_state in state_data.get("actions", {}).items():
                actions.append(ActionChoice(
                    id=f"{state_id}_{len(actions)}",
                    text=action_text,
                    target_state=target_state
                ))
            
            states[state_id] = StoryState(
                id=state_id,
                text=state_data.get("text", ""),
                actions=actions,
                is_terminal=len(actions) == 0
            )
        
        # Assume first state is initial (or "start" if it exists)
        initial_state = "start" if "start" in states else list(states.keys())[0]
        
        return cls(
            title="Generated Quest",
            description="AI-generated interactive quest",
            initial_state=initial_state,
            states=states
        )


class Lore(BaseModel):
    """Represents the quest lore/description."""
    
    title: str = Field(..., description="Quest title")
    description: str = Field(..., description="Quest description")
    initial_state: str = Field(..., description="Description of initial state")
    goal: str = Field(..., description="Quest goal")
    world_context: str = Field(..., description="World/setting context")
    obstacles: List[str] = Field(default_factory=list, description="Potential obstacles")
    branching_factor: Dict[str, int] = Field(
        default_factory=lambda: {"min": 1, "max": 3},
        description="Min/max choices per state"
    )
    depth_constraints: Dict[str, int] = Field(
        default_factory=lambda: {"min": 3, "max": 10},
        description="Min/max steps to goal"
    )
    characters: List[str] = Field(default_factory=list, description="Important characters")
    locations: List[str] = Field(default_factory=list, description="Important locations")
    items: List[str] = Field(default_factory=list, description="Important items")

    @classmethod
    def from_legacy_json(cls, json_data: Union[str, Dict[str, Any]]) -> Lore:
        """Create Lore from legacy JSON format."""
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                # If not valid JSON, treat as simple description
                return cls(
                    title="Legacy Quest",
                    description=json_data,
                    initial_state="Starting state",
                    goal="Complete the quest",
                    world_context="Fantasy world"
                )
        else:
            data = json_data

        return cls(
            title=data.get("title", "Legacy Quest"),
            description=data.get("description", ""),
            initial_state=data.get("initial_state", "Starting state"),
            goal=data.get("goal", "Complete the quest"),
            world_context=data.get("world_context", "Fantasy world"),
            obstacles=data.get("obstacles", []),
            branching_factor=data.get("branching_factor", {"min": 1, "max": 3}),
            depth_constraints=data.get("depth_constraints", {"min": 3, "max": 10}),
            characters=data.get("characters", []),
            locations=data.get("locations", []),
            items=data.get("items", [])
        )


class PDDLDomain(BaseModel):
    """Represents a PDDL domain file."""
    
    name: str = Field(..., description="Domain name")
    content: str = Field(..., description="PDDL domain content")
    predicates: List[str] = Field(default_factory=list, description="Domain predicates")
    actions: List[str] = Field(default_factory=list, description="Domain actions")
    
    @classmethod
    def from_file(cls, file_path: Path) -> PDDLDomain:
        """Load PDDL domain from file."""
        content = file_path.read_text(encoding="utf-8")
        
        # Extract domain name
        name = "unknown"
        for line in content.split("\n"):
            if line.strip().startswith("(domain"):
                name = line.strip().split()[1].rstrip(")")
                break
        
        return cls(name=name, content=content)

    def save_to_file(self, file_path: Path) -> None:
        """Save PDDL domain to file."""
        file_path.write_text(self.content, encoding="utf-8")


class PDDLProblem(BaseModel):
    """Represents a PDDL problem file."""
    
    name: str = Field(..., description="Problem name")
    domain: str = Field(..., description="Associated domain name")
    content: str = Field(..., description="PDDL problem content")
    objects: List[str] = Field(default_factory=list, description="Problem objects")
    init: List[str] = Field(default_factory=list, description="Initial state")
    goal: List[str] = Field(default_factory=list, description="Goal state")
    
    @classmethod
    def from_file(cls, file_path: Path) -> PDDLProblem:
        """Load PDDL problem from file."""
        content = file_path.read_text(encoding="utf-8")
        
        # Extract problem name and domain
        name = "unknown"
        domain = "unknown"
        for line in content.split("\n"):
            if line.strip().startswith("(problem"):
                name = line.strip().split()[1].rstrip(")")
            elif ":domain" in line:
                domain = line.strip().split()[1].rstrip(")")
        
        return cls(name=name, domain=domain, content=content)

    def save_to_file(self, file_path: Path) -> None:
        """Save PDDL problem to file."""
        file_path.write_text(self.content, encoding="utf-8")


class ValidationResult(BaseModel):
    """Result of PDDL validation."""
    
    is_valid: bool = Field(..., description="Whether the PDDL is valid")
    has_solution: bool = Field(default=False, description="Whether a solution exists")
    error_message: str = Field(default="", description="Error message if invalid")
    plan: Optional[List[str]] = Field(None, description="Generated plan if valid")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    
    @property
    def success(self) -> bool:
        """Whether validation was completely successful."""
        return self.is_valid and self.has_solution
