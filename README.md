# twitter-dl
A command line tool to download media from twitter profiles.

## How it works
twitter-dl takes in a list of twitter usernames as command like arguments. It then downloads all media from the given users in the current directory with all downloaded files going into their respective user folders. It also creates a database in the current directory (if not already created) which stores the user id, the username associated with the user id, and each post that is downloaded. This tool only downloads posts which are more recent than the most recently downloaded post for a given user in the database.

## Config
Upon its first execution twitter-dl creates a directory at ~/.config/twitter-dl in which it stores two files. The first file is twitter-dl.db: a sqlite database containing information about downloaded tweets. The second file is bearer_token: a file that contains a Twitter API bearer token. The bearer_token file is only created when a bearer token is supplied using the --bearer-token argument (i.e. twitter-dl --bearer-token=[YOUR BEARER TOKEN]).

## Known Issues
- Only tested on Linux. This is by design and I have no plans right now to ensure it is cross-compatible with Windows and macOS.

- User downloads happen synchronously.
The process of downloading user media should happen in a multi-threaded manner in which each user's media is downloaded at one time to maximize the potential speed of completion. Currently the tool only downloads one user's media at a time which substantially increases the time to completion if there is a large amount of media to download.

- User feedback is lacking verbosity and completeness.

- Cannot choose which items to download by media type.

- Error handling is nearly nonexistent.
