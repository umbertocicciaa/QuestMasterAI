from pathlib import Path
import subprocess
import logging
import ollama
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

MODEL_NAME = os.environ.get("OLLAMA_MODEL", "llama3")

LORE_PATH = Path("data/lore.json")
DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")

def load_lore() -> str:
    logging.info(f"Loading lore from {LORE_PATH}")
    lore = LORE_PATH.read_text()
    logging.info(f"Lore loaded successfully. {lore}")
    return lore

def generate_pddl_with_ollama(lore: str) -> str:
    logging.info("Generating PDDL using Ollama...")
    prompt = f"""
    You are a Fast downard PDDL expert. Based on the following fantasy quest lore,
    generate a complete PDDL domain and problem file. Do not add any other comments.

    LORE:
    {lore}

    Output the domain and problem files one after the other using these delimiters:

    <DOMAIN_PDDL>
       ...domain text here...
    </DOMAIN_PDDL>
    
    <PROBLEM_PDDL>
       ...problem text here...
    </PROBLEM_PDDL>
    
    """
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    logging.info("OllamLLM process completed.")
    logging.info(f"Response: {response}")
    return response["message"]["content"]   

def extract_and_save_pddl(response: str) -> None:
    logging.info("Extracting domain and problem PDDL blocks from response...")
    
    try:
        domain_block = response.split("<DOMAIN_PDDL>")[1].split("</DOMAIN_PDDL>")[0].strip()
        problem_block = response.split("<PROBLEM_PDDL>")[1].split("</PROBLEM_PDDL>")[0].strip()
    except Exception as e:
        logging.error("Failed to extract PDDL blocks from response.")
        raise e
    
    DOMAIN_PATH.write_text(domain_block)
    PROBLEM_PATH.write_text(problem_block)
    
    logging.info("✅ domain.pddl and problem.pddl generated.")

def reflect_on_invalid_pddl(lore: str, domain_text: str, problem_text: str, validation_output:str) -> str:
    logging.info("Generating new PDDL using Ollama...")
    prompt = f"""You are a PDDL expert. The following domain and problem did NOT produce a plan:

                 Domain:
                 {domain_text}
                 
                 Problem:
                 {problem_text}
                 
                 This is the output from Fast Downward:
                 {validation_output}
                 
                 The lore is:
                 {lore}
                 
                 Reflect on the lore and the PDDL files, and generate a new domain and problem that should produce a valid plan.                 
                 Output the domain and problem files one after the other using these delimiters:

                 <DOMAIN_PDDL>
                    ...domain text here...
                 </DOMAIN_PDDL>
             
                 <PROBLEM_PDDL>
                    ...problem text here...
                 </PROBLEM_PDDL>
                 
              """
    result = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    logging.info(f"Response from OllamaLLM:\n{result}")
    logging.info("OllamaLLM process completed.")
    return result["message"]["content"]

def validate_plan(domain_path, problem_path) -> tuple[bool, str]:
    logging.info("Validating plan with Fast Downward...")    
    command = f"python fast-downward-24.06.1/fast-downward.py {domain_path} {problem_path} --search \"astar(blind())\""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = result.stdout + result.stderr
    logging.info(f"Fast Downward output:\n{result.stdout}\n{result.stderr}")
    return "Solution found" in output or "Plan found" in output, result.stderr

if __name__ == "__main__":
    lore = load_lore()
    response = generate_pddl_with_ollama(lore)
    extract_and_save_pddl(response)
    while True:
        valid, validation_output = validate_plan(DOMAIN_PATH, PROBLEM_PATH)
        if valid:
            logging.info("Plan is valid! ✅")
            break
        else:
            logging.warning("Plan is invalid! ❌")
            logging.info("Reflecting on invalid PDDL...")
            new_pddl = reflect_on_invalid_pddl(lore, DOMAIN_PATH.read_text(), PROBLEM_PATH.read_text(), validation_output)
            extract_and_save_pddl(new_pddl)
