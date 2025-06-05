import os
from pathlib import Path

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "codellama:7b")

LORE_PATH = Path("data/lore.json")
NEW_LORE_PATH = Path("data/new_lore.json")
DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")
STORY_PATH = Path("data/story.json")
EXAMPLE = Path("data/example_structure.json")

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