import logging
from openai import OpenAI

from constant import get_model_name, load_story, save_frontend


def extract_and_save_frontend(response: str) -> None:
    logging.info("Extracting frontend blocks from response...")
    
    try:
        frontend_block = response.split("<FRONTEND_CODE>")[1].split("</FRONTEND_CODE>")[0].strip()
        save_frontend(frontend_block)
    except Exception:
        logging.error("Failed to extract PDDL blocks from response.")
        return


def generate_frontend(client: OpenAI) -> None:
    logging.info("Generating Frontend...")
    prompt = f"""
    You are a Senior Streamlit frontend expert. Given the following story.json, generate:
    Streamlit code to create a user interface that allows users to interact with the lore for playing the game. User can make only one choice at a time.
    Don't use deprecated streamlit methods. Use the latest streamlit methods.
    
    Story.json
    {load_story()}
    
    Return yor response like plain text in ASCII character inside.
    <FRONTEND_CODE> 
    
    </FRONTEND_CODE> 
    blocks
    """
    response = client.responses.create(
        model=get_model_name(),
        input=prompt
    )
    logging.info("Chatgpt process completed.")
    logging.info(f"Response: {response}")