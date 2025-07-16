"""PDDL planner service using Fast Downward."""

import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple

from ..core.config import get_settings
from ..core.exceptions import PlannerError, ValidationError
from ..core.logging import get_logger
from ..models import ValidationResult

logger = get_logger(__name__)


class PlannerService:
    """Service for PDDL planning using Fast Downward."""
    
    def __init__(self) -> None:
        """Initialize planner service."""
        self.settings = get_settings()
        self.fast_downward_path = self.settings.fast_downward_path
        
        if not self.fast_downward_path or not self.fast_downward_path.exists():
            raise PlannerError(f"Fast Downward not found at {self.fast_downward_path}")

    def validate_pddl(
        self,
        domain_path: Path,
        problem_path: Path,
        search_algorithm: str = "astar(blind())",
        timeout: Optional[int] = None,
    ) -> ValidationResult:
        """Validate PDDL files and find a solution.
        
        Args:
            domain_path: Path to domain PDDL file
            problem_path: Path to problem PDDL file
            search_algorithm: Search algorithm to use
            timeout: Timeout in seconds
            
        Returns:
            ValidationResult with success status and details
        """
        timeout = timeout or self.settings.fast_downward_timeout
        
        logger.info(
            "Validating PDDL with Fast Downward",
            domain=str(domain_path),
            problem=str(problem_path),
            algorithm=search_algorithm,
        )
        
        start_time = time.time()
        
        try:
            # Check if files exist
            if not domain_path.exists():
                raise ValidationError(f"Domain file not found: {domain_path}")
            if not problem_path.exists():
                raise ValidationError(f"Problem file not found: {problem_path}")
            
            # Check Fast Downward path
            if not self.fast_downward_path:
                raise PlannerError("Fast Downward path not configured")
            
            # Construct Fast Downward command
            fd_script = self.fast_downward_path / "fast-downward.py"
            command = [
                "python3",
                str(fd_script),
                str(domain_path),
                str(problem_path),
                "--search",
                search_algorithm,
            ]
            
            logger.debug("Running Fast Downward command", command=" ".join(command))
            
            # Run Fast Downward
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.settings.base_dir,
            )
            
            execution_time = time.time() - start_time
            
            # Parse output
            stdout = result.stdout
            stderr = result.stderr
            combined_output = f"{stdout}\\n{stderr}"
            
            logger.debug(
                "Fast Downward completed",
                return_code=result.returncode,
                execution_time=execution_time,
            )
            
            # Check for solution
            has_solution = any(
                phrase in combined_output.lower()
                for phrase in ["solution found", "plan found", "search successful"]
            )
            
            # Check for validation errors
            is_valid = result.returncode == 0 or has_solution
            
            # Extract plan if available
            plan = self._extract_plan(combined_output) if has_solution else None
            
            # Determine error message
            error_message = ""
            if not is_valid:
                error_message = self._extract_error_message(stderr, stdout)
            
            return ValidationResult(
                is_valid=is_valid,
                has_solution=has_solution,
                error_message=error_message,
                plan=plan,
                execution_time=execution_time,
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.warning("Fast Downward timeout", timeout=timeout)
            return ValidationResult(
                is_valid=False,
                has_solution=False,
                error_message=f"Fast Downward timeout after {timeout} seconds",
                plan=None,
                execution_time=execution_time,
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Fast Downward execution failed", error=str(e))
            return ValidationResult(
                is_valid=False,
                has_solution=False,
                error_message=f"Fast Downward execution failed: {e}",
                plan=None,
                execution_time=execution_time,
            )

    def _extract_plan(self, output: str) -> Optional[List[str]]:
        """Extract plan from Fast Downward output.
        
        Args:
            output: Fast Downward output text
            
        Returns:
            List of plan actions or None if no plan found
        """
        plan_actions = []
        
        # Look for plan in output
        lines = output.split("\\n")
        in_plan = False
        
        for line in lines:
            line = line.strip()
            
            if "solution found" in line.lower() or "plan:" in line.lower():
                in_plan = True
                continue
                
            if in_plan:
                if line.startswith("(") and line.endswith(")"):
                    plan_actions.append(line)
                elif line == "" or "plan length" in line.lower():
                    break
        
        # Also try to read from sas_plan file if it exists
        sas_plan_path = self.settings.plan_path
        if sas_plan_path.exists():
            try:
                plan_content = sas_plan_path.read_text(encoding="utf-8")
                if plan_content.strip():
                    sas_actions = [
                        line.strip() for line in plan_content.split("\\n")
                        if line.strip() and not line.strip().startswith(";")
                    ]
                    if sas_actions:
                        plan_actions.extend(sas_actions)
            except Exception:
                pass  # Ignore errors reading sas_plan
        
        return plan_actions if plan_actions else None

    def _extract_error_message(self, stderr: str, stdout: str) -> str:
        """Extract meaningful error message from Fast Downward output.
        
        Args:
            stderr: Standard error output
            stdout: Standard output
            
        Returns:
            Extracted error message
        """
        # Common error patterns
        error_patterns = [
            "error:",
            "syntax error",
            "parse error",
            "unsolvable",
            "no solution",
            "invalid",
            "failed",
        ]
        
        # Check stderr first
        for line in stderr.split("\\n"):
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in error_patterns):
                return line.strip()
        
        # Check stdout
        for line in stdout.split("\\n"):
            line_lower = line.lower()
            if any(pattern in line_lower for pattern in error_patterns):
                return line.strip()
        
        # Return full stderr if no specific error found
        return stderr.strip() if stderr.strip() else "Unknown error"

    def check_fast_downward_installation(self) -> bool:
        """Check if Fast Downward is properly installed.
        
        Returns:
            True if Fast Downward is available, False otherwise
        """
        try:
            if not self.fast_downward_path:
                return False
                
            fd_script = self.fast_downward_path / "fast-downward.py"
            if not fd_script.exists():
                return False
            
            # Try to run Fast Downward with help flag
            result = subprocess.run(
                ["python3", str(fd_script), "--help"],
                capture_output=True,
                timeout=10,
            )
            
            return result.returncode == 0
            
        except Exception:
            return False
