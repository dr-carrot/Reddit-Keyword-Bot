import json
import unittest
from unittest.mock import patch, MagicMock

from src.app import notifier
from src.app import config
from src.app import processor
from src.app.config import BotProperties
from tests.mocks import SubmissionMock, create_submission


class TestNotifier(unittest.TestCase):

    def test_clamp_text(self):
        self.assertEqual(2048, len(notifier.clamp_text('a' * 3000)))

    def test_send_message_no_notifiers(self):
        config.configuration = config.BotProperties()
        config.configuration.notification = {}
        template_vars = {

        }
        with patch('src.app.notifier.send_to_reddit', MagicMock()) as strMock, patch('src.app.notifier.send_to_discord', MagicMock()) as stdMock:
            notifier.send_message(create_submission(), template_vars, None)
            strMock.assert_not_called()
            stdMock.assert_not_called()

    def test_send_message_reddit(self):
        config.configuration = config.BotProperties()
        config.configuration.notification = {
            'reddit': {}
        }
        template_vars = {
            'expressions': '',
            'match_data': '',
            'link': '',
            'subreddit': ''
        }
        with patch('src.app.notifier.send_to_reddit', MagicMock()) as strMock, patch('src.app.notifier.send_to_discord', MagicMock()) as stdMock:
            notifier.send_message(create_submission(), template_vars, None)
            strMock.assert_called()
            stdMock.assert_not_called()

    def test_send_message_discord(self):
        config.configuration = config.BotProperties()
        config.configuration.notification = {
            'discord': {}
        }
        template_vars = {

        }
        with patch('src.app.notifier.send_to_reddit', MagicMock()) as strMock, patch('src.app.notifier.send_to_discord', MagicMock()) as stdMock:
            notifier.send_message(create_submission(), template_vars, None)
            strMock.assert_not_called()
            stdMock.assert_called()

class TestRedditNotifier(unittest.TestCase):
    def test_send_to_reddit(self):
        config.configuration = BotProperties()
        config.configuration.notification = {
            'reddit': {
                'username': 'test'
            }
        }
        with patch('praw.reddit', MagicMock()) as redditMock:
            redditMock.redditor = MagicMock()
            notifier.send_to_reddit('', '', redditMock)
            redditMock.redditor.assert_called_once()

    def test_send_to_reddit_error(self):
        config.configuration = BotProperties()
        config.configuration.notification = {
            'reddit': {
                'username': 'test'
            }
        }
        with patch('praw.reddit', MagicMock()) as redditMock, patch('time.sleep', MagicMock()) as sleep, patch('json.dumps', MagicMock(return_value='{}')):
            redditMock.redditor = MagicMock(side_effect=Exception())
            notifier.send_to_reddit('', '', redditMock)
            sleep.assert_called_once()



class TestDiscordNotifier(unittest.TestCase):
    def test_send_to_discord(self):
        template_vars = {
            'expressions': '',
            'match_data': '',
            'link': '',
            'subreddit': ''
        }
        sub = create_submission()
        sub.selftext = 'test'
        sub.shortlink = 'test.com'
        sub.created_utc = 1665255745
        sub.author = MagicMock()
        sub.author.name = 'testauthor'
        sub.subreddit.icon_img = 'testimg'
        sub.subreddit.url = '/testurl'
        config.configuration = BotProperties()
        config.configuration.notification = {
            'discord': {
                'webhook': 'testhook.discord.com'
            }
        }
        resp = MagicMock()
        resp.status_code = 200
        resp.text = 'test'
        with patch('requests.post', MagicMock(return_value=resp)) as postMock:
            notifier.send_to_discord(sub, template_vars)
            postMock.assert_called_once()
            self.assertTrue('https://www.reddit.com/testurl' in postMock.call_args[1]['data'])

    def test_send_to_discord_old_reddit(self):
        template_vars = {
            'expressions': '',
            'match_data': '',
            'link': '',
            'subreddit': ''
        }
        sub = create_submission()
        sub.selftext = 'test'
        sub.shortlink = 'test.com'
        sub.created_utc = 1665255745
        sub.author = MagicMock()
        sub.author.name = 'testauthor'
        sub.subreddit.icon_img = 'testimg'
        sub.subreddit.url = '/testurl'
        sub.id = 'testid'
        config.configuration = BotProperties()
        config.configuration.redditClient = 'old'
        config.configuration.notification = {
            'discord': {
                'webhook': 'testhook.discord.com'
            }
        }
        resp = MagicMock()
        resp.status_code = 200
        resp.text = 'test'
        with patch('requests.post', MagicMock(return_value=resp)) as postMock:
            notifier.send_to_discord(sub, template_vars)
            postMock.assert_called_once()
            self.assertTrue('https://old.reddit.com/testurl/comments/testid' in postMock.call_args[1]['data'])

    def test_send_to_discord_apollo(self):
        template_vars = {
            'expressions': '',
            'match_data': '',
            'link': '',
            'subreddit': ''
        }
        sub = create_submission()
        sub.selftext = 'test'
        sub.shortlink = 'test.com'
        sub.created_utc = 1665255745
        sub.author = MagicMock()
        sub.author.name = 'testauthor'
        sub.subreddit.icon_img = 'testimg'
        sub.subreddit.url = '/testurl'
        sub.id = 'testid'
        config.configuration = BotProperties()
        config.configuration.redditClient = 'apollo'
        config.configuration.notification = {
            'discord': {
                'webhook': 'testhook.discord.com'
            }
        }
        resp = MagicMock()
        resp.status_code = 200
        resp.text = 'test'
        with patch('requests.post', MagicMock(return_value=resp)) as postMock:
            notifier.send_to_discord(sub, template_vars)
            postMock.assert_called_once()
            self.assertTrue('https://openinapollo.com?subreddit=test&postID=testid' in postMock.call_args[1]['data'])

    def test_send_to_discord_429(self):
        template_vars = {
            'expressions': '',
            'match_data': '',
            'link': '',
            'subreddit': ''
        }
        sub = create_submission()
        sub.selftext = 'test'
        sub.shortlink = 'test.com'
        sub.created_utc = 1665255745
        sub.author = MagicMock()
        sub.author.name = 'testauthor'
        sub.subreddit.icon_img = 'testimg'
        sub.subreddit.url = 'testurl'
        config.configuration = BotProperties()
        config.configuration.notification = {
            'discord': {
                'webhook': 'testhook.discord.com'
            }
        }
        resp = MagicMock()
        resp.status_code = 429
        resp.text = 'test'
        resp.json = MagicMock(return_value={'retry_after': 10})
        with patch('requests.post', MagicMock(return_value=resp)) as postMock, patch('time.sleep', MagicMock()) as timeMock:
            notifier.send_to_discord(sub, template_vars)
            postMock.assert_called_once()
            self.assertEqual(2, timeMock.call_count)

if __name__ == '__main__':
    unittest.main()
