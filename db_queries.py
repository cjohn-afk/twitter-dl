from sqlalchemy import select
from sqlalchemy.orm import Session

import db_models

from config import database_file
engine = create_engine("sqlite+pysqlite:///" + database_file, echo=True, future=True)

from datetime import datetime

def reformat_date(twitter_date):
    return datetime.strftime(datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')

def get_account_by_user_id(user_id):
    return session.query(db_models.Account).filter(db_models.Acount.user_id == user_id).first()
    
def get_account_by_username(username):
    with Session(engine) as session:
        account_id = session.query(db_models.Username).filter(db_models.Username.username == username).first().account_id
        account = session.query(db_models.Account).filter(db_models.Acount.id == account_id).first()
        return account

def get_posts_by_account_id(account_id):
    return session.query(db_models.Post).filter(db_models.Post.account_id == account_id)
    
def get_latest_post_date(account_id):
    return get_posts_by_account_id(account_id).last().post_date

def add_account(user_id, username):
    with Session(engine) as session:
        new_account = Account(user_id = user_id)
        session.add(new_account)
        session.commit()
    add_username(new_account.id, username)

def add_username(account_id, username):
    with Session(engine) as session:
        new_username = Username(account_id = account_id, username = username)
        session.add(new_username)
        session.commit()

def add_post(account_id, post_id, post_date, media_id):
    with Session(engine) as session:
        new_post = Post(account_id = account_id, post_id = post_id, post_date = post_date, media_id = media_id)
        session.add(new_post)
        session.commit()
