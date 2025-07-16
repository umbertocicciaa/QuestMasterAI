"""Story generator agent."""

import json

from ..core.exceptions import LLMError, StoryError
from ..core.logging import get_logger
from ..models import Lore, PDDLDomain, PDDLProblem, StoryGraph
from ..services import FileService, LLMService

logger = get_logger(__name__)


class StoryGeneratorAgent:
    """Agent for generating interactive story from PDDL and lore."""
    
    def __init__(
        self,
        llm_service: LLMService,
        file_service: FileService,
    ) -> None:
        """Initialize story generator agent.
        
        Args:
            llm_service: LLM service instance
            file_service: File service instance
        """
        self.llm_service = llm_service
        self.file_service = file_service

    def generate_story(
        self,
        lore: Lore,
        domain: PDDLDomain,
        problem: PDDLProblem,
        plan: list[str],
    ) -> StoryGraph:
        """Generate interactive story from PDDL and plan.
        
        Args:
            lore: Quest lore
            domain: PDDL domain
            problem: PDDL problem
            plan: Generated plan steps
            
        Returns:
            Generated story graph
            
        Raises:
            StoryError: If story generation fails
        """
        logger.info("Generating interactive story", title=lore.title)
        
        story_json = ""  # Initialize to avoid scope issues
        
        try:
            # Load example story for context
            example_story = self.file_service.load_example_story()
            
            # Create story generation prompt
            prompt = self._create_story_prompt(
                lore,
                domain,
                problem,
                plan,
                example_story,
            )
            
            # Generate story content
            response = self.llm_service.generate_completion(prompt)
            logger.debug("Raw LLM response received", response_length=len(response))
            
            # Try to extract JSON from response
            # First try to find XML blocks
            json_blocks = self.llm_service.extract_xml_blocks(response, "STORY_JSON")
            
            if json_blocks:
                story_json = json_blocks[0]
                logger.debug("Found XML JSON block", json_length=len(story_json))
            else:
                # Try to find markdown JSON blocks
                markdown_blocks = self.llm_service.extract_json_blocks(response)
                if markdown_blocks:
                    story_json = markdown_blocks[0]
                    logger.debug("Found markdown JSON block", json_length=len(story_json))
                else:
                    # Try to parse the entire response as JSON
                    story_json = response.strip()
                    logger.debug("Using full response as JSON", json_length=len(story_json))
            
            # Validate JSON is not empty
            if not story_json.strip():
                raise StoryError("Empty JSON response from LLM")
            
            # Parse JSON
            story_data = json.loads(story_json)
            logger.debug("Parsed story data", keys=list(story_data.keys()))
            
            # Log the structure for debugging
            if "states" in story_data:
                states = story_data["states"]
                if isinstance(states, dict):
                    logger.debug("States as dict", state_ids=list(states.keys()))
                elif isinstance(states, list):
                    logger.debug("States as list", count=len(states))
                    # Convert list to dict if needed
                    states_dict = {}
                    for i, state in enumerate(states):
                        if isinstance(state, dict) and "id" in state:
                            states_dict[state["id"]] = state
                        else:
                            states_dict[f"state_{i}"] = state
                    story_data["states"] = states_dict
                    logger.debug("Converted states list to dict", state_ids=list(states_dict.keys()))
            
            # Convert to StoryGraph
            if "states" in story_data and "initial_state" in story_data:
                # Debug the structure before validation
                logger.info("Story data before validation", 
                           initial_state=story_data.get("initial_state"),
                           states_keys=list(story_data.get("states", {}).keys()),
                           states_type=type(story_data.get("states", {})))
                
                # Debug the start state structure
                start_state = story_data.get("states", {}).get("start", {})
                logger.info("Start state structure", 
                           start_state_keys=list(start_state.keys()) if isinstance(start_state, dict) else "not_dict",
                           start_state_type=type(start_state))
                
                # New format
                story = StoryGraph.model_validate(story_data)
            else:
                # Legacy format
                story = StoryGraph.from_legacy_format(story_data)
            
            # Update story metadata
            story.title = lore.title
            story.description = lore.description
            story.metadata.update({
                "generated_from_lore": True,
                "original_goal": lore.goal,
                "world_context": lore.world_context,
            })
            
            logger.info("Story generation completed successfully", states=len(story.states))
            return story
            
        except json.JSONDecodeError as e:
            # Get safe content for logging
            content_preview = story_json[:200] if len(story_json) > 0 else "Empty content"
            logger.error("Failed to parse story JSON", error=str(e), json_content=content_preview)
            raise StoryError(f"Failed to parse generated story JSON: {e}") from e
        except LLMError as e:
            logger.error("LLM error during story generation", error=str(e))
            raise StoryError(f"Failed to generate story: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during story generation", error=str(e))
            raise StoryError(f"Unexpected error in story generation: {e}") from e

    def _create_story_prompt(
        self,
        lore: Lore,
        domain: PDDLDomain,
        problem: PDDLProblem,
        plan: list[str],
        example_story: dict,
    ) -> str:
        """Create prompt for story generation.
        
        Args:
            lore: Quest lore
            domain: PDDL domain
            problem: PDDL problem
            plan: Generated plan
            example_story: Example story structure
            
        Returns:
            Formatted prompt string
        """
        plan_str = "\\n".join(plan) if plan else "No plan available"
        
        return f"""You are an expert interactive storyteller. Given the following quest information, PDDL files, and generated plan, create an engaging interactive story as a finite state machine.

QUEST INFORMATION:
Title: {lore.title}
Description: {lore.description}
Initial State: {lore.initial_state}
Goal: {lore.goal}
World Context: {lore.world_context}
Characters: {', '.join(lore.characters)}
Locations: {', '.join(lore.locations)}
Items: {', '.join(lore.items)}

PDDL DOMAIN:
{domain.content}

PDDL PROBLEM:
{problem.content}

GENERATED PLAN:
{plan_str}

REQUIREMENTS:
1. Create an engaging narrative that follows the quest progression
2. Each state should have rich, descriptive text
3. Provide meaningful choices that advance the story
4. Include both successful and failure paths
5. Make the story feel immersive and interactive
6. Respect the branching factor: {lore.branching_factor['min']}-{lore.branching_factor['max']} choices per state
7. Target depth: {lore.depth_constraints['min']}-{lore.depth_constraints['max']} story steps

Generate a story.json with the following structure:

<STORY_JSON>
{{
  "title": "{lore.title}",
  "description": "{lore.description}",
  "initial_state": "start",
  "states": {{
    "start": {{
      "id": "start",
      "text": "Engaging opening narrative...",
      "actions": [
        {{
          "id": "choice1",
          "text": "Choice 1 description",
          "target_state": "state1",
          "description": "Additional context"
        }}
      ],
      "is_terminal": false,
      "image_url": null,
      "metadata": {{}}
    }},
    "state1": {{
      "id": "state1", 
      "text": "Continuation of the story...",
      "actions": [],
      "is_terminal": true,
      "image_url": null,
      "metadata": {{}}
    }}
  }},
  "metadata": {{
    "theme": "fantasy",
    "difficulty": "medium"
  }}
}}
</STORY_JSON>

Use this example structure as inspiration, but make it more original and dynamic:

EXAMPLE STRUCTURE:
{json.dumps(example_story, indent=2)}

Make the story captivating, with rich descriptions and meaningful choices that matter to the outcome. Ensure there are multiple paths and endings based on player choices.
"""
