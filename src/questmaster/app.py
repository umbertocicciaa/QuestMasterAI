"""Main QuestMaster AI application."""

from typing import Optional

from .agents import (
    FrontendGeneratorAgent,
    PDDLGeneratorAgent,
    ReflectionAgent,
    StoryGeneratorAgent,
)
from .core.config import get_settings
from .core.exceptions import PDDLError, QuestMasterError, ValidationError
from .core.logging import get_logger, setup_logging
from .models import Lore, ValidationResult
from .services import FileService, LLMService, PlannerService

logger = get_logger(__name__)


class QuestMasterApp:
    """Main QuestMaster AI application."""
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize QuestMaster application.
        
        Args:
            api_key: Optional OpenAI API key override
        """
        self.settings = get_settings()
        
        # Initialize services
        self.file_service = FileService()
        self.llm_service = LLMService(api_key)
        self.planner_service = PlannerService()
        
        # Initialize agents
        self.pddl_generator = PDDLGeneratorAgent(self.llm_service, self.file_service)
        self.reflection_agent = ReflectionAgent(self.llm_service, self.file_service)
        self.story_generator = StoryGeneratorAgent(self.llm_service, self.file_service)
        self.frontend_generator = FrontendGeneratorAgent(self.llm_service, self.file_service)

    def run_phase1(self, lore_path: Optional[str] = None) -> ValidationResult:
        """Run Phase 1: Story Generation with PDDL validation.
        
        Args:
            lore_path: Optional path to lore file
            
        Returns:
            Final validation result
            
        Raises:
            QuestMasterError: If Phase 1 fails
        """
        logger.info("Starting Phase 1: Story Generation")
        
        try:
            # Load lore
            if lore_path:
                from pathlib import Path
                lore = self.file_service.load_lore(Path(lore_path))
            else:
                lore = self.file_service.load_lore()
            
            logger.info("Loaded quest lore", title=lore.title)
            
            # Generate initial PDDL
            domain, problem = self.pddl_generator.generate_pddl(lore)
            
            # Save initial PDDL files
            self.file_service.save_domain(domain)
            self.file_service.save_problem(problem)
            
            # Validation and refinement loop
            max_iterations = 5
            iteration = 0
            validation_result = None
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Validation iteration {iteration}/{max_iterations}")
                
                # Validate PDDL
                validation_result = self.planner_service.validate_pddl(
                    self.settings.domain_path,
                    self.settings.problem_path,
                )
                
                if validation_result.success:
                    logger.info("PDDL validation successful! ✅")
                    return validation_result
                else:
                    logger.warning(
                        "PDDL validation failed ❌",
                        error=validation_result.error_message,
                        iteration=iteration,
                    )
                    
                    if iteration < max_iterations:
                        # Use reflection agent to fix issues
                        logger.info("Attempting to fix PDDL issues...")
                        domain, problem = self.reflection_agent.reflect_and_fix(
                            lore, domain, problem, validation_result
                        )
                        
                        # Save fixed PDDL files
                        self.file_service.save_domain(domain)
                        self.file_service.save_problem(problem)
                    else:
                        logger.error("Maximum validation iterations reached")
                        break
            
            # If we get here, validation failed after all attempts
            last_error = validation_result.error_message if validation_result else "Unknown error"
            raise ValidationError(
                f"PDDL validation failed after {max_iterations} iterations. "
                f"Last error: {last_error}"
            )
            
        except Exception as e:
            logger.error("Phase 1 failed", error=str(e))
            if isinstance(e, QuestMasterError):
                raise
            else:
                raise QuestMasterError(f"Phase 1 execution failed: {e}") from e

    def run_phase2(self) -> None:
        """Run Phase 2: Interactive Story Game generation.
        
        Raises:
            QuestMasterError: If Phase 2 fails
        """
        logger.info("Starting Phase 2: Interactive Story Game")
        
        try:
            # Try to load existing story first
            try:
                story = self.file_service.load_story()
                logger.info("Loaded existing story from file", states=len(story.states))
            except Exception:
                logger.info("No existing story found, generating new story")
                
                # Load necessary files for story generation
                lore = self.file_service.load_lore()
                domain = self.file_service.load_domain()
                problem = self.file_service.load_problem()
                
                # Load plan if available
                try:
                    plan_content = self.file_service.load_plan()
                    plan = [line.strip() for line in plan_content.split('\\n') if line.strip()]
                except Exception:
                    logger.warning("No plan file found, generating story without plan")
                    plan = []
                
                # Generate story
                story = self.story_generator.generate_story(lore, domain, problem, plan)
                
                # Save the generated story
                self.file_service.save_story(story)
                logger.info("Story generated and saved", states=len(story.states))
            
            # Generate frontend from the story
            frontend_code = self.frontend_generator.generate_frontend(story)
            
            # Save frontend
            self.file_service.save_frontend(frontend_code)
            logger.info("Frontend generated and saved")
            
            logger.info("Phase 2 completed successfully! ✅")
            
        except Exception as e:
            logger.error("Phase 2 failed", error=str(e))
            if isinstance(e, QuestMasterError):
                raise
            else:
                raise QuestMasterError(f"Phase 2 execution failed: {e}") from e

    def run_full_pipeline(self, lore_path: Optional[str] = None) -> None:
        """Run the complete QuestMaster pipeline.
        
        Args:
            lore_path: Optional path to lore file
            
        Raises:
            QuestMasterError: If pipeline fails
        """
        logger.info("Starting QuestMaster AI full pipeline")
        
        try:
            # Run Phase 1
            validation_result = self.run_phase1(lore_path)
            logger.info("Phase 1 completed successfully")
            
            # Run Phase 2
            self.run_phase2()
            logger.info("Phase 2 completed successfully")
            
            logger.info("QuestMaster AI pipeline completed successfully! 🎉")
            
        except Exception as e:
            logger.error("QuestMaster pipeline failed", error=str(e))
            raise

    def check_requirements(self) -> bool:
        """Check if all requirements are met.
        
        Returns:
            True if all requirements are met, False otherwise
        """
        logger.info("Checking QuestMaster requirements")
        
        issues = []
        
        # Check OpenAI API key
        if not self.settings.openai_api_key:
            issues.append("OpenAI API key not configured")
        
        # Check Fast Downward installation
        if not self.planner_service.check_fast_downward_installation():
            issues.append("Fast Downward not properly installed")
        
        # Check required directories
        if not self.settings.data_dir.exists():
            issues.append(f"Data directory not found: {self.settings.data_dir}")
        
        if not self.settings.resources_dir.exists():
            issues.append(f"Resources directory not found: {self.settings.resources_dir}")
        
        # Check required example files
        if not self.settings.example_domain_path.exists():
            issues.append(f"Example domain file not found: {self.settings.example_domain_path}")
        
        if not self.settings.example_problem_path.exists():
            issues.append(f"Example problem file not found: {self.settings.example_problem_path}")
        
        if issues:
            logger.error("Requirements check failed", issues=issues)
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info("All requirements satisfied ✅")
            return True


def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging(log_level="INFO", debug=False)
    
    try:
        # Create and run application
        app = QuestMasterApp()
        
        # Check requirements
        if not app.check_requirements():
            logger.error("Requirements not met. Please check the issues above.")
            return
        
        # Run full pipeline
        app.run_full_pipeline()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
