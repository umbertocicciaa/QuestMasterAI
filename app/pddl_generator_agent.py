import json
import logging
from langchain_ollama import OllamaLLM

from constant import MODEL_NAME, load_domain, load_lore, load_new_lore, load_problem
from reflect_agent import reflect_on_invalid_pddl, validate_plan
from utils import extract_and_save_pddl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def generate_pddl_with_ollama(lore: str, llm: OllamaLLM) -> str:
    logging.info("Generating PDDL using Ollama...")
    prompt = f"""
    Sei un modellatore PDDL. Data questa descrizione di una quest, genera:
    1. Un file DOMAIN.PDDL con predicati e azioni, ciascuna con commenti.
    2. Un file PROBLEM.PDDL con lo stato iniziale e goal coerente con il dominio.
    
    Lore:
    {json.dumps(lore, indent=2)}
    
    Usa i delimitatori <DOMAIN_PDDL> e </DOMAIN_PDDL> per il dominio, e <PROBLEM_PDDL> e </PROBLEM_PDDL> per il problema. Utiliza solo i caratteri ASCII standard e non usare caratteri speciali o emoji per la tua risposta.
    """
    response = llm.invoke(prompt)
    logging.info("OllamLLM process completed.")
    logging.info(f"Response: {response}")
    return response 

llm = OllamaLLM(model=MODEL_NAME)
lore = load_lore()
response = generate_pddl_with_ollama(lore, llm)
extract_and_save_pddl(response)

while True:
    valid, validation_output = validate_plan()
    if valid:
        logging.info("Plan is valid! ✅")
        break
    else:
        logging.warning("Plan is invalid! ❌")
        logging.info("Reflecting on invalid PDDL...")
        new_pddl = reflect_on_invalid_pddl(lore, load_domain(), load_problem(), llm)
        extract_and_save_pddl(new_pddl)
        lore = load_new_lore()