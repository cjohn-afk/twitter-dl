from multiprocessing import Process, JoinableQueue
from threading import Thread
from queue import LifoQueue
from pathlib import Path
from time import sleep
import requests
from datetime import datetime

from config import download_directory
import db_queries

class UserMediaDownloader(Process):
    def __init__(self, download_queue):
        super().__init__(target=self.download_media)
        self.daemon         = True
        self.download_queue = download_queue
        self.thread_queue   = LifoQueue(maxsize = 50)
        
    def download_media(self):
        while(True):
            media = self.download_queue.get()
            if not media['path'].exists():
                media['path'].mkdir(parents = True)
            dl_thread = Thread(target=self.download, args=(media['url'], media['path'],))
            dl_thread.start()
            self.thread_queue.put(dl_thread)
            
    
    def download(self, url, path, retries = 0):
        filename = path / url.split('/')[-1].split('?')[0]
        if not filename.exists():
            print("[" + path.parts[-1] + "]: Downloading " + str(filename.parts[-1]))
            try:
                data = requests.get(url).content
            except:
                print("[" + path.parts[-1] + "]: Failed to download " + str(filename.parts[-1]))
                if retries < 5:
                    retries += 1
                    print("[" + path.parts[-1] + "]: Download of " + str(filename.parts[-1]) + " failed, trying again.  Attempt " + str(retries))
                    sleep(5)
                    self.download(url, path, retries)
                else:
                    print("[" + path.parts[-1] + "]: Download of " + str(filename.parts[-1]) + " failed." + str(retries))
                    raise Exception
            else:
                with open(filename, "wb") as file:
                    file.write(data)
        else:
            print("[" + path.parts[-1] + "]: " + str(filename.parts[-1]) + " already exists. Skipping.")
        self.thread_queue.get()
        self.thread_queue.task_done()
        self.download_queue.task_done()

class UserMediaCollector(Process):
    def __init__(self, username, t_api, download_queue, pictures_only = False, videos_only = False, update = False):
        super().__init__(target=self.get_user_media, args=(username,))
        
        self.download_dir = Path().expanduser() / username
        
        self.pictures_only  = pictures_only
        self.videos_only    = videos_only
        self.update         = update
        
        self.t_api = t_api
        
        self.download_queue = download_queue
        
    def get_user_media(self, username):
        account = db_queries.get_account_by_username(username)
        latest_post_id = None
        
        if account is None:
            user_id = self.t_api.get_user_id(username)
            #TODO: Handle case where username doesn't exist or is not found. Currently the assignment of 'id' below causes an error in this case because the response will not contain a data key if the username is not found.
            db_queries.add_account(user_id, username)
            account_id = db_queries.get_account_by_user_id(user_id).id
            latest_post_id = None
        else:
            user_id = account.user_id
            account_id = account.id
            latest_post_id = db_queries.get_latest_post_id(account_id)
        
        future_latest_post_id = None

        media_list = []
        
        pagination_token = -1
        page_num = 0
        
        while pagination_token is not None:
            page_num += 1
            print("[" + username + "]: Scanning page " + str(page_num))
            tweets = self.t_api.get_tweets(user_id, pagination_token = pagination_token if pagination_token != -1 and pagination_token is not None else None, since_id = (latest_post_id if self.update else None))
            
            if future_latest_post_id is None:
                try:
                    future_latest_post_id = tweets['meta']['newest_id']
                except:
                    print("[" + username + "]: No new media.")
                    
            try:
                tweets['meta']['next_token']
            except:
                pagination_token = None
            else:
                pagination_token = tweets['meta']['next_token']

            try:
                tweets['includes']['media']
            except:
                tweets = []
            else:
               tweets = tweets['includes']['media']
               
            for media in tweets:
                
                if (media['type'] == 'video' or media['type'] == 'animated_gif') and not self.pictures_only:
                    videos = media['variants']
                    bit_rate = -1
                    video_url = None
                    for v in videos:
                        if v['content_type'] == 'video/mp4':
                            if v['bit_rate'] > bit_rate:
                                bit_rate = v['bit_rate']
                                video_url = v['url']
                    self.download_queue.put({'url': video_url, 'path': self.download_dir })
                elif media['type'] == 'photo' and not self.videos_only:
                    self.download_queue.put({'url': media['url']+'?name=orig', 'path': self.download_dir })

        if self.update and future_latest_post_id is not None:
            db_queries.add_post(account_id, future_latest_post_id, datetime.now())
