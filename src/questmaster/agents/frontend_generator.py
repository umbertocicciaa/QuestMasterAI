"""Frontend generator agent."""

import ast
import subprocess
import sys
import tempfile
from typing import Tuple

from ..core.exceptions import LLMError, StoryError
from ..core.logging import get_logger
from ..models import StoryGraph
from ..services import FileService, LLMService

logger = get_logger(__name__)


class FrontendGeneratorAgent:
    """Agent for generating Streamlit frontend from story."""
    
    def __init__(
        self,
        llm_service: LLMService,
        file_service: FileService,
    ) -> None:
        """Initialize frontend generator agent.
        
        Args:
            llm_service: LLM service instance
            file_service: File service instance
        """
        self.llm_service = llm_service
        self.file_service = file_service

    def generate_frontend(self, story: StoryGraph) -> str:
        """Generate Streamlit frontend code from story.
        
        Args:
            story: Story graph to generate frontend for
            
        Returns:
            Generated frontend code
            
        Raises:
            StoryError: If frontend generation fails
        """
        logger.info("Generating Streamlit frontend", title=story.title)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Create frontend generation prompt
                prompt = self._create_frontend_prompt(story)
                
                # Generate frontend code
                response = self.llm_service.generate_completion(prompt)
                
                # Extract frontend code
                frontend_code = self.llm_service.extract_frontend_code(response)
                
                if not frontend_code:
                    raise StoryError("Failed to extract frontend code from LLM response")
                
                # Validate syntax
                is_valid, error_message = self._validate_python_syntax(frontend_code)
                
                if is_valid:
                    logger.info("Frontend generation completed successfully")
                    return frontend_code
                else:
                    logger.warning(
                        f"Frontend syntax validation failed (attempt {attempt + 1}/{max_attempts})",
                        error=error_message,
                    )
                    
                    if attempt < max_attempts - 1:
                        # Try to fix the syntax errors
                        frontend_code = self._fix_syntax_errors(frontend_code, error_message)
                        is_valid, _ = self._validate_python_syntax(frontend_code)
                        
                        if is_valid:
                            logger.info("Frontend syntax fixed successfully")
                            return frontend_code
                
            except LLMError as e:
                logger.error(f"LLM error during frontend generation (attempt {attempt + 1})", error=str(e))
                if attempt == max_attempts - 1:
                    raise StoryError(f"Failed to generate frontend: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error during frontend generation (attempt {attempt + 1})", error=str(e))
                if attempt == max_attempts - 1:
                    raise StoryError(f"Unexpected error in frontend generation: {e}") from e
        
        raise StoryError(f"Failed to generate valid frontend after {max_attempts} attempts")

    def _create_frontend_prompt(self, story: StoryGraph) -> str:
        """Create prompt for frontend generation.
        
        Args:
            story: Story graph
            
        Returns:
            Formatted prompt string
        """
        return f"""You are a Senior Streamlit frontend expert. Create a beautiful, interactive web interface for the following interactive story game.

STORY INFORMATION:
Title: {story.title}
Description: {story.description}
Number of states: {len(story.states)}
Initial state: {story.initial_state}

STORY DATA:
{story.model_dump_json(indent=2)}

REQUIREMENTS:
1. Create a modern, beautiful UI using Streamlit
2. Use session state to track current story state
3. Display story text in an engaging way
4. Show action choices as buttons or selectbox
5. Handle state transitions properly
6. Include a reset/restart option
7. Show progress or breadcrumbs if possible
8. Use proper error handling
9. Make it responsive and user-friendly
10. Don't use deprecated Streamlit methods

FEATURES TO INCLUDE:
- Story title and description at the top
- Current story text in a nice container
- Action buttons that are clearly labeled
- Visual feedback for choices
- Game state management
- Restart functionality
- Maybe a sidebar with game info

Return the complete Streamlit code inside these tags:
<FRONTEND_CODE>
[Complete Streamlit application code here]
</FRONTEND_CODE>

The code should be production-ready, well-commented, and use modern Streamlit features. Make it engaging and polished!
"""

    def _validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python syntax of the generated code.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse the code to check syntax
            ast.parse(code)
            
            # Try to compile it
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file.flush()
                
                result = subprocess.run(
                    [sys.executable, '-m', 'py_compile', temp_file.name],
                    capture_output=True,
                    text=True,
                )
                
                if result.returncode == 0:
                    return True, ""
                else:
                    return False, result.stderr
                    
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _fix_syntax_errors(self, code: str, error_message: str) -> str:
        """Attempt to fix syntax errors in the code.
        
        Args:
            code: Code with syntax errors
            error_message: Error message from validation
            
        Returns:
            Potentially fixed code
        """
        logger.info("Attempting to fix syntax errors using LLM")
        
        fix_prompt = f"""You are a Python syntax expert. The following Streamlit code has syntax errors. Please fix them and return only the corrected code.

Error message:
{error_message}

Code with errors:
{code}

Return the corrected code inside <FIXED_CODE> tags:
<FIXED_CODE>
[corrected code here]
</FIXED_CODE>

Rules:
- Fix only syntax errors, don't change the logic
- Ensure the code is valid Python and Streamlit
- Don't use deprecated Streamlit methods
- Return only the corrected code without explanations
"""
        
        try:
            response = self.llm_service.generate_completion(fix_prompt)
            fixed_blocks = self.llm_service.extract_xml_blocks(response, "FIXED_CODE")
            
            if fixed_blocks:
                logger.info("Code syntax fixed by LLM")
                return fixed_blocks[0]
            else:
                logger.warning("LLM could not extract fixed code blocks")
                return code
                
        except Exception as e:
            logger.error("Failed to fix syntax errors with LLM", error=str(e))
            return code
