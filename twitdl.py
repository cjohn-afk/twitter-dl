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

totalRequests = 0
headers = CaseInsensitiveDict()
headers["Authorization"] = "Bearer " + bearer_token

def reformat_date(twitter_date):
    return  datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.UTC)

def requestTrimmer():
    global totalRequests
    while True:
        if totalRequests > 0:
            totalRequests -= 1
        sleep(1.15)

def requestLimiter():
    global totalRequests
    while True:
        if totalRequests < 20:
            break
        sleep(1.5)

def download(URL, location): 
    filename = location + URL.split('/')[-1].split('?')[0]
    if not exists(filename):
        print("Downloading " + URL + " to " + filename + ".")
        data = requests.get(URL).content
        with open(filename, "wb") as file:
            file.write(data)
    else:
        print(URL)
        print(filename + " already exists. It will not be downloaded.")
        
def downloadUserMedia(username):
    global totalRequests
    paginationToken = None
    
    account = db_queries.get_account_by_username(username)
    if account is None:
        print("No stored ID for " + username + ". Requesting ID...")
        response = requests.get('https://api.twitter.com/2/users/by/username/' + username, headers=headers)
        totalRequests += 1
        requestLimiter()
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

    userDir = "./" + username + "/"

    most_recent_post_date = db_queries.get_latest_post_date(db_queries.get_account_by_user_id(id).id)

    paginationToken = -1
    while paginationToken is not None:
        query = {'exclude':'retweets,replies', 'expansions':'attachments.media_keys', 'max_results':100}
        if paginationToken != -1 and paginationToken is not None:
            query["pagination_token"] = paginationToken

        response = requests.get('https://api.twitter.com/2/users/'+str(id)+'/tweets', params=query, headers=headers)
        totalRequests += 1
        requestLimiter()
        
        try:
            response.json()['data']
        except:
            break
            
        try:
            response.json()['meta']['next_token']
        except:
            paginationToken = None
        else:
            paginationToken = response.json()['meta']['next_token']
        
        idList = []
        for tweet in response.json()['data']:
            try:
                tweet['attachments']
            except:
                pass
            else:
                idList.append(tweet['id'])

        for postID in idList:
            query = {'id':postID, 'include_entities':'true', 'trim_user':'true','include_ext_alt_text':'false','include_my_retweet':'false','include_card_uri':'false'}
            response = requests.get('https://api.twitter.com/1.1/statuses/show.json', headers=headers, params=query)
            created_at = reformat_date(response.json()['created_at'])
            totalRequests += 1
            requestLimiter()
            
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
                        videoURL = None
                        for v in videos:
                            if v['content_type'] == 'video/mp4':
                                if v['bitrate'] > bitrate:
                                    bitrate = v['bitrate']
                                    videoURL = v['url']
                        download(videoURL, userDir)
                    else:
                        download(m['media_url_https']+"?name=orig", userDir)
                        
        if paginationToken is None:
            print("End of downloadable media from " + username + ".")

def main(args):
    del args[0]

    print(args)

    rtThread = threading.Thread(target=requestTrimmer)
    rtThread.daemon = True
    rtThread.start()

    for username in args:
        downloadUserMedia(username)
        
    totalRequests = -1

main(sys.argv)
sys.exit()
