def create_prompt_find_article_ideas(scraped_text):
    """
    Creates a prompt for article idea generation based on scraped content.
    
    Args:
        scraped_text (str): The concatenated text from all scraped articles.
        
    Returns:
        str: A formatted prompt for article idea generation.
    """
    return f"""Based on the following competitor article content, suggest 3 areas 
    were not addressed in these articles that could be written to provide additional value to readers.

    For each suggestion, explain in a maximum of three sentences why you think it is a good idea, based on whether
    the existing articles have covered the that sub-topic in their articles, or explained it throughly.
    
    {scraped_text}
    
    Please provide article ideas in the following format:
    Idea #1 - [Brief description]
    Idea #2 - [Brief description]
    Idea #3 - [Brief description]
    """