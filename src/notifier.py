import time
import datetime
import config
import logger
import json
import requests
from string import Template
from datetime import datetime, timezone

DEFAULT_MESSAGE_BODY_TEMPLATE = 'A post was found matching your search criteria in $subreddit: $link'
DEFAULT_MESSAGE_SUBJECT_TEMPLATE = 'A post was found in $subreddit'


def send_to_reddit(subject, body, reddit):
    try:
        reddit.redditor(config.configuration.notification["reddit"]["username"]).message(subject, body)
        logger.info('Sent new reddit message: ' + subject, dict_msg=body)
    except Exception as e:
        logger.error('Error sending message to reddit user: ', err=e)
        time.sleep(60)


def clamp_text(text, limit=2048):
    return text[:(limit - 4)] + (text[(limit - 4):] and '...')


def send_to_discord(submission):
    try:
        headers = {'Content-Type': 'application/json'}
        if hasattr(submission, 'url_overridden_by_dest') and submission.url_overridden_by_dest != '':
            desc = '[' + submission.domain + '](' + submission.url_overridden_by_dest + ')'
        else:
            desc = clamp_text(submission.selftext)
        if hasattr(submission.subreddit, 'icon_img') and submission.subreddit.icon_img != '':
            img = submission.subreddit.icon_img
        elif 'community_icon' in vars(submission.subreddit) and submission.subreddit.community_icon != '':
            img = submission.subreddit.community_icon
        else:
            img = 'https://i.redd.it/qupjfpl4gvoy.jpg'

        if 'key_color' in vars(submission.subreddit) and submission.subreddit.key_color != '':
            color = int(submission.subreddit.key_color[1:], 16)
        else:
            color = 1127128

        payload = {"embeds": [
            {
                "color": color,
                "author": {
                    "name": submission.subreddit.display_name_prefixed,
                    "url": 'https://www.reddit.com' + submission.subreddit.url,
                    "icon_url": img
                },
                "title": clamp_text(submission.title, limit=256),
                "description": desc,
                "url": submission.shortlink,
                "timestamp": datetime.fromtimestamp(submission.created_utc, timezone.utc).isoformat().replace('+00:00',
                                                                                                              'Z'),
                "footer": {
                    "text": 'u/' + submission.author.name
                }
            }
        ]}
        logger.debug('Payload:', dict_msg=payload)
        logger.debug('Post to webhook: ' + config.configuration.notification['discord']['webhook'])
        response = requests.post(
            config.configuration.notification['discord']['webhook'], data=json.dumps(payload), headers=headers)

        logger.debug("Got response from discord", {"code": response.status_code, "text": response.text})
        logger.info('Sent new discord message for post: ' + desc)
        if response.status_code == 429:
            logger.warn('too many requests')
            jsn = response.json()
            logger.info('sleeping for:' + str(jsn['retry_after']))
            time.sleep(float(jsn['retry_after']))
        elif response.status_code >= 400:
            raise Exception('Failed to send discord hook! Got code: ' + str(response.status_code))
        # try to evade rate limiting
        time.sleep(2)
    except Exception as e:
        raise e


def send_message(submission, template_vars, reddit):
    try:
        logger.debug('Found new notification in ' + submission.subreddit.display_name_prefixed, dict_msg=template_vars)

        if 'reddit' in config.configuration.notification:
            subject = Template(DEFAULT_MESSAGE_SUBJECT_TEMPLATE).substitute(template_vars)
            body = Template(DEFAULT_MESSAGE_BODY_TEMPLATE).substitute(template_vars)
            send_to_reddit(subject, body, reddit)
        if 'discord' in config.configuration.notification:
            send_to_discord(submission)
    except Exception as e:
        logger.error('Could not send message', err=e)
        raise e
