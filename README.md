# Redit Keyword Bot
A moderately simple app to trigger notifications based on reddit submissions to different subreddits based on a set of rules

# Instructions:
## Running the bot
### Docker Compose
Grab the `examples/docker-compose.yaml` file and do the standard `docker-compose up`

### Kubernetes
Grab the `examples/kubernetes.yaml` file and edit it to suit your needs. Then just apply it to your cluster

### Straight up
Just run `main.py`

## Configuration
### Via file
The bot will try to pick up a config.yaml file from its working directory. An alternate file location can be specified with the environment variable: `BOT_CONFIG_PATH`. Alternatively, all options can be specified as environment variables.
For a given yaml property, the corresponding environment variable takes the form `BOT_DICTPATH1_DICTPATH2_CONFIGNAME`
So the property `reddit.clientId` would be `BOT_REDDIT_CLIENTID` and `notification.discord.webhook` would be `BOT_NOTIFICATION_DISCORD_WEBHOOK`
The app must be restarted when the configuration is changed. Items in the config file are OVERWRITTEN by their corresponding environment variable

### Reddit Configuration `reddit.* (BOT_REDDIT_*)`
To get the client id and client secret from new reddit, go to [your username > user settings > safety and privacy > manage third-party app authorization](https://www.reddit.com/prefs/apps) > create new app. Make sure you select "script". Call the bot whatever you like, and in the "redirect uri" box, enter "http://localhost:8080" (or whatever port you exposed). Then click create. The client id is in the upper left of the box  under "personal use script" and the secret is labeled.
* `reddit.username (BOT_REDDIT_USERNAME)` - The username for the bot to use to find submissions
* `reddit.password (BOT_REDDIT_PASSWORD)` - The password for the bot to use
* `reddit.clientId (BOT_REDDIT_CLIENTID)` - The clientId of the bot
* `reddit.clientSecret (BOT_REDDIT_CLIENTSECRET)` - The client secret of the bot
* `reddit.userAgent (BOT_REDDIT_USERAGENT)` (optional) - The user agent to use. You don't need to set this

### Scraper Configuration
The bot can search submission bodies, titles, or both at once, configured by the `scraper` property. This one doesn't translate very well to an env var, but you could alternatively specify `scraperJson (BOT_SCRAPERJSON)` which works better in this case.
From the top level scraper property, you can specify your subreddit names, omitting the 'r/'. Remember, **_SUBREDDITS ARE CASE SENSITIVE_**. From the subreddit key, depending on what you want to filter by, you should specify `title` for titles, `body` for bodies, and/or `all` to match both title and body.
Each search category is a list of lists. The first list is an or group. The nested list is an and group. The submission will trigger a notification if all the items in the nested list match for any of the top-level lists.
Check out example/sample.yaml for a good demo of what to do and how to do it
The and lists are a list of strings. There are some fancy features:
* You can use a regular old string. These are case-insensitive
* You can use a regular expression by starting and ending your string with '/'. Partial matching is used, so use '/^' and '$/' to match the whole thing). These are case-sensitive. If you want to specify a string that is enclosed in '/', but not a regular expression, you can start it with '//' 
* You can negate the string by starting it with an '!'. This works for regex and regular strings. You can escape the '!' with '!!' and it will not count as negated 
Instead of providing this configuration in yaml form, you can specify the `scraperJson (BOT_SCRAPERJSON)` property and provide a json string of the configuration


### Misc options
* `exitOnError (BOT_EXITONERROR)` (default 'false') - When set to true, allows application to crash if an error occurs
* `logLevel (BOT_LOG_LEVEL)` (default 'warn') - The log level. Should be one of none, error, warn, info, or debug
* `maxErrors (BOT_MAXERROR)]` (default 8) - The amount of consecutive errors allowed, after which the bot will exit

### Notification delivery types
These are set in `notification.* (BOT_NOTIFICATION_*)` section of the config.

#### Discord `notification.discord.* (BOT_NOTIFICATION_DISCORD_*`
* `notification.discord.webhook (BOT_NOTIFICATION_DISCORD_WEBHOOK)` - The webhook url. [Instructions can be found here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

#### Reddit `notification.reddit.* (BOT_NOTIFICATION_REDDIT_*`
* `notification.reddit.username (BOT_NOTIFICATION_REDDIT_USERNAME` - The username of the account to send the message to

## Troubleshooting
* Raise an issue here on Github
* Try [r/redditdev](https://www.reddit.com/r/redditdev)
* Get good
