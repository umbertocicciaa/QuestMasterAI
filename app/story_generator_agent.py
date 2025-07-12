import logging
import json

from constant import get_model_name, load_domain, load_example, load_lore, load_plan, load_problem, save_lore
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def generate_story(client: OpenAI) -> None:
    lore = json.loads(load_lore())
    domain = load_domain()
    problem = load_problem()
    plan = load_plan()
    example_structure = load_example()
    
    logging.info("Generazione storia!..")
    
    prompt = f"""Sei uno storyteller interattivo.
    Dati questi file PDDL e questa lore, crea una rappresentazione JSON della storia come macchina a stati finiti (FSM). 

    Lore: {json.dumps(lore, indent=2)}

    DOMAIN.PDDL:
    {domain}

    PROBLEM.PDDL:
    {problem}

    SAS_PLAN
    {plan}

    Genera uno story.json con la seguente struttura e niente altro. Fai riferimento ad una struttura esempio rendendola più originale e dinamica:
    STRUTTURA ESEMPIO:
    {example_structure}
    """

    response = client.responses.create(
        model=get_model_name(),
        input=prompt
    )

    story = response.output_text

    save_lore(story)
    logging.info("story.json generato.")