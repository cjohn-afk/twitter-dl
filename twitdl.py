from time import sleep
from os import mkdir
from os.path import exists,isdir,isfile
import sys
from datetime import datetime
import pytz
import threading
import requests
from requests.structures import CaseInsensitiveDict

import db_queries

from config import bearer_token

total_requests = 0
headers = CaseInsensitiveDict()
headers["Authorization"] = "Bearer " + bearer_token

def reformat_date(twitter_date):
    return  datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)

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
        
def download_user_media(username):
    global total_requests
    pagination_token = None
    
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
        mkdir(username)
        print("Created directory './" + username + "'.")
    else:
        if isdir(username):
            print("Directory ./" + username + " already exists.")
        else:
            pass
            ### TODO HANDLE CASE WHERE A FILE EXISTS AS THE USERNAME 

    user_directory = "./" + username + "/"

    most_recent_post_date = db_queries.get_latest_post_date(db_queries.get_account_by_user_id(id).id)

    pagination_token = -1
    while pagination_token is not None:
        query = {'exclude':'retweets,replies', 'expansions':'attachments.media_keys', 'max_results':100}
        if pagination_token != -1 and pagination_token is not None:
            query["pagination_token"] = pagination_token

        response = requests.get('https://api.twitter.com/2/users/'+str(id)+'/tweets', params=query, headers=headers)
        total_requests += 1
        request_limiter()
        
        try:
            response.json()['data']
        except:
            break
            
        try:
            response.json()['meta']['next_token']
        except:
            pagination_token = None
        else:
            pagination_token = response.json()['meta']['next_token']
        
        id_list = []
        for tweet in response.json()['data']:
            try:
                tweet['attachments']
            except:
                pass
            else:
                id_list.append(tweet['id'])

        for post_id in id_list:
            query = {'id':post_id, 'include_entities':'true', 'trim_user':'true','include_ext_alt_text':'false','include_my_retweet':'false','include_card_uri':'false'}
            response = requests.get('https://api.twitter.com/1.1/statuses/show.json', headers=headers, params=query)
            created_at = reformat_date(response.json()['created_at'])
            total_requests += 1
            request_limiter()
            
            if most_recent_post_date is not None and created_at <= pytz.UTC.localize(most_recent_post_date):
                break
            
            media = None
            try:
                media = response.json()['extended_entities']['media']
            except:
                print("No media in post.")
            else:
                for m in media:
                    
                    db_queries.add_post(account_id, response.json()['id'], created_at)
                    
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
                        
        if pagination_token is None:
            print("End of downloadable media from " + username + ".")

def main(args):
    del args[0]

    print(args)

    request_trimmer_thread = threading.Thread(target=request_trimmer)
    request_trimmer_thread.daemon = True
    request_trimmer_thread.start()

    for username in args:
        download_user_media(username)
        
    total_requests = -1

main(sys.argv)
sys.exit()
