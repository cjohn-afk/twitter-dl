from time import sleep
from os import mkdir
from os.path import exists,isdir,isfile
import sys
import threading
import multiprocessing
import requests
from requests.structures import CaseInsensitiveDict

from config import *

totalRequests = 0

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
        
def downloadUserMedia(user):
    global totalRequests
    paginationToken = None
    
    response = requests.get('https://api.twitter.com/2/users/by/username/' + user, headers=headers)
    totalRequests += 1
    requestLimiter()
    id = response.json()['data']['id']

    if not exists(user):
        mkdir(user)
        print("Created directory './" + user + "'.")
    else:
        if isdir(user):
            print("Directory ./" + user + " already exists.")
        else:
            pass
            ### TODO 
            # HANDLE CASE WHERE A FILE EXISTS AS THE USERNAME 

    userDir = "./" + user + "/"

    while True:
        query = {'exclude':'retweets,replies', 'expansions':'attachments.media_keys', 'max_results':100}
        if paginationToken is not None:
            query["pagination_token"] = paginationToken

        response = requests.get('https://api.twitter.com/2/users/'+id+'/tweets', params=query, headers=headers)
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
                print("No attachments in post.")
            else:
                idList.append(tweet['id'])

        for id in idList:
            query = {'id':id, 'include_entities':'true', 'trim_user':'true','include_ext_alt_text':'false','include_my_retweet':'false','include_card_uri':'false'}
            response = requests.get('https://api.twitter.com/1.1/statuses/show.json', headers=headers, params=query)
            totalRequests += 1
            requestLimiter()
            
            media = None
            try:
                media = response.json()['extended_entities']['media']
            except:
                print("No media in post.")
            else:
                for m in media:
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
            print("End of downloadable media from " + user + ".")
            break

args = sys.argv
del args[0]

print(args)

headers = CaseInsensitiveDict()
headers["Authorization"] = "Bearer " + bearer_token

rtThread = threading.Thread(target=requestTrimmer)
rtThread.start()

for user in args:
    userDLThread = threading.Thread(target=downloadUserMedia, args=(user,))
    userDLThread.start()
