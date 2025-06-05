import json
import logging
import os
import subprocess

from langchain_ollama import OllamaLLM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")

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

llm = OllamaLLM(model=MODEL_NAME)