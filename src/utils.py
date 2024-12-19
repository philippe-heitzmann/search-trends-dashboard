import logging

logging.basicConfig(level=logging.INFO)

def save_text(content: str, filepath: str) -> None:
    """
    Saves text content to a file with error handling.
    
    Args:
        content: Text content to save
        filepath: Path where the file should be saved
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"File saved to {filepath}")
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")