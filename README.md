# twitter-dl
A command line tool to download media from twitter profiles.

## How it works
twitter-dl is a tool that allows you to download media from twitter profiles. It can take one or more username via command line or list file and download all media associated with the sepcified account(s). Several options exist to tailor what will be downloaded from the twitter profile. You may choose to only download photos, videos or both (default). There is also an option to 'update', which will only download media which is newer than the most recent previously downloaded media. Keep in mind that a Twitter API bearer token is required for this tool to work.

## Config
Upon its first execution twitter-dl creates a directory at ~/.config/twitter-dl in which it stores two files. The first file is 'twitter-dl.db', an sqlite database containing information about downloaded tweets. The second file is 'bearer_token', a file that contains a Twitter API bearer token. The bearer_token file is only created when a bearer token is supplied using the --bearer-token argument (i.e. twitter-dl --bearer-token=[YOUR BEARER TOKEN]).
