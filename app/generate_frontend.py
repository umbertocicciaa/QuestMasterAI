import logging
import ast
import tempfile
import subprocess
import sys
from openai import OpenAI

from constant import get_model_name, load_story, save_frontend

def check_python_syntax(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file.flush()
            
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', temp_file.name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr
                
    except SyntaxError as e:
        return False, f"Syntax Error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def fix_syntax_errors(client: OpenAI, code: str, error_message: str) -> str:
    logging.info("Attempting to fix syntax errors using OpenAI...")
    
    fix_prompt = f"""
    You are a Python syntax expert. The following Streamlit code has syntax errors. Please fix them and return only the corrected code.

    Error message:
    {error_message}

    Code with errors:
    {code}

    Return the corrected code inside <FIXED_CODE> tags:
    <FIXED_CODE>
    
    </FIXED_CODE>
    
    Rules:
    - Fix only syntax errors, don't change the logic
    - Ensure the code is valid Python and Streamlit
    - Don't use deprecated Streamlit methods
    - Return only the corrected code without explanations
    """
    
    try:
        response = client.responses.create(
            model=get_model_name(),
            input=fix_prompt
        )
        
        fixed_code = response.output_text.split("<FIXED_CODE>")[1].split("</FIXED_CODE>")[0].strip()
        logging.info("Code syntax fixed successfully")
        return fixed_code
        
    except Exception as e:
        logging.error(f"Failed to fix syntax errors: {str(e)}")
        return code


def validate_and_save_frontend(client: OpenAI, frontend_code: str, max_attempts: int = 3) -> None:
    logging.info("Validating frontend code syntax...")
    
    current_code = frontend_code
    attempts = 0
    
    while attempts < max_attempts:
        is_valid, error_message = check_python_syntax(current_code)
        
        if is_valid:
            logging.info("Frontend code syntax is valid. Saving...")
            save_frontend(current_code)
            return
        else:
            attempts += 1
            logging.warning(f"Syntax error detected (attempt {attempts}/{max_attempts}): {error_message}")
            
            if attempts < max_attempts:
                current_code = fix_syntax_errors(client, current_code, error_message)
            else:
                logging.error(f"Failed to fix syntax errors after {max_attempts} attempts. Saving original code...")
                save_frontend(frontend_code)
                return


def extract_and_save_frontend(client: OpenAI, response: str) -> None:
    logging.info("Extracting frontend blocks from response...")
    try:
        frontend_block = response.split("<FRONTEND_CODE>")[1].split("</FRONTEND_CODE>")[0].strip()
        validate_and_save_frontend(client, frontend_block)
    except Exception:
        logging.error("Failed to extract FRONTEND blocks from response.")
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
    extract_and_save_frontend(client, response.output_text)