from time import sleep
from os import mkdir
from os.path import exists,isdir,isfile
import sys
from datetime import datetime
from dateutil import parser
import pytz
import threading
import requests
from requests.structures import CaseInsensitiveDict
from sqlmanager import SQLManager
from queue import Queue

import db_queries

from config import bearer_token

total_requests = 0
headers = CaseInsensitiveDict()
headers["Authorization"] = "Bearer " + bearer_token

def reformat_date(twitter_date):
    return parser.parse(twitter_date)
    #return  datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)

def request_trimmer():
    global total_requests
    while True:
        if total_requests > 0:
            total_requests -= 1
        sleep(1.15)

def request_limiter():
    global total_requests
    while True:
        if total_requests < 20:
            break
        sleep(1.5)

def download(url, location): 
    filename = location + url.split('/')[-1].split('?')[0]
    if not exists(filename):
        print("Downloading " + url + " to " + filename + ".")
        data = requests.get(url).content
        with open(filename, "wb") as file:
            file.write(data)
    else:
        print(url)
        print(filename + " already exists. It will not be downloaded.")
        
def create_directory(username):
    mkdir(username)
    print("Created directory './" + username + "'.")
        
def download_user_media(username):
    global total_requests
    pagination_token = None
    
    print("Downloading media from " + username)
    
    account = db_queries.get_account_by_username(username)
    if account is None:
        print("No stored ID for " + username + ". Requesting ID...")
        response = requests.get('https://api.twitter.com/2/users/by/username/' + username, headers=headers)
        total_requests += 1
        request_limiter()
        id = int(response.json()['data']['id'])
        db_queries.add_account(id, username)
        account_id = db_queries.get_account_by_user_id(id).id
    else:
        id = account.user_id
        account_id = account.id

    if not exists(username):
        directory_exists = False
    else:
        if isdir(username):
            directory_exists = True
        else:
            pass
            ### TODO HANDLE CASE WHERE A FILE EXISTS AS THE USERNAME

    user_directory = "./" + username + "/"

    most_recent_post_date = db_queries.get_latest_post_date(db_queries.get_account_by_user_id(id).id)

    pagination_token = -1
    while pagination_token is not None:
        query = {'exclude':'retweets,replies', 'expansions':'attachments.media_keys', 'max_results':100, 'tweet.fields':'created_at,author_id'}
        if pagination_token != -1 and pagination_token is not None:
            query["pagination_token"] = pagination_token

        response = requests.get('https://api.twitter.com/2/users/'+str(id)+'/tweets', params=query, headers=headers)
        total_requests += 1
        request_limiter()
        
        try:
            response.json()['data']
        except:
            break
        else:
            newest_tweet = response.json()['data'][0]
            created_at = reformat_date(newest_tweet['created_at'])
            db_queries.add_post(account_id, newest_tweet['id'], created_at)
            
        try:
            response.json()['meta']['next_token']
        except:
            pagination_token = None
        else:
            pagination_token = response.json()['meta']['next_token']
        
        id_list = []
        ## TODO: Rework the check for newest tweet vs tweet.
        try:
            for tweet in response.json()['data']:
                created_at = reformat_date(tweet['created_at'])
                if most_recent_post_date is not None and created_at <= pytz.UTC.localize(most_recent_post_date):
                    raise Exception()
                try:
                    tweet['attachments']
                except:
                    pass
                else:
                    id_list.append(tweet['id'])
        except:
            pagination_token = None
            pass

        for post_id in id_list:
            query = {'id':post_id, 'include_entities':'true', 'trim_user':'true','include_ext_alt_text':'false','include_my_retweet':'false','include_card_uri':'false'}
            response = requests.get('https://api.twitter.com/1.1/statuses/show.json', headers=headers, params=query)
            created_at = reformat_date(response.json()['created_at'])
            total_requests += 1
            request_limiter()
            
            media = None
            try:
                media = response.json()['extended_entities']['media']
            except:
                print("No media in post.")
            else:
                if not directory_exists:
                    create_directory(username)
                for m in media:
                    
                    if m['type'] == 'video':
                        videos = m['video_info']['variants']
                        bitrate = 0
                        video_url = None
                        for v in videos:
                            if v['content_type'] == 'video/mp4':
                                if v['bitrate'] > bitrate:
                                    bitrate = v['bitrate']
                                    video_url = v['url']
                        download(video_url, user_directory)
                    else:
                        download(m['media_url_https']+"?name=orig", user_directory)
                        
                    db_queries.add_post(account_id, response.json()['id'], created_at)
                        
        if pagination_token is None:
            print("End of downloadable media from " + username + "\n")

def main(args):
    del args[0]
    print(args)
    
    user_queues = {}
    sql_manager_queue = Queue()
    
    for username in args:
        user_queues[username] = Queue()

    sql_manager = SQLManager(sql_manager_queue, user_queues)
    sql_manager_thread = threading.Thread(target=sql_manager.run)
    
    request_trimmer_thread = threading.Thread(target=request_trimmer)
    request_trimmer_thread.daemon = True
    request_trimmer_thread.start()

    for username in args:
        #user_downloader_thread = threading.Thread(target=download_user_media, args=(username,user_queues[username],))
        #user_downloader_thread.start()
        download_user_media(username)
        
    
    total_requests = -1

main(sys.argv)
sys.exit()
