import streamlit as st
from datetime import datetime, timedelta
from functools import wraps
import pandas as pd
import logging
import time 
from trendspy import Trends

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
                'Trend keywords': news_links_str  # Replace with clickable links
            })

        # Convert the list of data into a pandas DataFrame
        trending_df = pd.DataFrame(data)

        return trending_df

    except Exception as e:
        # Log the detailed error for debugging
        logging.error("An error occurred while fetching trending data.", exc_info=True)
        return pd.DataFrame()  # Return an empty DataFrame on error


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

    if st.button("Refresh Now"):
        # Fetch the trending data
        data = fetch_trending_data()

        # Adjust the timestamp to 6 hours earlier
        current_time = datetime.now()
        adjusted_time = current_time - timedelta(hours=5)
        formatted_time = adjusted_time.strftime('%A, %B %d, %Y at %I:%M %p')

        # Display the last refresh timestamp with markdown formatting
        timestamp_placeholder.markdown(
            f"**Dashboard last refreshed at:** {formatted_time}"
        )

        if not data.empty:
            # Rename columns, except for the first one
            data.columns = ["Search query", "Volume", "Timeframe", "Related articles"]

            # Format volume numbers with thousands separators
            data["Volume"] = data["Volume"].apply(lambda x: f"{x:,}")

            # Format the DataFrame for Streamlit
            styled_data = data.style.format(
                {
                    'Trend keywords': lambda x: x,  # Render HTML for links
                    'Related articles': lambda x: x  # Render HTML for links
                }
            ).set_table_styles(
                [
                    {'selector': 'thead th', 'props': [('text-align', 'left')]},  # Align header
                    {'selector': 'td', 'props': [('text-align', 'left'), ('vertical-align', 'top')]}  # Align cells
                ]
            )

            # Display the results in a table with expanded width and flexible row height
            st.success("Trending topics updated successfully!")
            st.write(styled_data.to_html(escape=False), unsafe_allow_html=True)  # Render as HTML for clickable links

            # Display the time taken to fetch results (Dummy duration for example)
            time_placeholder.markdown(
                f"_Dashboard took {fetch_trending_data.last_duration:.2f} seconds to pull results._",
                unsafe_allow_html=True
            )
        else:
            st.error("No trending data available.") 



if __name__ == "__main__":
    main()