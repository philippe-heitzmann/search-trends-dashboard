#!/usr/bin/env python3
"""
Google Trends RSS Feed Explorer

This script demonstrates the usage of the trending_now_by_rss API endpoint from the TrendsPy library.
It fetches and logs detailed information about trending topics from Google Trends' RSS feed.

Usage:
    python ./src/trending_rss.py [--geo GEO] [--raw]
    python ./src/trending_rss.py --geo US

Geographic Codes Examples:
    - US: United States
    - GB: United Kingdom
    - DE: Germany
    - FR: France
    - JP: Japan

Example:
    python test_trending_rss.py --geo GB
    python test_trending_rss.py --geo US --raw

Requirements:
    - trendspy library
    - rich library (for pretty printing)
    - xmltodict library (for parsing raw RSS)
"""

import argparse
import json
import logging
import xmltodict
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from trendspy import Trends
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trending_rss.log'),
        logging.StreamHandler()
    ]
)

def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Explore Google Trends RSS Feed API')
    parser.add_argument('--geo', default='US',
                      help='Geographic location (e.g., US, GB, DE)')
    parser.add_argument('--raw', action='store_true',
                      help='Display raw RSS feed data')
    return parser

def parse_raw_rss(raw_xml):
    """
    Parse raw RSS XML data into a more readable format.
    
    Args:
        raw_xml (str): Raw RSS XML data
    
    Returns:
        dict: Parsed RSS data
    """
    try:
        return xmltodict.parse(raw_xml)
    except Exception as e:
        logging.error(f"Failed to parse RSS XML: {str(e)}")
        return None

def explore_trending_rss(geo='US', show_raw=False):
    """
    Fetch and explore trending topics from Google Trends RSS feed.
    
    Args:
        geo (str): Geographic location
        show_raw (bool): Whether to show raw RSS data
    """
    tr = Trends()
    
    # Fetch both raw and processed data
    raw_data = tr.trending_now_by_rss(geo=geo, return_raw=True)
    processed_data = tr.trending_now_by_rss(geo=geo, return_raw=False)

    # Log raw response
    if show_raw:
        logging.info("Raw RSS Feed Response:")
        logging.info(raw_data)
        
        # Parse and log structured RSS data
        parsed_rss = parse_raw_rss(raw_data)
        if parsed_rss:
            logging.info("\nParsed RSS Structure:")
            logging.info(json.dumps(parsed_rss, indent=2))

    # Create a pretty table for the processed results
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Keyword")
    table.add_column("Volume")
    table.add_column("Trend Keywords")
    # table.add_column("Link")
    table.add_column("Started")
    table.add_column("News Articles")

    # Process and display each trending topic
    for trend in processed_data:
        # Log detailed information about each trend
        logging.info(f"\nDetailed Trend Information:")
        logging.info(f"Keyword: {trend.keyword}")
        logging.info(f"Volume: {trend.volume}")
        logging.info(f"Trend Keywords: {', '.join(trend.trend_keywords) if trend.trend_keywords else 'N/A'}")
        # logging.info(f"Link: {trend.link}")
        logging.info(f"Started: {datetime.fromtimestamp(trend.started) if trend.started else 'N/A'}")
        logging.info(f"News Articles: {trend.news if trend.news else 0}")
        
        # Add row to the pretty table
        table.add_row(
            trend.keyword,
            str(trend.volume) if trend.volume else "N/A",
            ', '.join(trend.trend_keywords) if trend.trend_keywords else "N/A",
            trend.link if trend.link else "N/A",
            datetime.fromtimestamp(trend.started).strftime('%Y-%m-%d %H:%M:%S') if trend.started else "N/A",
            f"{trend.news} articles" if trend.news else "No articles"
        )

    # Print the pretty table
    console.print(f"\nTrending Topics from RSS Feed (Region: {geo}):")
    console.print(table)

def main():
    """Main function to run the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    logging.info(f"Starting trending RSS exploration with parameters:")
    logging.info(f"Geo: {args.geo}")
    logging.info(f"Show Raw: {args.raw}")
    
    try:
        explore_trending_rss(
            geo=args.geo,
            show_raw=args.raw
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()