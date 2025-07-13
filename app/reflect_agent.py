import logging
import subprocess

from openai import OpenAI

from constant import BASE_DIR, DOMAIN_PATH, PROBLEM_PATH, get_model_name, load_example_domain, load_example_problem

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def reflect_on_invalid_pddl(lore: str, domain_text: str, problem_text: str, validation_output: str, client: OpenAI) -> str:
    logging.info("Generating new PDDL...")
    prompt = f"""
    You are a pddl expert that helps correct PDDL models files. The following domain and problem were generated, but no valid plan was found.
    Analyze the two PDDL files and the previous error, and suggest a corrected and consistent version according to the following Lore:

    LORE:
    {lore}

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
    In your response pay attention to the pddl syntax. Each pddl block is encapsulated in ( and ). Example (define (guard-awake ?location) A guard is awake at the specified location)
    Here an example of valid domain:
    {load_example_domain()}
    Here an example of valid problem:
    {load_example_problem()}
    """
    response = client.responses.create(
        model=get_model_name(),
        input=prompt
    )
    logging.info(f"Response from Chatgpt:\n{response}")
    logging.info("Chatgpt process completed.")
    return response.output_text

def validate_plan() -> tuple[bool, str]:
    logging.info("Validating plan with Fast Downward...")    
    domain_path = DOMAIN_PATH
    problem_path = PROBLEM_PATH
    command = f"python3 {BASE_DIR}/fast-downward-24.06.1/fast-downward.py {domain_path} {problem_path} --search \"astar(blind())\""
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    output = result.stdout + result.stderr
    logging.info(f"Fast Downward output:\n{result.stdout}\n{result.stderr}")
    return "Solution found" in output or "Plan found" in output, result.stderr