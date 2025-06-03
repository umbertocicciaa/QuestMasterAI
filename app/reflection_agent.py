import subprocess

from langchain_ollama import OllamaLLM

def reflect_on_invalid_pddl(pddl_text: str, planner_output: str, llm: OllamaLLM) -> str:
    prompt = f"""
    The PDDL plan below is invalid. Help fix it.
    PDDL:
    {pddl_text}

    Planner Output:
    {planner_output}

    Suggest a corrected version, preserving story consistency.
    """
    result = llm.invoke(prompt)
    return result
