import logging
from pathlib import Path

DOMAIN_PATH = Path("data/domain.pddl")
PROBLEM_PATH = Path("data/problem.pddl")

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
    
    logging.info("✅ domain.pddl and problem.pddl generated.")
