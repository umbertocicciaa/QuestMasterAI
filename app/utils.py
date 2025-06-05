import json
import logging

from constant import save_domain, save_new_lore, save_problem

def extract_and_save_pddl(response: str) -> None:
    logging.info("Extracting domain and problem PDDL blocks from response...")
    
    try:
        domain_block = response.split("<DOMAIN_PDDL>")[1].split("</DOMAIN_PDDL>")[0].strip()
        problem_block = response.split("<PROBLEM_PDDL>")[1].split("</PROBLEM_PDDL>")[0].strip()
        save_domain(domain_block)
        save_problem(problem_block)
    except Exception:
        logging.error("Failed to extract PDDL blocks from response.")
        return
    
    try:
        lore_block = response.split("<LORE>")[1].split("</LORE>")[0].strip()
        save_new_lore(json.dumps(lore_block))
    except Exception:
        logging.error("Logging error while extracting Lore blocks.")
        return
    
    logging.info("✅ domain.pddl and problem.pddl generated.")
