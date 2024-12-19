#!/usr/bin/env python3
"""
Google Trends Story Explorer

This script demonstrates the usage of the trending_stories API endpoint from the TrendsPy library.
It fetches and logs detailed information about trending stories across different categories.

Usage:
    python trending_stories.py [--category CATEGORY] [--geo GEO] [--max_stories MAX_STORIES]
    python ./src/trending_stories.py --category all --geo US --max_stories 10

Categories:
    - all: All categories (default)
    - b: Business
    - e: Entertainment
    - m: Health
    - t: Sci/Tech
    - s: Sports
    - h: Top stories

Example:
    python test_trending_stories.py --category b --geo US --max_stories 10

Requirements:
    - trendspy library
    - rich library (for pretty printing)
"""

import argparse
import json
import logging
from rich.console import Console
from rich.table import Table
from trendspy import Trends

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trending_stories.log'),
        logging.StreamHandler()
    ]
)

def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Explore Google Trends Stories API')
    parser.add_argument('--category', default='all',
                      help='Category to fetch (all, b, e, m, t, s, h)')
    parser.add_argument('--geo', default='US',
                      help='Geographic location (e.g., US, GB, DE)')
    parser.add_argument('--max_stories', type=int, default=10,
                      help='Maximum number of stories to fetch')
    return parser

def explore_trending_stories(category='all', geo='US', max_stories=10):
    """
    Fetch and explore trending stories from Google Trends.
    
    Args:
        category (str): Story category
        geo (str): Geographic location
        max_stories (int): Maximum number of stories to fetch
    """
    tr = Trends()
    
    # Fetch both raw and processed data
    raw_data = tr.trending_stories(
        geo=geo,
        category=category,
        max_stories=max_stories,
        return_raw=True
    )
    
    processed_data = tr.trending_stories(
        geo=geo,
        category=category,
        max_stories=max_stories,
        return_raw=False
    )

    # Log raw response
    logging.info("Raw API Response Structure:")
    logging.info(json.dumps(raw_data, indent=2))

    # Create a pretty table for the processed results
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Title")
    table.add_column("Entity Names")
    table.add_column("Article Count")
    table.add_column("Time Range")

    # Process and display each trending story
    for story in processed_data:
        # Log detailed information about each story
        logging.info(f"\nDetailed Story Information:")
        logging.info(f"Story Title: {story.title}")
        logging.info(f"Entity Names: {story.entityNames}")
        logging.info(f"Article Count: {story.articles_count}")
        
        # Add row to the pretty table
        table.add_row(
            story.title,
            ", ".join(story.entityNames) if story.entityNames else "N/A",
            str(story.articles_count),
            f"{story.time}"
        )

    # Print the pretty table
    console.print("\nTrending Stories Summary:")
    console.print(table)

def main():
    """Main function to run the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    logging.info(f"Starting trending stories exploration with parameters:")
    logging.info(f"Category: {args.category}")
    logging.info(f"Geo: {args.geo}")
    logging.info(f"Max Stories: {args.max_stories}")
    
    try:
        explore_trending_stories(
            category=args.category,
            geo=args.geo,
            max_stories=args.max_stories
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()