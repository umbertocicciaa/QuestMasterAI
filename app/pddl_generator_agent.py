import json
from pathlib import Path
import logging
from langchain_ollama import OllamaLLM
import os

from utils import extract_and_save_pddl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "codellama:7b")

LORE_PATH = Path("data/lore.json")
DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")

def load_lore() -> str:
    logging.info(f"Loading lore from {LORE_PATH}")
    lore = LORE_PATH.read_text()
    return lore

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