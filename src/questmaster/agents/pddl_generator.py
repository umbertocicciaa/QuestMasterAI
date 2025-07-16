"""PDDL generator agent."""

from typing import Tuple

from ..core.exceptions import LLMError, PDDLError
from ..core.logging import get_logger
from ..models import Lore, PDDLDomain, PDDLProblem
from ..services import FileService, LLMService

logger = get_logger(__name__)


class PDDLGeneratorAgent:
    """Agent for generating PDDL domain and problem files from lore."""
    
    def __init__(
        self,
        llm_service: LLMService,
        file_service: FileService,
    ) -> None:
        """Initialize PDDL generator agent.
        
        Args:
            llm_service: LLM service instance
            file_service: File service instance
        """
        self.llm_service = llm_service
        self.file_service = file_service

    def generate_pddl(self, lore: Lore) -> Tuple[PDDLDomain, PDDLProblem]:
        """Generate PDDL domain and problem from lore.
        
        Args:
            lore: Quest lore/description
            
        Returns:
            Tuple of (domain, problem)
            
        Raises:
            PDDLError: If PDDL generation fails
        """
        logger.info("Generating PDDL from lore", title=lore.title)
        
        try:
            # Load example files for context
            example_domain = self.file_service.load_example_domain()
            example_problem = self.file_service.load_example_problem()
            
            # Create prompt
            prompt = self._create_pddl_prompt(lore, example_domain, example_problem)
            
            # Generate PDDL content
            response = self.llm_service.generate_completion(prompt)
            
            # Extract PDDL blocks
            domain_content, problem_content = self.llm_service.extract_pddl_blocks(response)
            
            if not domain_content or not problem_content:
                raise PDDLError("Failed to extract PDDL blocks from LLM response")
            
            # Create PDDL objects
            domain = PDDLDomain(
                name=f"{lore.title.lower().replace(' ', '_')}_domain",
                content=domain_content,
            )
            
            problem = PDDLProblem(
                name=f"{lore.title.lower().replace(' ', '_')}_problem",
                domain=domain.name,
                content=problem_content,
            )
            
            logger.info("PDDL generation completed successfully")
            return domain, problem
            
        except LLMError as e:
            logger.error("LLM error during PDDL generation", error=str(e))
            raise PDDLError(f"Failed to generate PDDL: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during PDDL generation", error=str(e))
            raise PDDLError(f"Unexpected error in PDDL generation: {e}") from e

    def _create_pddl_prompt(
        self,
        lore: Lore,
        example_domain: str,
        example_problem: str,
    ) -> str:
        """Create prompt for PDDL generation.
        
        Args:
            lore: Quest lore
            example_domain: Example domain content
            example_problem: Example problem content
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a PDDL modeler expert. Given the following quest description, generate:
1. A DOMAIN.PDDL file with predicates and actions, each with comments.
2. A PROBLEM.PDDL file with an initial state and goal consistent with the domain.

Quest Information:
Title: {lore.title}
Description: {lore.description}
Initial State: {lore.initial_state}
Goal: {lore.goal}
World Context: {lore.world_context}

Additional Details:
- Characters: {', '.join(lore.characters)}
- Locations: {', '.join(lore.locations)}
- Items: {', '.join(lore.items)}
- Obstacles: {', '.join(lore.obstacles)}

Constraints:
- Branching factor: {lore.branching_factor['min']}-{lore.branching_factor['max']} choices per state
- Quest depth: {lore.depth_constraints['min']}-{lore.depth_constraints['max']} steps

Return your response in plain text with ASCII characters inside:
<DOMAIN_PDDL>
[domain content here]
</DOMAIN_PDDL>

<PROBLEM_PDDL>
[problem content here]
</PROBLEM_PDDL>

Pay attention to PDDL syntax. Each PDDL block is encapsulated in ( and ). 
Example: (define (predicate-name ?param) ; Comment describing the predicate)

Here are examples of valid PDDL files:

EXAMPLE DOMAIN:
{example_domain}

EXAMPLE PROBLEM:
{example_problem}

Ensure your generated PDDL:
1. Is syntactically correct
2. Has clear, descriptive comments for each predicate and action
3. Models the quest narrative accurately
4. Includes all necessary objects, predicates, and actions
5. Has a solvable path from initial state to goal
"""
