from pathlib import Path
import logging
from langchain_ollama import OllamaLLM

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


LORE_PATH = Path("data/lore.md")
DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")

def load_lore() -> str:
    logging.info(f"Loading lore from {LORE_PATH}")
    return LORE_PATH.read_text()

def generate_pddl_with_ollama(lore: str, llm: OllamaLLM) -> str:
    logging.info("Generating PDDL using Ollama...")
    prompt = f"""
    You are a PDDL expert. Based on the following fantasy quest lore,
    generate a complete PDDL domain and problem file that defines:
    - Initial state (as per the quest)
    - Goal: reunite 5 fragments and perform a ritual
    - Logical actions (travel, ally, retrieve, betray, etc.)
    - Objects: characters, locations, artifacts

    Add human-readable comments above each block to explain what it does.

    LORE:
    {lore}

    Output the domain and problem files one after the other, like:

    ```domain.pddl
    
    ```
    ```problem.pddl
    
    ```
    """
    response = llm.invoke(prompt)
    logging.info("OllamLLM process completed.")
    return response

def extract_and_save_pddl(response: str) -> None:
    logging.info("Extracting domain and problem PDDL blocks from response...")
    
    domain_start = response.find("```domain.pddl")
    problem_start = response.find("```problem.pddl")
    
    if domain_start == -1 or problem_start == -1:
        logging.error("Could not find PDDL code blocks in the response.")
        return

    domain_code = response[domain_start + len("```domain.pddl"):problem_start]
    domain_code = domain_code.split("```")[0].strip()
    
    problem_code = response[problem_start + len("```problem.pddl"):]
    problem_code = problem_code.split("```")[0].strip()

    DOMAIN_PATH.write_text(domain_code)
    PROBLEM_PATH.write_text(problem_code)
    
    logging.info("✅ domain.pddl and problem.pddl generated.")

if __name__ == "__main__":
    llm = OllamaLLM(model="llama3.2")
    try:
        lore = load_lore()
        response = generate_pddl_with_ollama(lore, llm)
        extract_and_save_pddl(response)
    finally:
        logging.info("OllamLLM model destroyed.")
