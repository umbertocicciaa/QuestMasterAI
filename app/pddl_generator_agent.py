import json
import logging

from story_generator_agent import generate_story
from constant import get_model_name, load_domain, load_example_domain, load_example_problem, load_lore, load_new_lore, load_problem
from reflect_agent import reflect_on_invalid_pddl, validate_plan
from utils import extract_and_save_pddl

from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def generate_pddl(lore: str, client: OpenAI) -> str:
    logging.info("Generating PDDL...")
    prompt = f"""
    You are a PDDL modeler. Given the following quest description, generate:
    1. A DOMAIN.PDDL file with predicates and actions, each with comments.
    2. A PROBLEM.PDDL file with an initial state and goal consistent with the domain.
    
    Lore:
    {json.dumps(lore, indent=2)}
    
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
    logging.info("OllamLLM process completed.")
    logging.info(f"Response: {response}")
    return response.output_text 

client = OpenAI()
lore = load_lore()
response = generate_pddl(lore, client)
extract_and_save_pddl(response)

while True:
    valid, validation_output = validate_plan()
    if valid:
        logging.info("Plan is valid! ✅")
        generate_story(client)
        break
    else:
        logging.warning("Plan is invalid! ❌")
        logging.info("Reflecting on invalid PDDL...")
        new_pddl = reflect_on_invalid_pddl(lore, load_domain(), load_problem(), validation_output,client)
        extract_and_save_pddl(new_pddl)