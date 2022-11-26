import requests
from requests.structures import CaseInsensitiveDict

from multiprocessing import RLock
from time import sleep

class TwitterAPI():
    def __init__(self, bearer_token):
        # Header Dictionary
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = "Bearer " + bearer_token
    
        # API base URL + Endpoints
        self.base_URL = 'https://api.twitter.com'
        self.user_by_username = '/2/users/by/username/{username}'
        self.tweets_by_user_id = '/2/users/{user_id}/tweets'
        self.tweet_by_id = '/2/tweets/{tweet_id}'
        
        # Process Lock
        self.lock = RLock()
        self.requests = 0
        
    def get_user_id(self, username):
        request_URL = (self.base_URL + self.user_by_username).format(username=username)
        response = requests.get(request_URL, headers=self.headers)
        
        user_id = int(response.json()['data']['id'])
        return user_id
    
    def get_tweets(self, user_id, max_results = 100, pagination_token = None, since_id = None):
        request_URL = (self.base_URL + self.tweets_by_user_id).format(user_id=user_id)
        params = {'exclude':'retweets,replies', 'expansions':'attachments.media_keys', 'media.fields':'type,url,variants', 'max_results':max_results, 'tweet.fields':'created_at'} ## until_id ?? 
        if pagination_token is not None:
            params['pagination_token'] = pagination_token
        if since_id is not None:
            params['since_id'] = since_id
            
        self.lock.acquire()
        response = requests.get(request_URL, headers=self.headers, params=params)
        sleep(0.6)
        self.lock.release()
            
        return response.json()
    
    def get_tweet(self, tweet_id):
        pass
