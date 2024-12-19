import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
import pandas as pd
import logging
import time 
from trendspy import Trends

from website_scraper import scrape_single_page
from utils import save_text, query_chatgpt
from prompts import create_prompt_find_article_ideas


# Set up logging to a file
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize the TrendsWrapper (configure proxy if needed)
tr = Trends()  # Example: TrendsWrapper(proxy={'http': 'http://proxy:port', 'https': 'https://proxy:port'})

def time_it(func):
    """
    A decorator that measures and prints the time taken by a function to complete.
    
    Args:
        func (callable): The function to be decorated.
    
    Returns:
        callable: The wrapped function with timing functionality.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the wrapped function
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        wrapper.last_duration = duration  # Store the duration in the wrapper
        print(f"Function '{func.__name__}' completed in {duration:.2f} seconds.")
        return result  # Return the result of the function
    wrapper.last_duration = 0  # Initialize last_duration attribute
    return wrapper

@time_it
def fetch_trending_data():
    """
    Fetch trending data and related news articles, merge the results into a DataFrame.
    
    Returns:
        pandas.DataFrame: DataFrame containing the merged trending data.
    """
    try:
        # Fetch trending topics
        trending_now_data = tr.trending_now(geo='US')

        # Limit the size of the trending topics to 3
        trending_now_data = trending_now_data[:3]

        # Initialize a list to store data
        data = []

        # Process each TrendKeyword object
        for trend in trending_now_data:
            # logging.info(f"trend attributes: {trend.__dict__}")
            # Extract basic information about the trend
            keyword = trend.keyword
            volume = trend.volume
            timeframe = f"{trend._convert_to_datetime(trend.started_timestamp[0]).strftime('%Y-%m-%d %H:%M:%S')} - " \
                        f"{trend._convert_to_datetime(trend.ended_timestamp[0]).strftime('%Y-%m-%d %H:%M:%S') if trend.is_trend_finished else 'now'}"

            # Fetch news articles related to the trend using `trending_now_news_by_ids`
            news_articles_data = tr.trending_now_news_by_ids(trend.news_tokens, max_news=5)
            news_links = []
            for article in news_articles_data:
                # Append clickable URLs
                news_links.append(f"<a href='{article.url}' target='_blank'>{article.url}</a>")
                time.sleep(0.5)  # Add a delay to avoid hitting API rate limits

            # Combine all news links into a newline-separated string
            news_links_str = "<br>".join(news_links) if news_links else "No articles"

            # Append the extracted data to the list
            data.append({
                'Keyword': keyword,
                'Volume': volume,
                'Timeframe': timeframe,
                'Articles': news_links_str  # Replace with clickable links
            })

        # Convert the list of data into a pandas DataFrame
        trending_df = pd.DataFrame(data)

        return trending_df

    except Exception as e:
        # Log the detailed error for debugging
        logging.error("An error occurred while fetching trending data.", exc_info=True)
        return pd.DataFrame()  # Return an empty DataFrame on error


@time_it
def scrape_articles(search_queries):
    """
    Scrape article ideas based on trending search queries.
    
    Args:
        search_queries (str): Text containing article URLs
    """
    all_text = ""
    
    # Extract all URLs from the text
    logging.info(f"Scraping articles for query: {search_queries} of type {type(search_queries)}")
    urls = scrape_urls(search_queries)
    # Deduplicate URLs using set operation while preserving order
    urls = list(dict.fromkeys(urls))
    logging.info(f"Found {len(urls)} unique URLs of {urls}")
    
    # Scrape each URL
    for url in urls:
        logging.info(f"Scraping article from URL: {url}")
        try:
            text = scrape_single_page(url)
            all_text += f"\n--- Article from {url} ---\n{text}\n"
        except Exception as e:
            logging.error(f"Error scraping URL {url}: {str(e)}")

    return all_text


def scrape_urls(search_queries: str):
    """
    Extract all HTTPS URLs from text string or list of strings.
    
    Args:
        search_queries (Union[str, list]): Text or list containing URLs
    
    Returns:
        list[str]: List of extracted HTTPS URLs
    """
    # Convert to string if list is provided
    
    urls = []
    current_pos = 0
    
    while True:
        # Find the next https occurrence
        https_start = search_queries.lower().find('https://', current_pos)
        if https_start == -1:  # No more URLs found
            break
            
        # Find the end of the URL (space, quote, or newline)
        url_end = next((
            i for i in range(https_start, len(search_queries))
            if search_queries[i] in [' ', '"', "'", '\n', '<']
        ), len(search_queries))
        
        # Extract the URL
        url = search_queries[https_start:url_end]
        urls.append(url)
        
        # Move position to look for next URL
        current_pos = url_end + 1
    
    return urls



# Streamlit App
def main():
    """
    Main function to render the Streamlit app.
    """
    st.set_page_config(layout="wide")  # Set wide layout for Streamlit
    st.title("Trending Topics Dashboard")
    st.write("View the latest trending topics and related news articles in real-time.")

    # Placeholder for the timestamp and the results
    timestamp_placeholder = st.empty()
    time_placeholder = st.empty()

    # Create a columns layout for the buttons with minimal gap
    col1, col2, col3 = st.columns([1, 1, 8], gap="small")
    
    # Place "Refresh Now" in the first column
    if col1.button("Refresh Now"):
        # Store the fetched data in session state so it persists
        st.session_state.trending_data = fetch_trending_data()
        # Store the duration in session state as well
        st.session_state.last_duration = fetch_trending_data.last_duration
        data = st.session_state.trending_data
        
        # Adjust the timestamp to 6 hours earlier
        current_time = datetime.now()
        adjusted_time = current_time - timedelta(hours=5)
        formatted_time = adjusted_time.strftime('%A, %B %d, %Y at %I:%M %p')

        # Display the last refresh timestamp with markdown formatting
        timestamp_placeholder.markdown(
            f"**Dashboard last refreshed at:** {formatted_time}"
        )

    # Check if we have data stored in session state
    if hasattr(st.session_state, 'trending_data'):
        data = st.session_state.trending_data
        
        # Display the styled data table
        styled_data = data.style.format(
            {
                'Trend keywords': lambda x: x,
                'Related articles': lambda x: x
            }
        ).set_table_styles(
            [
                {'selector': 'thead th', 'props': [('text-align', 'left')]},
                {'selector': 'td', 'props': [('text-align', 'left'), ('vertical-align', 'top')]}
            ]
        )
        st.write(styled_data.to_html(escape=False), unsafe_allow_html=True)
   
        # Update this line to use the stored duration
        if hasattr(st.session_state, 'last_duration'):
            time_placeholder.markdown(
                f"_Dashboard took {st.session_state.last_duration:.2f} seconds to pull results._",
                unsafe_allow_html=True
            )

        # Handle article ideas button separately
        if col2.button("Find article ideas", type="primary", key="find_articles_button"):
            progress_message = st.empty()
            progress_message.info("Processing articles... Please wait.")
            
            try:
                # Process each trending topic
                article_ideas_list = []
                
                # Iterate through all rows in the trending data
                for _, row in data.iterrows():
                    search_query = row["Keyword"]
                    articles = row["Articles"]
                    
                    # Scrape and process articles
                    scraped_text = scrape_articles(articles)
                    
                    # Save scraped text
                    timestamp = datetime.now().strftime("%m%d_%H_%M_%S")
                    save_text(scraped_text, f"./data/scrapedarticles_{search_query}_{timestamp}.txt")
                    
                    # Generate and save article ideas
                    prompt = create_prompt_find_article_ideas(scraped_text)
                    article_ideas = query_chatgpt(prompt)
                    save_text(article_ideas, f"./data/gptsuggestions_{search_query}_{timestamp}.txt")
                    
                    # Add to our list of results
                    article_ideas_list.append({
                        'Search Query': search_query,
                        'Article Ideas': article_ideas
                    })
                
                # Update the session state with new article ideas
                st.session_state.article_ideas_data = pd.DataFrame(article_ideas_list)
                
                progress_message.success("✅ Article processing complete!")
                
                # Display the article ideas table
                st.subheader("Generated Article Ideas")
                styled_ideas = st.session_state.article_ideas_data.style.set_table_styles([
                    {'selector': 'thead th', 'props': [('text-align', 'left')]},
                    {'selector': 'td', 'props': [('text-align', 'left'), ('vertical-align', 'top')]}
                ])
                st.write(styled_ideas.to_html(escape=False), unsafe_allow_html=True)
                
            except Exception as e:
                progress_message.error(f"❌ An error occurred: {str(e)}")
                logging.error(f"Error processing articles: {str(e)}", exc_info=True)

        # Display existing article ideas if they exist in session state
        elif 'article_ideas_data' in st.session_state and not st.session_state.article_ideas_data.empty:
            st.subheader("Generated Article Ideas")
            styled_ideas = st.session_state.article_ideas_data.style.set_table_styles([
                {'selector': 'thead th', 'props': [('text-align', 'left')]},
                {'selector': 'td', 'props': [('text-align', 'left'), ('vertical-align', 'top')]}
            ])
            st.write(styled_ideas.to_html(escape=False), unsafe_allow_html=True)


if __name__ == "__main__":
    main()