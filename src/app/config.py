import copy
import json
import os
from os import path
import yaml
from collections.abc import MutableMapping
import sys

from . import logger

DEFAULT_MESSAGE_BODY_TEMPLATE = 'A post was found matching your search criteria in $subreddit: $link'
DEFAULT_MESSAGE_SUBJECT_TEMPLATE = 'A post was found in $subreddit'
DEFAULT_MAX_ERRORS = 12
botDebugMode = False

configuration = None


class BotProperties:

    def __init__(self, **data):
        self.reddit = {
            "username": None,
            "password": None,
            "clientId": None,
            "clientSecret": None,
            "userAgent": "u/drCarrotson\'s Message Notification Bot"
        }
        self.configVersion = 1
        self.scraper = None
        self.logLevel = 'warn'
        self.redditClient = 'default'
        self.prometheus = {
            "enabled": False,
            "port": 9090
        }
        self.notification = {
            "discord": {
                "webhook": None
            },
            "reddit": {
                "username": None
            }
        }
        self.scraperJson = ''
        self.exitOnError = False
        self.maxErrors = 8
        if data:
            self.__dict__.update(data)
            if (self.scraperJson is not None or self.scraperJson != '') and self.scraper is None:
                self.scraper = json.loads(self.scraperJson)

    def verify(self):
        has_issues = False

        items = flatten(self.__dict__)
        for key, value in items.items():
            if value is None:
                logger.error(
                    'Missing value for required attribute: ' + '.'.join(key.split('_')) + ', Environment variable: ' + to_env_var(key))
                has_issues = True
        if self.scraper is not None:
            for ix in range(0, len(self.scraper)):
                item = self.scraper[ix]
                if 'name' not in item:
                    has_issues = True
                    logger.error("Missing a 'name' value for scraper profile at index " + str(ix))
                if 'type' not in item:
                    has_issues = True
                    logger.error("Missing a 'type' value for scraper profile at index " + str(ix))
                if 'subreddits' not in item:
                    has_issues = True
                    logger.error("Missing a 'subreddits' value for scraper profile at index " + str(ix))
                if 'expressions' not in item:
                    has_issues = True
                    logger.error("Missing an 'expression' value for scraper profile at index " + str(ix))
        if has_issues:
            sys.exit(1)


def to_env_var(parent, var_path=None, prefix='bot'):
    if var_path is not None:
        return (prefix + '_' + parent + '_' + var_path).upper()
    return (prefix + '_' + parent).upper()


def flatten(d, parent_key='', sep='_'):
    items = []
    if type(d) is not dict:
        return d
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def apply_value_to_dict_path(dict_ref, prop_list, value):
    if len(prop_list) == 1:
        dict_ref[prop_list[0]] = value
        return
    if prop_list[0] not in dict_ref:
        dict_ref[prop_list[0]] = {}
    apply_value_to_dict_path(dict_ref[prop_list[0]], prop_list[1:], value)


def merge(a, b, obj_path=None):
    if obj_path is None:
        obj_path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], obj_path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif b[key] is not None:
                a[key] = b[key]

    return a


def safe_config():
    cpy = copy.deepcopy(configuration.__dict__)
    cpy['reddit']['password'] = '[REDACTED]'
    cpy['reddit']['clientSecret'] = '[REDACTED]'
    return cpy


def initialize():
    global configuration
    configuration = BotProperties()
    config_path = os.environ.get('BOT_CONFIG_PATH', 'redditbot.yaml')
    env_dict = {}
    if path.exists(config_path):
        with open(config_path) as f:
            data = yaml.safe_load(f)
            env_dict = merge(configuration.__dict__, data)
    # Load the env vars. Replace any config file properties
    for key, value in flatten(configuration.__dict__).items():
        env_val = os.environ.get(to_env_var(key), value)
        if env_val is not None and env_val != '':
            apply_value_to_dict_path(env_dict, key.split('_'), env_val)

    # Convert an inline json config to a dictionary
    if (configuration.scraperJson is not None and configuration.scraperJson != '') and configuration.scraper is None:
        configuration.scraper = json.loads(configuration.scraperJson)

    # If any of the notifications are missing required fields, delete the config
    for key, value in flatten(configuration.notification).items():
        if value is None:
            configuration.notification.pop(key.split('_')[0], None)
        else:
            logger.info("Using Notification service: " + key.split('_')[0])

    configuration.verify()
