# twitter-dl
A command line tool to download media from twitter profiles.
## How it works
It can take in one or more usernames as command line arguments or a text file containing a list of newline separated usernames or both, and it will retrieve the media from each account. You may choose to download videos, photos, or both (default). You also have the option of limiting your download to media that is newer than the newest media you've already downloaded. \
\
A [Twitter API](https://developer.twitter.com/en/docs/twitter-api) bearer token is required. In the future I may include an option to gather media using web scraping which does not require direct API access. \
\
Please don't hesitate to file an issue if you have any problems using this tool or have a suggestion to improve it.

## Configuration
Upon first execution, twitter-dl creates a directory at *~/.config/twitter-dl* in which it stores two files.
- '*twitter-dl.db*': an sqlite database containing information about downloaded tweets.
- '*bearer_token*': used to store the bearer token.
