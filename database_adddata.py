import mysql.connector
import pymongo
from database import Database_connector
import tweepy 
import praw 
import instaloader
import datetime 

class Data_Loader(Database_connector):
    def __init__(self):
        super().__init__()
    def load_data_instagram(self):
        L = instaloader.Instaloader()
        USERNAME = ""
        PASSWORD = ""
        L.login(USERNAME,PASSWORD)
        hashtag_name = "trending"
        posts = instaloader.Hashtag.from_name(L.context, hashtag_name).get_posts()

        count = 0
        for post in posts:
            if count >= 100:
                break
        
            doc = {
                "platform": "instagram",
                    "id": post.shortcode,
                    "title": post.caption or "",
                    "likes": post.likes,
                    "comments": post.comments,
                    "author": post.owner_username,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "created_utc": datetime.utcfromtimestamp(post.date_utc.timestamp()),
                    "fetched_at": datetime.utcnow()
                }
            super().add_data_mongo('reddit',doc)

        print(f"Saved {count} Instagram posts")
    def load_data_reddit(self):
        reddit = praw.Reddit(client_id = '',client_secret='',user_agent = '')
        '''
        trend analysis: likes. karnma , title(subject detection , locations)
        '''
        subreddit = reddit.subreddit('all')
        data = []
        for post in subreddit.hot(limit=100000):
            post_data = {
                "author": str(post.author) if post.author else None,
                "likes": post.ups,         
                "post_score": post.score,
                "down_votes": post.ups - post.score,
                "title": post.title,
                "subreddit": str(post.subreddit),  
                "url": post.url,
                "location": None                   
            }
            if hasattr(post, "link_flair_text") and post.link_flair_text:
                post_data["location"] = post.link_flair_text
            data.append(post_data)
        if data:
            try:
                super().add_data_mongo('reddit',data)
                Database_connector.write_logs('successfully added data to mongodb database reddit function') 
            except Exception as e:
                Database_connector.write_logs('Unable to add to database from database_adddata.py function for reddit ',e)        
d = Data_Loader()
d.load_data_instagram()