from pathlib import Path

def setup_config_folder(config_dir):
    if not config_dir.exists():
        config_dir.mkdir(parents = True)

def get_bearer_token():
    global bearer_token_file
    if bearer_token_file.exists():
        with open(bearer_token_file, 'rt') as file:
            return file.read()
    else:
        return None

def set_bearer_token(bearer__token):
    global bearer_token_file
    bearer_token = bearer__token
    with open(bearer_token_file, 'w') as file:
        file.write(bearer__token)
        file.close()

config_dir = Path.home() / '.config' / 'twitter-dl'
setup_config_folder(config_dir)

download_directory = Path.home() / 'Downloads' / 'test'

bearer_token_file = config_dir / 'bearer_token'
database_file = config_dir / 'twitter-dl.db'

bearer_token = get_bearer_token()
