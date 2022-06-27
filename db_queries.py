from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

import db_models

from config import database_file
## ADD ', echo=True, future=True' below for logging
engine = create_engine("sqlite+pysqlite:///" + str(database_file))
db_models.Base.metadata.create_all(engine)

def get_account_by_user_id(user_id):
    with Session(engine) as session:
        return session.query(db_models.Account).filter(db_models.Account.user_id == user_id).first()

def get_account_by_username(username):
    with Session(engine) as session:
        uname = session.query(db_models.Username).filter(db_models.Username.username == username).first()
        if uname is not None:
            account_id = uname.account_id
        else:
            return None
        account = session.query(db_models.Account).filter(db_models.Account.id == account_id).first()
        return account

def get_posts_by_account_id(account_id):
    with Session(engine) as session:
        return session.query(db_models.Post).filter(db_models.Post.account_id == account_id).order_by(db_models.Post.post_date.desc())
    
def get_latest_post_date(account_id):
    first_post = get_posts_by_account_id(account_id).first()
    return first_post.post_date if first_post is not None else None

def add_account(user_id, username):
    with Session(engine) as session:
        new_account = db_models.Account(user_id = user_id)
        session.add(new_account)
        session.commit()
    add_username(get_account_by_user_id(user_id).id, username)

def add_username(account_id, username):
    with Session(engine) as session:
        new_username = db_models.Username(account_id = account_id, username = username)
        session.add(new_username)
        session.commit()

def add_post(account_id, post_id, post_date):
    with Session(engine) as session:
        new_post = db_models.Post(account_id = account_id, post_id = post_id, post_date = post_date)
        session.add(new_post)
        session.commit()
