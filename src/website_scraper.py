"""
This script is used to scrape text content from a website.
It uses BeautifulSoup to get all subpages of a website and then scrapes text content from each subpage.
It also uses Selenium to scrape text content from the website if BeautifulSoup doesn't get any content.

Run with python ./src/scraping/website_scraper.py https://philippeheitzmann.com/
python -m src.scraping.website_scraper https://arcules.com/
"""

import requests
import time 
from bs4 import BeautifulSoup
import logging 
from urllib.parse import urljoin, urlparse
import sys
from typing import Optional

from constants import MAX_SCRAPED_TEXT_LENGTH, SKIP_EXTENSIONS, COMMON_SUBPAGE_NAMES

logging.basicConfig(format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
                    datefmt="%Y-%m-%d:%H:%M:%S",
                    level=logging.INFO,
                    stream=sys.stdout,)

def is_internal_url(base_url: str, url: str) -> bool:
    """
    Determines if the provided URL is internal to the base URL's domain.

    A URL is considered internal if its network location (netloc) is identical
    to that of the base URL's netloc. This typically means that both URLs
    share the same domain name.

    Parameters:
    - base_url (str): The base URL of the website.
    - url (str): The URL to be checked.

    Returns:
    - bool: True if the URL is internal, False otherwise.
    """
    return urlparse(url).netloc == urlparse(base_url).netloc


def get_subpages(url):
    '''Use BeautifulSoup to get all subpages of a website'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    subpages = set()

    for link in soup.find_all('a', href=True):
        href = link['href']
        if is_internal_url(url, href) or href.strip("/").lower() in COMMON_SUBPAGE_NAMES:
            subpage = urljoin(url, href)
            subpages.add(subpage)

    return subpages


def get_text_from_url(url: str) -> Optional[str]:
    """
    Fetches the content at the given URL and extracts text contained within <p> tags.

    :param url: The URL of the webpage from which to scrape the text.
    :return: A string containing the concatenated text from all <p> tags, or None if an error occurs.
    """
    if any(url.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        logging.info(f"Skipped URL with skipped extension: {url}")
        return ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        print(f"Error: Unable to fetch {url} - {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Extract text from each paragraph tag
    paragraphs = soup.find_all('p')
    all_text = '\n'.join(paragraph.get_text(strip=True) for paragraph in paragraphs)

    return all_text



def split_string(string, max_length=5000):
    """Split a string into a list of substrings each of max length 5000 characters."""
    substrings = []
    for i in range(0, len(string), max_length):
        substrings.append(string[i:i+max_length])
    return substrings



def check_scraped_text_length(scraped_text):
    if len(scraped_text) > MAX_SCRAPED_TEXT_LENGTH:
        return scraped_text[:MAX_SCRAPED_TEXT_LENGTH]
    return scraped_text


def scrape_single_page(url: str) -> str:
    """
    Scrapes text content from a single webpage using multiple methods.
    
    Args:
        url: The URL to scrape
    Returns:
        The scraped text content
    """
    if any(url.lower().endswith(ext) for ext in SKIP_EXTENSIONS):
        logging.info(f"Skipped URL with excluded extension: {url}")
        return ""
        
    # Try BeautifulSoup first
    text_content = get_text_from_url(url) or ""
    
    # Fall back to Selenium if BeautifulSoup didn't get any content
    # if not text_content:
    #     text_content = scrape_website_text_nodes(url) or ""
        
    return text_content


def scrape_website(main_url: str) -> str:
    """
    Scrapes text content from a main URL and all its subpages.
    
    Args:
        main_url: The main URL to scrape
    Returns:
        Combined text content from all successfully scraped pages
    """
    start_time = time.time()
    
    # Get all pages to scrape
    subpages = get_subpages(main_url)
    subpages.add(main_url)
    logging.info(f"Found {len(subpages)} total pages to scrape")
    
    # Scrape each page
    all_text = []
    successful_pages = 0
    
    for page in subpages:
        try:
            text_content = scrape_single_page(page)
            if text_content:
                all_text.append(text_content)
                successful_pages += 1
                logging.info(f"Successfully scraped {len(text_content)} chars from {page}")
        except Exception as e:
            logging.error(f"Failed to scrape {page}: {str(e)}")
            continue

    # Combine results
    combined_text = " ".join(all_text)
    
    # Log summary
    duration = time.time() - start_time
    logging.info(
        f"Finished scraping {len(combined_text)} total chars from "
        f"{successful_pages}/{len(subpages)} pages in {duration:.2f} seconds"
    )
    
    return combined_text


def save_scraped_text(filename: str, content: str) -> None:
    """
    Writes the given content to a text file. If the file does not exist, it will be created.

    :param filename: The name of the file where the content will be written.
    :param content: The text content that will be written to the file.
    :return: None
    """
    try:
        # Using 'with' automatically takes care of closing the file after the block of code is executed
        with open(filename, "w") as text_file:
            text_file.write(content)
    except IOError as e:
        # Handle the error (for example, print an error message)
        print(f"An error occurred while writing to the file: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python website_scraper.py <website_url>")
        sys.exit(1)
        
    website_url = sys.argv[1]
    try:
        scraped_content = scrape_website(website_url)
        # Save to a file named after the domain
        domain = urlparse(website_url).netloc
        output_file = f"{domain}_scraped.txt"
        save_scraped_text(output_file, scraped_content)
        print(f"Successfully scraped content saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to scrape {website_url}: {str(e)}")
        sys.exit(1)

