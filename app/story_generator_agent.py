import logging
from pathlib import Path
import json, re, ollama, os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")

LORE_PATH = Path("data/lore.json")
DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")
STORY_PATH = Path("data/story.json")
EXAMPLE = Path("data/example_structure.json")

lore = json.loads(LORE_PATH.read_text(encoding="utf-8"))
domain = DOMAIN_PATH.read_text(encoding="utf-8")
problem = PROBLEM_PATH.read_text(encoding="utf-8")
example_structure = EXAMPLE.read_text(encoding="utf-8")


prompt = f"""Sei uno storyteller interattivo.
Dati questi file PDDL e questa lore, crea una rappresentazione JSON della storia come macchina a stati finiti (FSM). 

Lore: {json.dumps(lore, indent=2)}

DOMAIN.PDDL:
{domain}

PROBLEM.PDDL:
{problem}

Genera uno story.json con la seguente struttura e niente altro. Fai riferimento ad una struttura esempio rendendola più originale e dinamica:
STRUTTURA ESEMPIO:
{example_structure}
"""

response = ollama.chat(model=MODEL_NAME, messages=[{"role":"user","content":prompt}])

json_text = re.search(r"\{[\s\S]*\}", response['message']['content']).group(0)
story = json.loads(json_text)

STORY_PATH.write_text(json.dumps(story, indent=2), encoding="utf-8")
print("story.json generato.")