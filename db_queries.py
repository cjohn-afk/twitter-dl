from datetime import datetime

def reformat_date(twitter_date):
    return datetime.strftime(datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')

def get_user_id(username):
    pass

def get_latest_post_date(user_id):
    pass

def add_user(username):
    pass

def add_username(user_id, username):
    pass

def add_post(user_id, post_id, post_date, media_id):
    pass
