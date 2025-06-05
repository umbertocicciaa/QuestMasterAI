import logging
import json, re, ollama

from constant import MODEL_NAME, load_domain, load_example, load_lore, load_problem, save_lore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

lore = json.loads(load_lore())
domain = load_domain()
problem = load_problem()
example_structure = load_example()


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

save_lore(json.dumps(story, indent=2))
print("story.json generato.")