"""Reflection agent for fixing PDDL issues."""

from typing import Tuple

from ..core.exceptions import LLMError, PDDLError
from ..core.logging import get_logger
from ..models import Lore, PDDLDomain, PDDLProblem, ValidationResult
from ..services import FileService, LLMService

logger = get_logger(__name__)


class ReflectionAgent:
    """Agent for reflecting on and fixing PDDL validation issues."""
    
    def __init__(
        self,
        llm_service: LLMService,
        file_service: FileService,
    ) -> None:
        """Initialize reflection agent.
        
        Args:
            llm_service: LLM service instance
            file_service: File service instance
        """
        self.llm_service = llm_service
        self.file_service = file_service

    def reflect_and_fix(
        self,
        lore: Lore,
        domain: PDDLDomain,
        problem: PDDLProblem,
        validation_result: ValidationResult,
    ) -> Tuple[PDDLDomain, PDDLProblem]:
        """Reflect on validation errors and generate fixed PDDL.
        
        Args:
            lore: Original quest lore
            domain: Current domain
            problem: Current problem
            validation_result: Validation failure details
            
        Returns:
            Tuple of (fixed_domain, fixed_problem)
            
        Raises:
            PDDLError: If reflection/fixing fails
        """
        logger.info(
            "Reflecting on PDDL validation errors",
            error=validation_result.error_message,
        )
        
        try:
            # Load example files for context
            example_domain = self.file_service.load_example_domain()
            example_problem = self.file_service.load_example_problem()
            
            # Create reflection prompt
            prompt = self._create_reflection_prompt(
                lore,
                domain,
                problem,
                validation_result,
                example_domain,
                example_problem,
            )
            
            # Generate fixed PDDL
            response = self.llm_service.generate_completion(prompt)
            
            # Extract fixed PDDL blocks
            domain_content, problem_content = self.llm_service.extract_pddl_blocks(response)
            
            if not domain_content or not problem_content:
                raise PDDLError("Failed to extract fixed PDDL blocks from LLM response")
            
            # Create fixed PDDL objects
            fixed_domain = PDDLDomain(
                name=domain.name,
                content=domain_content,
            )
            
            fixed_problem = PDDLProblem(
                name=problem.name,
                domain=problem.domain,
                content=problem_content,
            )
            
            logger.info("PDDL reflection and fixing completed successfully")
            return fixed_domain, fixed_problem
            
        except LLMError as e:
            logger.error("LLM error during PDDL reflection", error=str(e))
            raise PDDLError(f"Failed to fix PDDL: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during PDDL reflection", error=str(e))
            raise PDDLError(f"Unexpected error in PDDL reflection: {e}") from e

    def _create_reflection_prompt(
        self,
        lore: Lore,
        domain: PDDLDomain,
        problem: PDDLProblem,
        validation_result: ValidationResult,
        example_domain: str,
        example_problem: str,
    ) -> str:
        """Create prompt for PDDL reflection and fixing.
        
        Args:
            lore: Original quest lore
            domain: Current domain
            problem: Current problem
            validation_result: Validation failure details
            example_domain: Example domain content
            example_problem: Example problem content
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a PDDL expert that helps correct PDDL model files. The following domain and problem were generated, but validation failed with Fast Downward.

Analyze the PDDL files and the validation error, then provide corrected and consistent versions according to the original quest requirements.

ORIGINAL QUEST REQUIREMENTS:
Title: {lore.title}
Description: {lore.description}
Initial State: {lore.initial_state}
Goal: {lore.goal}
World Context: {lore.world_context}
Characters: {', '.join(lore.characters)}
Locations: {', '.join(lore.locations)}
Items: {', '.join(lore.items)}
Obstacles: {', '.join(lore.obstacles)}

CURRENT DOMAIN.PDDL:
{domain.content}

CURRENT PROBLEM.PDDL:
{problem.content}

VALIDATION ERROR:
{validation_result.error_message}

ANALYSIS INSTRUCTIONS:
1. Identify the specific issues causing the validation failure
2. Check for syntax errors, missing predicates, inconsistent object names
3. Ensure the initial state is properly defined
4. Verify that the goal is achievable with the available actions
5. Make sure all predicates used in actions are defined in the domain
6. Ensure object types are consistent between domain and problem

Return the corrected PDDL files in plain text with ASCII characters inside:
<DOMAIN_PDDL>
[corrected domain content here]
</DOMAIN_PDDL>

<PROBLEM_PDDL>
[corrected problem content here]
</PROBLEM_PDDL>

Pay attention to PDDL syntax. Each PDDL block is encapsulated in ( and ).
Example: (define (predicate-name ?param) ; Comment describing the predicate)

Here are examples of valid PDDL files for reference:

EXAMPLE DOMAIN:
{example_domain}

EXAMPLE PROBLEM:
{example_problem}

Ensure your corrected PDDL:
1. Fixes the specific validation errors
2. Maintains the original quest narrative
3. Is syntactically correct
4. Has a solvable path from initial state to goal
5. Includes clear comments explaining the fixes made
"""
