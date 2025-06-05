import json
import logging
import subprocess

from langchain_ollama import OllamaLLM

from constant import DOMAIN_PATH, MODEL_NAME, PROBLEM_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def reflect_on_invalid_pddl(lore: str, domain_text: str, problem_text: str, validation_output: str, llm: OllamaLLM) -> str:
    logging.info("Generating new PDDL using Ollama...")
    prompt = f"""
    You are a pddl expert that helps correct PDDL models files. The following domain and problem were generated, but no valid plan was found.
    Analyze the two PDDL files and the previous error, and suggest a corrected and consistent version according to the following Lore:

    LORE:
    {json.dumps(lore, indent=2)}

    ORIGINAL DOMAIN.PDDL:
    {domain_text}

    ORIGINAL PROBLEM.PDDL:
    {problem_text}

    PREVIOUS VALIDATION ERROR:
    {validation_output}

    Return yor response like plain text in ASCII character inside 
    <DOMAIN_PDDL> 
    
    </DOMAIN_PDDL> 
    blocks for the domain, 
    and 
    <PROBLEM_PDDL>  
    
    </PROBLEM_PDDL> for the problem.
    
    """
    response = llm.invoke(prompt)
    logging.info(f"Response from OllamaLLM:\n{response}")
    logging.info("OllamaLLM process completed.")
    return response

def validate_plan() -> tuple[bool, str]:
    logging.info("Validating plan with Fast Downward...")    
    domain_path = DOMAIN_PATH
    problem_path = PROBLEM_PATH
    command = f"python fast-downward-24.06.1/fast-downward.py {domain_path} {problem_path} --search \"astar(blind())\""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = result.stdout + result.stderr
    logging.info(f"Fast Downward output:\n{result.stdout}\n{result.stderr}")
    return "Solution found" in output or "Plan found" in output, result.stderr

llm = OllamaLLM(model=MODEL_NAME)