"""This is for all the code used to interact with the AlphaVantage API
and the SQLite database. Remember that the API relies on a key that is
stored in your `.env` file and imported via the `config` module.
"""

import sqlite3

import pandas as pd
import requests
from PIL import Image
import imagehash
from io import BytesIO
from datetime import datetime, timedelta


# Helper function
def hash_from_url(thumbnail, url):
    if thumbnail.startswith("https:"):
        response = requests.get(thumbnail)
        if response.headers.get('content-type').startswith("image"):
            img = Image.open(BytesIO(response.content))
            img = img.resize((140,140))
            return str(imagehash.average_hash(img))
    return "Image empty"    

class RedditAPI:
    def __init__(self, subreddit):
    
        self.__Initialized = False
        self.subreddit = subreddit
        self.to_delete = ['all_awardings', 'allow_live_comments', 'author_flair_css_class', 'author_flair_richtext', 'author_flair_text', 'author_flair_type', 'author_fullname', 'author_is_blocked', 'author_patreon_flair', 'author_premium', 'awarders', 'can_mod_post', 'content_categories', 'contest_mode', 'created_utc', 'domain', 'gilded', 'gildings', 'id', 'is_created_from_ads_ui', 'is_crosspostable', 'is_meta', 'is_original_content', 'is_reddit_media_domain', 'is_robot_indexable', 'is_self', 'is_video', 'link_flair_background_color', 'link_flair_css_class', 'link_flair_richtext', 'link_flair_text', 'link_flair_text_color', 'link_flair_type', 'locked', 'media_only', 'no_follow', 'num_comments', 'num_crossposts', 'over_18', 'parent_whitelist_status', 'permalink', 'pinned', 'post_hint', 'preview', 'pwls', 'retrieved_on', 'selftext', 'send_replies', 'spoiler', 'stickied', 'subreddit', 'subreddit_id', 'subreddit_subscribers', 'subreddit_type', 'top_awarded_type', 'total_awards_received', 'treatment_tags', 'upvote_ratio', 'url_overridden_by_dest', 'whitelist_status', 'wls', 'link_flair_template_id', 'author_flair_background_color', 'author_flair_text_color', 'suggested_sort', 'removed_by_category', 'author_cakeday',"author_flair_template_id", "crosspost_parent","crosspost_parent_list", "media", "media_embed", "secure_media", "secure_media_embed", "category"]
    def initialize_past_data(self, start_year, query_per_year=1, minimum_score=1000):
        """Initialize a df with past data

        Parameters
        ----------
        start_year : int
            The year we start querying at
        query_per_year=1
            The number of queries we look at per year
            For example: query_per_year = 2 means we're querying the results every ~180 days
        minimum_score=1000
            Restrict results based on scores = upvotes - downvotes. More often known simply as upvotes

        Returns
        -------
        pd.DataFrame
        """

        # Check if instance has been initialized or not
        if not self.__Initialized:

            # Create Datetime range
            gap = (datetime.now().year - start_year)*query_per_year
            date_list = [timedelta(days=365)+int(365/query_per_year)*timedelta(days=x) for x in range(0,gap)]
            
            # Create list to later concatenate all smaller dataste
            appended_data = []
            print("This is going to take a couple of minutes, sit back and grab a coffee while you wait")

            # Loop through requests
            for i in range(len(date_list)-1):
                before = date_list[i]
                after = date_list[i+1]
                url =  (
                    "https://api.pushshift.io/reddit/search/submission/?"
                    f"subreddit={self.subreddit}&"
                    "size=500&"
                    f"score=%3E{minimum_score}&"
                    f"before={before.days}d&"
                    f"after={after.days}d"
                )
                print(url)
                # Send request to API
                response = requests.get(url=url)

                # Clean response json
                query_data = response.json()["data"]
                for item in query_data:
                    for key in self.to_delete:
                        item.pop(key,None)

                # Read data into DataFrame
                df = pd.DataFrame.from_dict(query_data)

                # Create hash column
                df['hash'] = df.apply(lambda x: hash_from_url(x.thumbnail, x.url), axis=1)
                
                # Remove deleted posts
                df = df[df["hash"] != "Image empty"]

                # Set hash to index
                df.index = df['hash']

                # Add request df to main df
                appended_data.append(df)
            
            # Concatenate all dfs
            self.initialized_df = pd.concat(appended_data)

            # Change Initialized status
            self.__Initialized = True

            # Return DataFrame
            return self.initialized_df

        # If the instance is already initialized
        print("Already Initialized")
        return


    def update(self,max_return=500, upvotes = 5000):
        """Get lastest year top posts from r/pics.

        Parameters
        ----------
        max_return : int, optional
            Number of results to return. Default is 500, which is also the maximum
        upvotes : int, optional
            Restrict results based on scores = upvotes - downvotes. More often known simply as upvotes

        Returns
        -------
        pd.DataFrame
        """
        
        # Create URL

        url =  (
            "https://api.pushshift.io/reddit/search/submission/?"
            f"subreddit={self.subreddit}&"
            f"size={max_return}&"
            f"score=%3E{upvotes}&"
            "after=365d"
        )
        # Send request to API
        response = requests.get(url=url)

        # Clean response json
        query_data = response.json()["data"]
        for item in query_data:
            for key in self.to_delete:
                item.pop(key,None)

        # Read data into DataFrame 
        df = pd.DataFrame.from_dict(query_data)

        # Create hash column
        df['hash'] = df.apply(lambda x: hash_from_url(x.thumbnail, x.url), axis=1)
        
        # Remove deleted posts
        df = df[df["hash"] != "Image empty"]

        # Set hash to index
        df = df.set_index("hash")

        # Return DataFrame
        return df


class SQLRepository:
    def __init__(self,connection):

        self.connection = connection

    def insert_table(self, table_name, records, if_exists='append'):
    
        """Insert DataFrame into SQLite database as table

        Parameters
        ----------
        table_name : str
        records : pd.DataFrame
        if_exists : str, optional
            How to behave if the table already exists.

            - 'fail': Raise a ValueError.
            - 'replace': Drop the table before inserting new values.
            - 'append': Insert new values to the existing table.

            Dafault: 'fail'

        Returns
        -------
        dict
            Dictionary has two keys:

            - 'transaction_successful', followed by bool
            - 'records_inserted', followed by int
        """
        cur = self.connection.cursor()
        try:
            n_inserted = records.to_sql(name=table_name, con=self.connection, if_exists=if_exists)
            return {
                "transaction_successful": True,
                "records_inserted": n_inserted
            }
        except Exception as e:
            return {
                "transaction_successful": False,
                "error_message": e
            }
        

                

    def read_table(self,table_name, limit=None):
    
        """Read table from database.

        Parameters
        ----------
        table_name : str
            Name of table in SQLite database.
        limit : int, None, optional
            Number of most recent records to retrieve. If `None`, all
            records are retrieved. By default, `None`.

        Returns
        -------
        pd.DataFrame
            Index is DatetimeIndex "date". Columns are 'open', 'high',
            'low', 'close', and 'volume'. All columns are numeric.
        """
        # Create SQL query (with optional limit)
        query = f"SELECT * FROM '{table_name}'"
        if limit:
            query += f" LIMIT {limit}" 

        # Retrieve data, read into DataFrame
        results = pd.read_sql(
            sql=query,con=self.connection,index_col="hash"
        )

        # Return DataFrame
        return results