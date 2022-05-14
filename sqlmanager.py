from queue import Queue
import db_queries

class SQLManager:
    def __init__(self, input_queue, output_queue_list):
        self.input_queue  = input_queue
        self.output_queue_list = output_queue_list
        self.username = None
        self.data  =  None
    
    def get_account_by_username():
        account = db_queries.get_account_by_username(self.data['username'])
        self.add_to_output_queue(self.username, account)
        
    def get_account_by_user_id(user_id):
        account = db_queries.get_account_by_username(self.data['user_id'])
        self.add_to_output_queue(self.username, account)
        
    def get_latest_post_date():
        date = db_queries.get_latest_post_date(self.data['account_id'])
        self.add_to_output_queue(self.username, date)

    def add_account():
        user_id = self.data['user_id']
        username = self.username
        db_queries.add_account(user_id, username)
        
        
    def add_post():
        account_id = self.data['account_id']
        post_id = self.data['post_id']
        post_date = self.data['post_date']
        db_queries.add_post(account_id, post_id, post_date)
        
    
    def next_statement():
        return self.input_queue.get()
    
    def send_to_output_queue(username, object):
        self.output_queue_list[username].put(object)
    
    def main_loop():
        statement = self.next_statment()
        if statement is not None:
            
            self.username = statement['username']
            querie_type = statement['querie_type']
            self.data   = statment['data']

            if querie_type == "get_account_by_username":
                self.get_account_by_username()
                
            elif querie_type == "get_account_by_user_id":
                self.get_account_by_user_id()
                
            elif querie_type == "get_latest_post_date":
                self.get_latest_post_date()
                
            elif querie_type == "add_account":
                self.add_account()
                
            elif querie_type == "add_post":
                self.add_post()
    
    def run():
        while True:
           main_loop()
