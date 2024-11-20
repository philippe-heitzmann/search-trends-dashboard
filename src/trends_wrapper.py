from trendspy import Trends, BatchPeriod
import logging
import pandas as pd


class TrendsWrapper:
    """
    A wrapper class for accessing Google Trends data using the TrendsPy library.
    
    Provides reusable methods for popular Google Trends features:
    - Interest over time
    - Interest by region
    - Related queries and topics
    - Real-time trending searches and news
    - Geographic analysis
    
    Usage:
        tw = TrendsWrapper(proxy={"http": "http://proxy.example.com:3128"})
        df = tw.get_interest_over_time(['python', 'javascript'])
    """
    
    def __init__(self, proxy=None):
        """
        Initialize the TrendsWrapper with optional proxy configuration.

        Args:
            proxy (dict or str, optional): Proxy configuration in requests format.
        """
        self.proxy = proxy
        self.trends = Trends(proxy=proxy)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_interest_over_time(self, keywords, timeframe='today 12-m', geo=None, category=None):
        """
        Retrieve interest over time for specified keywords.

        Args:
            keywords (list): List of keywords to analyze.
            timeframe (str): Timeframe for the analysis (default: 'today 12-m').
            geo (str, optional): Geographic region code (default: None).
            category (str, optional): Category ID for the analysis (default: None).
        
        Returns:
            pandas.DataFrame: DataFrame containing interest over time.
        """
        logging.info(f"Fetching interest over time for keywords: {keywords}")
        return self.trends.interest_over_time(
            keywords, timeframe=timeframe, geo=geo, cat=category
        )

    def get_interest_by_region(self, keyword, geo=None, resolution='COUNTRY'):
        """
        Analyze geographic distribution of interest.

        Args:
            keyword (str): Keyword to analyze.
            geo (str, optional): Geographic region code (default: None).
            resolution (str, optional): Geographic resolution ('COUNTRY', 'REGION', 'CITY').
        
        Returns:
            pandas.DataFrame: DataFrame containing interest by region.
        """
        logging.info(f"Fetching interest by region for keyword: {keyword}")
        return self.trends.interest_by_region(
            keyword, geo=geo, resolution=resolution
        )

    def get_related_queries(self, keyword):
        """
        Retrieve related queries for a keyword.

        Args:
            keyword (str): Keyword to analyze.

        Returns:
            dict: Dictionary of related queries (rising and top).
        """
        logging.info(f"Fetching related queries for keyword: {keyword}")
        return self.trends.related_queries(keyword, 
                                           headers={'referer': 'https://www.google.com/'})

    def get_related_topics(self, keyword):
        """
        Retrieve related topics for a keyword.

        Args:
            keyword (str): Keyword to analyze.

        Returns:
            dict: Dictionary of related topics (rising and top).
        """
        logging.info(f"Fetching related topics for keyword: {keyword}")
        return self.trends.related_topics(keyword)

    def get_trending_now(self, geo='US'):
        """
        Retrieve currently trending searches.

        Args:
            geo (str): Geographic region code (default: 'US').

        Returns:
            list: List of trending topics.
        """
        logging.info(f"Fetching trending searches for geo: {geo}")
        return self.trends.trending_now(geo=geo)

    def get_trending_news(self, geo='US'):
        """
        Retrieve trending searches with associated news articles.

        Args:
            geo (str): Geographic region code (default: 'US').

        Returns:
            list: List of trending topics with associated news articles.
        """
        logging.info(f"Fetching trending searches with news for geo: {geo}")
        return self.trends.trending_now_by_rss(geo=geo)

    def get_historical_trends(self, keywords, timeframe=BatchPeriod.Past24H):
        """
        Retrieve independent historical data for multiple keywords.

        Args:
            keywords (list): List of keywords to analyze.
            timeframe (BatchPeriod): Timeframe for the analysis (default: Past24H).

        Returns:
            pandas.DataFrame: DataFrame containing historical trends.
        """
        logging.info(f"Fetching historical trends for keywords: {keywords}")
        return self.trends.trending_now_showcase_timeline(keywords, timeframe=timeframe)

    def search_categories(self, query):
        """
        Search for category IDs based on a query string.

        Args:
            query (str): Query string to search for categories.

        Returns:
            list: List of matching categories with their IDs.
        """
        logging.info(f"Searching for categories matching: {query}")
        return self.trends.categories(find=query)

    def search_locations(self, query):
        """
        Search for location codes based on a query string.

        Args:
            query (str): Query string to search for locations.

        Returns:
            list: List of matching locations with their IDs.
        """
        logging.info(f"Searching for locations matching: {query}")
        return self.trends.geo(find=query)

    def set_proxy(self, proxy):
        """
        Update the proxy configuration.

        Args:
            proxy (dict or str): Proxy configuration in requests format.
        """
        logging.info("Updating proxy configuration.")
        self.trends.set_proxy(proxy)


def parse_related_queries(keyword, trends_wrapper, output_file=None):
    """
    Fetch, parse, and save related queries for a given keyword using TrendsPy.

    Args:
        keyword (str): The search keyword for which related queries are fetched.
        trends_wrapper (TrendsWrapper): An instance of the TrendsWrapper class.
        output_file (str, optional): Path to save the resulting CSV file. Defaults to None.

    Returns:
        pandas.DataFrame: DataFrame containing the parsed related queries.
    
    Columns in DataFrame:
        - query: The related search query text.
        - value: Popularity or growth score of the related query.
        - category: Indicates whether the query is 'top' or 'rising'.
        - keyword: The original keyword used in the search.
    """
    # Fetch related queries
    related_queries = trends_wrapper.get_related_queries(keyword)
    
    # Initialize a list to store parsed data
    data = []

    # Process each category ('top' and 'rising') in the related queries
    for category, queries in related_queries.items():
        if queries is not None:  # Ensure there are queries in the category
            for _, query_data in queries.iterrows():  # Iterate over the DataFrame rows
                data.append({
                    'query': query_data['query'],  # Query text
                    'value': query_data['value'],  # Popularity or growth score
                    'category': category,  # 'top' or 'rising'
                    'keyword': keyword  # The original keyword for traceability
                })

    # Convert the collected data into a pandas DataFrame
    df_related_queries = pd.DataFrame(data)

    # Save the DataFrame to a CSV file if an output file path is provided
    if output_file:
        df_related_queries.to_csv(output_file, index=False)
        print(f"Related queries saved to {output_file}")

    # Return the DataFrame for further analysis
    return df_related_queries