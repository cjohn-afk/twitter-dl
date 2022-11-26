from pathlib import Path

class UserList():
    def __init__(self, filename):
        self.list_file  = Path(filename).expanduser()
        if not self.list_file.is_file():
            raise FileNotFoundError
        
        self.user_list = []
        self.index     = 0
        self.loaded    = False
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.loaded: self.load()
        
        if self.index < len(self.user_list):
            user = self.user_list[self.index]
            self.index += 1
            return user
        
        self.index = 0
        raise StopIteration
    
    def load(self):
        try:
            with self.list_file.open() as list_file:
                while(username := list_file.readline().rstrip()):
                    if username is not None:
                        self.user_list.append(username.lower())
        except:
            ## TODO: Handle potential errors
            pass
        else:
            self.loaded = True
