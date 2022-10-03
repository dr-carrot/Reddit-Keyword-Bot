# Redit Keyword Bot
A moderately simple app to trigger notifications based on reddit submissions to different subreddits based on a set of rules


[discord.png](pics/img.png)
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
From the top level scraper property, you can specify a list of scraper profiles. Each profile contains a name, list of subreddits, a type, and a list of expressions to match against. For example:
```yaml
- name: Profile 1 # The name of the profile
  type: title # the type of matcher to use (title|body|all)
  subreddits: # List of subreddits to watch
    - pics
    - illegallysmolanimals
  expressions: # List of expressions
    - - cat # This is a 2d list. The lowest level list contains one string: 'cat'
    - - kitten
      - !chonk
```
Remember, **_SUBREDDITS ARE CASE SENSITIVE_** and DO NOT include 'r/'. You can choose to match the submission title, boy or both by specifying `title` for titles, `body` for bodies, and/or `all` to match both title and body.
The expressions are is a lists of lists. The first list is an or group. The nested list is an and group. The submission will trigger a notification if all the items in the nested list match for any of the top-level lists.
Check out example/sample.yaml for a good demo of what to do and how to do it
The and lists are a list of strings. They are case-insensitive unless configured otherwise. There are some fancy features:
* You can use a regular old string.
* You can use a regular expression by starting and ending your string with '/'. Partial matching is used, so use '/^' and '$/' to match the whole thing). If you want to specify a string that is enclosed in '/', but not a regular expression, you can start it with '//' 
* You can make regex or simple string match case-sensitive by starting it with '~'
* You can negate the string by starting it with an '!'. This works for regex and regular strings. You can escape the '!' with '!!' and it will not count as negated. Negation should *always* be the first character (before '~')
Instead of providing this configuration in yaml form, you can specify the `scraperJson (BOT_SCRAPERJSON)` property and provide a json string of the configuration


### Misc options
* `exitOnError (BOT_EXITONERROR)` (default 'false') - When set to true, allows application to crash if an error occurs
* `logLevel (BOT_LOG_LEVEL)` (default 'warn') - The log level. Should be one of none, error, warn, info, or debug
* `maxErrors (BOT_MAXERROR)` (default 8) - The amount of consecutive errors allowed, after which the bot will exit
* `redditClient (BOT_REDDITCLIENT)` (default `None`) - The reddit client to configure links for. Can be `None`/'default' (new reddit), 'old' (old reddit), or 'apollo' (Apollo for reddit) 

### Notification delivery types
These are set in `notification.* (BOT_NOTIFICATION_*)` section of the config.

#### Discord `notification.discord.* (BOT_NOTIFICATION_DISCORD_*`
* `notification.discord.webhook (BOT_NOTIFICATION_DISCORD_WEBHOOK)` - The webhook url. [Instructions can be found here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

#### Reddit `notification.reddit.* (BOT_NOTIFICATION_REDDIT_*`
* `notification.reddit.username (BOT_NOTIFICATION_REDDIT_USERNAME` - The username of the account to send the message to

## Troubleshooting
* Raise an issue here on Github
* Try [r/redditdev](https://www.reddit.com/r/redditdev)
