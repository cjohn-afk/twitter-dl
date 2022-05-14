# twitterdl
A command line tool to download media from twitter profiles.

## How it works
twitdl.py takes in a list of twitter usernames as command like arguments. It then downloads all media from the given users in the current directory with all downloaded files going into their respective user folders. It also creates a database in the current directory (if not already created) which stores the user id, the username associated with the user id, and each post that is downloaded. This tool only downloads posts which are most recent than the most recently downloaded post for a given user in this database.

## Config
Currently the configuration options are limited to where the database file is stored, and setting the Twitter API bearer token which is required for this tool to work (token can be requested through dev.twitter.com). These configuration variables are stored in config.py.

## Known Issues
- User downloads happen synchronously.
    The process should happen in a multi-threaded manner in which each request user's media is downloaded at once to maximize the potential speed of completion. Currently the tool only downloads one user's media at a time which substantially increases the time to completion.
