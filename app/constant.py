import os
from pathlib import Path

MODEL_NAME = os.environ.get("CHATGPT_MODEL")

BASE_DIR = Path(__file__).resolve().parent.parent
LORE_PATH = Path(f"{BASE_DIR}/data/lore.json")
NEW_LORE_PATH = Path(f"{BASE_DIR}/data/new_lore.json")
DOMAIN_PATH = Path(f"{BASE_DIR}/data/domain.pddl")
PROBLEM_PATH = Path(f"{BASE_DIR}/data/problem.pddl")
STORY_PATH = Path(f"{BASE_DIR}/data/story.json")
EXAMPLE = Path(f"{BASE_DIR}/resources/story_example.json")
EXAMPLE_DOMAIN = Path(f"{BASE_DIR}/resources/valid_domain.pddl")
EXAMPLE_PROBLEM = Path(f"{BASE_DIR}/resources/valid_problem.pddl")
PLAN_PATH = Path(f"{BASE_DIR}/sas_plan")
FRONTEND_PATH = Path(f"{BASE_DIR}/app/frontend.py")

def load_lore() -> str:
    if LORE_PATH.exists():
        return LORE_PATH.read_text()
    else:
        raise FileNotFoundError(f"Lore file not found at {LORE_PATH}")

def save_lore(lore: str) -> None:
    LORE_PATH.write_text(lore)
    print(f"Lore saved to {LORE_PATH}")

def load_new_lore() -> str:
    if NEW_LORE_PATH.exists():
        return NEW_LORE_PATH.read_text()
    else:
        raise FileNotFoundError(f"New lore file not found at {NEW_LORE_PATH}")

def save_new_lore(lore: str) -> None:
    if not NEW_LORE_PATH.parent.exists():
        NEW_LORE_PATH.parent.mkdir(parents=True)
    NEW_LORE_PATH.write_text(lore)
    print(f"New lore saved to {NEW_LORE_PATH}")

def load_domain() -> str:
    if DOMAIN_PATH.exists():
        return DOMAIN_PATH.read_text()
    else:
        raise FileNotFoundError(f"Domain file not found at {DOMAIN_PATH}")

def save_domain(domain: str) -> None:
    DOMAIN_PATH.write_text(domain)
    print(f"Domain saved to {DOMAIN_PATH}")
    
def load_problem() -> str:
    if PROBLEM_PATH.exists():
        return PROBLEM_PATH.read_text()
    else:
        raise FileNotFoundError(f"Problem file not found at {PROBLEM_PATH}")

def load_plan() -> str:
    if PLAN_PATH.exists():
        return PLAN_PATH.read_text()
    else:
        raise FileNotFoundError(f"Plan file not found at {PLAN_PATH}")

def save_problem(problem: str) -> None:
    PROBLEM_PATH.write_text(problem)
    print(f"Problem saved to {PROBLEM_PATH}")

def load_story() -> str:
    if STORY_PATH.exists():
        return STORY_PATH.read_text()
    else:
        raise FileNotFoundError(f"Story file not found at {STORY_PATH}")
    
def save_story(story: str) -> None:
    STORY_PATH.write_text(story)
    print(f"Story saved to {STORY_PATH}")

def load_example() -> str:
    if EXAMPLE.exists():
        return EXAMPLE.read_text()
    else:
        raise FileNotFoundError(f"Example file not found at {EXAMPLE}")

def load_example_domain() -> str:
    if EXAMPLE_DOMAIN.exists():
        return EXAMPLE_DOMAIN.read_text()
    else:
        raise FileNotFoundError(f"Example file not found at {EXAMPLE_DOMAIN}")
    
def load_example_problem() -> str:
    if EXAMPLE_PROBLEM.exists():
        return EXAMPLE_PROBLEM.read_text()
    else:
        raise FileNotFoundError(f"Example file not found at {EXAMPLE_PROBLEM}")

def get_model_name() -> str:
    if MODEL_NAME:
        return MODEL_NAME
    else:
        raise ValueError("MODEL_NAME environment variable is not set. Please set it to the desired model name.")
    
def save_frontend(frontend: str) -> None:
    FRONTEND_PATH.write_text(frontend)
    print(f"Frontend saved to {FRONTEND_PATH}")