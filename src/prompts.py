def create_prompt_find_article_ideas(scraped_text):
    """
    Creates a prompt for article idea generation based on scraped content.
    
    Args:
        scraped_text (str): The concatenated text from all scraped articles.
        
    Returns:
        str: A formatted prompt for article idea generation.
    """
    return f"""Based on the following competitor article content, suggest 5 areas 
    were not addressed in these articles that could be written to provide additional value to readers:
    
    {scraped_text}
    
    Please provide article ideas in the following format:
    1. [Article Title] - [Brief description]
    2. [Article Title] - [Brief description]
    etc.
    """