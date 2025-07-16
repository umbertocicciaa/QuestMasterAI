"""LLM service for OpenAI interactions."""

import re
from typing import Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_settings
from ..core.exceptions import LLMError
from ..core.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions."""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize LLM service.
        
        Args:
            api_key: Optional OpenAI API key override
        """
        self.settings = get_settings()
        self.client = OpenAI(
            api_key=api_key or self.settings.openai_api_key,
            timeout=self.settings.openai_timeout,
            max_retries=self.settings.openai_max_retries,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate completion from LLM.
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated completion text
            
        Raises:
            LLMError: If completion fails
        """
        try:
            logger.info("Generating LLM completion", model=model or self.settings.chatgpt_model)
            
            response = self.client.chat.completions.create(
                model=model or self.settings.chatgpt_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if not response.choices:
                raise LLMError("No response choices returned from LLM")
            
            content = response.choices[0].message.content
            if not content:
                raise LLMError("Empty response content from LLM")
            
            logger.info("LLM completion generated successfully")
            return content
            
        except Exception as e:
            logger.error("Failed to generate LLM completion", error=str(e))
            raise LLMError(f"Failed to generate completion: {e}") from e

    def extract_xml_blocks(self, text: str, tag: str) -> list[str]:
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

    def extract_pddl_blocks(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Extract PDDL domain and problem blocks from text.
        
        Args:
            text: Text containing PDDL blocks
            
        Returns:
            Tuple of (domain_content, problem_content)
        """
        domain_blocks = self.extract_xml_blocks(text, "DOMAIN_PDDL")
        problem_blocks = self.extract_xml_blocks(text, "PROBLEM_PDDL")
        
        domain = domain_blocks[0] if domain_blocks else None
        problem = problem_blocks[0] if problem_blocks else None
        
        return domain, problem

    def extract_frontend_code(self, text: str) -> Optional[str]:
        """Extract frontend code from text.
        
        Args:
            text: Text containing frontend code
            
        Returns:
            Extracted frontend code or None
        """
        code_blocks = self.extract_xml_blocks(text, "FRONTEND_CODE")
        return code_blocks[0] if code_blocks else None

    def extract_lore_content(self, text: str) -> Optional[str]:
        """Extract lore content from text.
        
        Args:
            text: Text containing lore content
            
        Returns:
            Extracted lore content or None
        """
        lore_blocks = self.extract_xml_blocks(text, "LORE")
        return lore_blocks[0] if lore_blocks else None

    def extract_json_blocks(self, text: str) -> list[str]:
        """Extract JSON content from markdown code blocks.
        
        Args:
            text: Text containing markdown JSON blocks
            
        Returns:
            List of extracted JSON content blocks
        """
        # Pattern to match ```json ... ``` or ``` ... ``` blocks
        patterns = [
            r"```json\s*(.*?)\s*```",  # ```json ... ```
            r"```\s*(.*?)\s*```",      # ``` ... ```
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return [match.strip() for match in matches]
        
        return []
