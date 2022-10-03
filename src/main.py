import sys
import time
import logger
import config
import praw
import processor
import notifier
from prometheus_client import start_http_server, Counter

foundCounter = Counter('reddit_bot_found_posts', 'A count of the posts found by the reddit bot', ['subreddit'])
matchedBySubredditCounter = Counter('reddit_bot_matching_subreddit_posts',
                                    'A count of the posts matching a configured expression across configuration by '
                                    'subreddit by the reddit bot',
                                    ['subreddit'])
matchedByRuleCounter = Counter('reddit_bot_matching_posts',
                               'A count of the posts matching a configured expression by rule by the reddit bot',
                               ['rule_name'])
matchedExtrasCounter = Counter('reddit_bot_matching_posts_keys',
                               'A count of the posts matching a configured expression by the reddit bot (Includes '
                               'labels)',
                               ['subreddit', 'expression', 'rule_name'])


def create_trigger_config():
    conf = {}
    for i in range(0, len(config.configuration.scraper)):
        for item in config.configuration.scraper[i]['subreddits']:
            if item in conf:
                conf[item].append(i)
            else:
                conf[item] = [i]
    return conf, conf.keys()


def find_submissions(reddit):
    trigger_conf, subreddit_list = create_trigger_config()
    subreddits = '+'.join(subreddit_list)
    logger.info('Searching in: ' + ', '.join(subreddit_list))
    logger.debug('Begin!')
    all_key = next((x for x in subreddit_list if x.lower() == 'all'), None)
    if all_key is not None:
        logger.warn('It is assumed that any unknown key will match with queries from r/' + all_key + '!')
    try:
        error_count = 0
        while True:
            try:
                for submission in reddit.subreddit(subreddits).stream.submissions(skip_existing=True):
                    try:
                        check_key = submission.subreddit.display_name
                        if submission.subreddit.display_name not in trigger_conf and all_key is not None:
                            check_key = all_key
                            logger.info(
                                'Found new submission in ' + submission.subreddit.display_name_prefixed + ' (via r/' + all_key + '): ' + submission.title)
                        else:
                            logger.info(
                                'Found new submission in ' + submission.subreddit.display_name_prefixed + ': ' + submission.title)

                        foundCounter.labels(submission.subreddit.display_name).inc()
                        should_notify, match_data = processor.should_notify(
                            submission, trigger_conf[check_key])
                        if should_notify:
                            template_vars = {
                                'match_data': match_data,
                                'subreddit': submission.subreddit.display_name_prefixed,
                                'link': submission.shortlink
                            }
                            matchedBySubredditCounter.labels(submission.subreddit.display_name).inc()
                            for rule in trigger_conf[check_key]:
                                matchedByRuleCounter.labels(rule).inc()
                            for match in match_data:
                                matchedExtrasCounter.labels(submission.subreddit.display_name, match['expression'], match['name']).inc()
                            notifier.send_message(submission, template_vars, reddit)
                        error_count = 0
                    except KeyError as ke:
                        logger.error('Could not find subreddit. They are CASE SENSITIVE:', err=ke)
                        raise ke
                    except Exception as e:
                        logger.error('An error has occurred while consuming a submission:', err=e)
                        if config.configuration.exitOnError:
                            raise e
            except Exception as e:
                if config.configuration.exitOnError:
                    raise e
                else:
                    error_count += 1
                    if error_count > config.configuration.maxErrors:
                        logger.error('Too many errors have occurred. Raising last exception:')
                        raise e
                    else:
                        timeout = 2 ** (2 + error_count)
                        logger.error('An error has occurred. Retry ' + str(error_count) + '/' + str(
                            config.configuration.maxErrors) + ' after ' + str(timeout) + 's:', err=e)
                        time.sleep(timeout)
    except KeyError as ke:
        logger.error('Could not find subreddit. They are CASE SENSITIVE', err=ke)
    except Exception as e:
        raise e


def connect_to_reddit():
    logger.debug('login: ' + config.configuration.reddit["username"])
    reddit = praw.Reddit(
        username=config.configuration.reddit["username"],
        password=config.configuration.reddit["password"],
        client_id=config.configuration.reddit["clientId"],
        client_secret=config.configuration.reddit["clientSecret"],
        user_agent=config.configuration.reddit["userAgent"])
    user_test = reddit.user.me()
    if user_test is None:
        logger.error('Login failed!')
        sys.exit(1)
    logger.info("Login seems to have succeeded")
    return reddit


if __name__ == '__main__':
    config.initialize()
    logger.info("Configuration loaded!")
    logger.debug("Dump configuration:", dict_msg=config.safe_config())
    if config.configuration.prometheus["enabled"]:
        logger.debug('Prometheus is enabled')
        start_http_server(int(config.configuration.prometheus["port"]))
    try:
        find_submissions(connect_to_reddit())
    except KeyboardInterrupt:
        logger.info('Exited (interrupt)')
