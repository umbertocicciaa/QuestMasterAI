import json
from pathlib import Path
import subprocess
import logging
from langchain_ollama import OllamaLLM
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")

LORE_PATH = Path("data/lore.json")
NEW_LORE_PATH = Path("data/new_lore.json")
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

def extract_and_save_pddl(response: str) -> None:
    logging.info("Extracting domain and problem PDDL blocks from response...")
    
    try:
        domain_block = response.split("<DOMAIN_PDDL>")[1].split("</DOMAIN_PDDL>")[0].strip()
        problem_block = response.split("<PROBLEM_PDDL>")[1].split("</PROBLEM_PDDL>")[0].strip()
    except Exception:
        logging.error("Failed to extract PDDL blocks from response.")
        return
    
    try:
        lore_block = response.split("<LORE>")[1].split("</LORE>")[0].strip()
    except Exception:
        logging.error("Logging error while extracting Lore blocks.")
        return
    
    DOMAIN_PATH.write_text(domain_block)
    PROBLEM_PATH.write_text(problem_block)
    NEW_LORE_PATH.write_text(lore_block)
    
    logging.info("✅ domain.pddl and problem.pddl generated.")

def reflect_on_invalid_pddl(lore: str, domain_text: str, problem_text: str, llm: OllamaLLM) -> str:
    logging.info("Generating new PDDL using Ollama...")
    prompt = f"""
    Sei un agente riflessivo che aiuta a correggere modelli PDDL. È stato generato il seguente dominio e problema, ma nessun piano valido è stato trovato.

    Analizza i due file PDDL e suggerisci una versione corretta e coerente con la seguente Lore:

    LORE:
    {json.dumps(lore, indent=2)}

    DOMAIN.PDDL ORIGINALE:
    {domain_text}

    PROBLEM.PDDL ORIGINALE:
    {problem_text}

    Usa i delimitatori <DOMAIN_PDDL> e </DOMAIN_PDDL> per il dominio, e <PROBLEM_PDDL> e </PROBLEM_PDDL> per il problema. Utiliza solo i caratteri ASCII standard e non usare caratteri speciali o emoji per la tua risposta.
    (Se necessario) Fornisci una nuova LORE aggiornata dentro il blocco <LORE> e </LORE>.
    """
    response = llm.invoke(prompt)
    logging.info(f"Response from OllamaLLM:\n{response}")
    logging.info("OllamaLLM process completed.")
    return response

def validate_plan(domain_path, problem_path) -> tuple[bool, str]:
    logging.info("Validating plan with Fast Downward...")    
    command = f"python fast-downward-24.06.1/fast-downward.py {domain_path} {problem_path} --search \"astar(blind())\""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = result.stdout + result.stderr
    logging.info(f"Fast Downward output:\n{result.stdout}\n{result.stderr}")
    return "Solution found" in output or "Plan found" in output, result.stderr

if __name__ == "__main__":
    llm = OllamaLLM(model=MODEL_NAME)
    lore = load_lore()
    response = generate_pddl_with_ollama(lore, llm)
    extract_and_save_pddl(response)
    while True:
        valid, validation_output = validate_plan(DOMAIN_PATH, PROBLEM_PATH)
        if valid:
            logging.info("Plan is valid! ✅")
            break
        else:
            logging.warning("Plan is invalid! ❌")
            logging.info("Reflecting on invalid PDDL...")
            new_pddl = reflect_on_invalid_pddl(lore, DOMAIN_PATH.read_text(), PROBLEM_PATH.read_text(),llm)
            extract_and_save_pddl(new_pddl)
            lore = NEW_LORE_PATH.read_text()
