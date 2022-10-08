import unittest
from unittest.mock import patch, MagicMock

from src.app import main
from src.app import config
from src.app.config import BotProperties

from tests.mocks import SubmissionMock, create_reddit, create_submission


class TestUtilities(unittest.TestCase):
    def test_create_trigger_config(self):
        config.configuration = BotProperties()
        config.configuration.scraper = [
            {
                'subreddits': [
                    's1',
                    's2'
                ]
            },
            {
                'subreddits': [
                    's3',
                    's4'
                ]
            }
        ]
        conf, keys = main.create_trigger_config()
        self.assertEqual(4, len(keys))
        self.assertEqual({'s1': [0], 's2': [0], 's3': [1], 's4': [1]}, conf)

    @patch('praw.Reddit')
    def test_connect_to_reddit(self, reddit):
        config.configuration = BotProperties()
        config.configuration.reddit = {
            'username': 'test',
            'password': 'password',
            'clientId': 'clientid',
            'clientSecret': 'secret',
            'userAgent': 'agent'
        }
        conn = main.connect_to_reddit()
        self.assertIsNotNone(conn)


class TestFindSubmissions(unittest.TestCase):

    @patch('src.app.processor')
    def test_find_submissions(self, procMock):
        config.configuration = BotProperties()
        config.configuration.scraper = [

        ]
        reddit_mock = SubmissionMock([''])
        config.configuration.exitOnError = True
        with patch('src.app.main.process_submission', MagicMock(side_effect=Exception())):
            self.assertRaises(Exception, main.find_submissions, reddit_mock)


class TestProcessSubmission(unittest.TestCase):

    def test_process_submission_not_matched(self):
        triggerConf = {
            'test': [0]
        }
        with patch('src.app.processor.should_notify', MagicMock(return_value=(False, None))), patch(
                'src.app.notifier.send_message', MagicMock()) as noteMock:
            main.process_submission(create_reddit(), create_submission(), triggerConf, 'all')
            noteMock.assert_not_called()

    def test_process_submission_matched(self):
        triggerConf = {
            'test': [0]
        }
        match_data = [{
            'expression': '',
            'name': ''
        }]
        with patch('src.app.processor.should_notify', MagicMock(return_value=(True, match_data))), patch(
                'src.app.notifier.send_message', MagicMock()) as noteMock:
            main.process_submission(create_reddit(), create_submission(), triggerConf, 'all')
            noteMock.assert_called()

    def test_process_submission_matched_all(self):
        triggerConf = {
            'all': [0]
        }
        match_data = [{
            'expression': '',
            'name': ''
        }]
        with patch('src.app.processor.should_notify', MagicMock(return_value=(True, match_data))), patch(
                'src.app.notifier.send_message', MagicMock()) as noteMock:
            main.process_submission(create_reddit(), create_submission(), triggerConf, 'all')
            noteMock.assert_called()

    def test_process_submission_key_error(self):
        triggerConf = {
            'toast': [0]
        }
        match_data = [{
            'expression': '',
            'name': ''
        }]
        with patch('src.app.processor.should_notify', MagicMock(return_value=(True, match_data))), patch(
                'src.app.notifier.send_message', MagicMock()) as noteMock:
            self.assertRaises(KeyError, main.process_submission, create_reddit(), create_submission(), triggerConf,
                              'all')
            noteMock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
