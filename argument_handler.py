import argparse

parser = argparse.ArgumentParser(description='Command line tool to download media from Twitter profiles.')
parser.add_argument('--bearer-token',
                    help='specify the Twitter API bearer token, this token will be saved and used as the default value when this option is unspecified')

parser.add_argument('-n', '--newest', action='store_true',
                    help='download media which has not already been downloaded (NOT IMPLEMENTED)')

parser.add_argument('-p', '--pictures-only', action='store_true',
                    help='download pictures, do not download videos (NOT IMPLEMENTED)')

parser.add_argument('-v', '--videos-only', action='store_true',
                    help='download videos, do not download pictures (NOT IMPLEMENTED)')

parser.add_argument('-t', '--target-dir',
                    help='specify a target directory for downloaded media, if it doesn\'t exist an attempt will be made to create it')

parser.add_argument('-l', '--list',
                    help='read from a text file containing a list of usernames')

parser.add_argument('username', type=str, nargs='*',
                    help='a username, or list of usernames to download media from')

args = parser.parse_args()
