import unittest
from src.app import processor
from src.app import config
from unittest.mock import MagicMock
from praw.models import Submission


class ParserTests(unittest.TestCase):

    def test_query_parser_simple_string(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('Hello')
        self.assertEqual('hello', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_simple_string_case_sensitive(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('~Hello')
        self.assertEqual('Hello', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertTrue(is_case_sensitive)

    def test_query_parser_simple_string_case_insensitive_negated(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!Hello')
        self.assertEqual('hello', parsed)
        self.assertTrue(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_simple_string_case_escaped_negated(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!!Hello')
        self.assertEqual('!hello', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_simple_string_case_sensitive_negated(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!~Hello')
        self.assertEqual('Hello', parsed)
        self.assertTrue(is_negated)
        self.assertFalse(is_regex)
        self.assertTrue(is_case_sensitive)

    def test_query_parser_simple_string_case_insensitive_escaped_negation(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!!~Hello')
        self.assertEqual('!~hello', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_regex(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('/Hello.?World/')
        self.assertEqual('hello.?world', parsed)
        self.assertFalse(is_negated)
        self.assertTrue(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_regex_case_sensitive(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('~/Hello.?World/')
        self.assertEqual('Hello.?World', parsed)
        self.assertFalse(is_negated)
        self.assertTrue(is_regex)
        self.assertTrue(is_case_sensitive)

    def test_query_parser_regex_negated(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!/Hello.?World/')
        self.assertEqual('hello.?world', parsed)
        self.assertTrue(is_negated)
        self.assertTrue(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_regex_escaped_negated(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!!/Hello.?World/')
        self.assertEqual('!/hello.?world/', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_non_regex_escaped_negation(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('!!~/Hello.?World/')
        self.assertEqual('!~/hello.?world/', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_simple_string_escaped_case_sensitive(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('~~Hello World')
        self.assertEqual('~Hello World', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)

    def test_query_parser_simple_string_escaped_regex(self):
        parsed, is_negated, is_regex, is_case_sensitive = processor.parse_query_string('//Hello World/')
        self.assertEqual('/hello world/', parsed)
        self.assertFalse(is_negated)
        self.assertFalse(is_regex)
        self.assertFalse(is_case_sensitive)


class MatchStringTests(unittest.TestCase):

    def test_match_string_simple_string(self):
        is_match = processor.match_string('hello', 'Hello world, how is it going?')
        self.assertTrue(is_match)

    def test_match_string_simple_string_fail(self):
        is_match = processor.match_string('hullo', 'Hello world, how is it going?')
        self.assertFalse(is_match)

    def test_match_string_simple_string_negated(self):
        is_match = processor.match_string('!hello', 'Hello world, how is it going?')
        self.assertFalse(is_match)

    def test_match_string_simple_string_fail_negated(self):
        is_match = processor.match_string('!hullo', 'Hello world, how is it going?')
        self.assertTrue(is_match)

    def test_match_string_simple_string_case_sensitive_fail(self):
        is_match = processor.match_string('~hello', 'Hello world, how is it going?')
        self.assertFalse(is_match)

    def test_match_string_simple_string_case_sensitive(self):
        is_match = processor.match_string('~Hello', 'Hello world, how is it going?')
        self.assertTrue(is_match)

    def test_match_string_regex(self):
        is_match = processor.match_string('/(is|anyone|there) ?[a-zA-Z]+.*\\?$/', 'Hello world, how is it going?')
        self.assertTrue(is_match)

    def test_match_string_regex_negated(self):
        is_match = processor.match_string('!/(is|anyone|there) ?[a-zA-Z]+.*\\?$/', 'Hello world, how is it going?')
        self.assertFalse(is_match)

    def test_match_string_regex_fail(self):
        is_match = processor.match_string('/^(is|anyone|there) ?[a-zA-Z]+.*\\?$/', 'Hello world, how is it going?')
        self.assertFalse(is_match)

    def test_match_string_regex_fail_negated(self):
        is_match = processor.match_string('!/^(is|anyone|there) ?[a-zA-Z]+.*\\?$/', 'Hello world, how is it going?')
        self.assertTrue(is_match)


class CheckKeyTests(unittest.TestCase):

    def test_check_key(self):
        processor.match_string = MagicMock(side_effect=[False, True])
        is_match, data = processor.check_key([['hello', 'world'], ['yellow']], 'Hello World!')
        self.assertTrue(is_match)
        self.assertEqual(['yellow'], data)
        processor.match_string.assert_called()

    def test_check_key_empty(self):
        processor.match_string = MagicMock(side_effect=[False, True])
        # processor.match_string.assert_has_calls(any_order=True)
        is_match, data = processor.check_key([], 'Hello World!')
        self.assertFalse(is_match)
        self.assertEqual(None, data)
        processor.match_string.assert_not_called()


class ShouldNotifyTests(unittest.TestCase):
    def setUp(self) -> None:
        config.configuration = config.BotProperties()
        config.configuration.scraper = [
            {
                'name': 'test',
                'subreddits': [],
                'expressions': []
            }
        ]

    def test_should_notify_body(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'body'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(True, ['TEST RETURN'])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertTrue(should_notify)
        self.assertEqual(1, len(matched_rules))
        processor.check_key.assert_called_once()

    def test_should_notify_body_fail(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'body'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(False, [])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertFalse(should_notify)
        self.assertEqual(0, len(matched_rules))
        processor.check_key.assert_called_once()

    def test_should_notify_title(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'title'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(True, ['TEST RETURN'])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertTrue(should_notify)
        self.assertEqual(1, len(matched_rules))
        processor.check_key.assert_called_once()

    def test_should_notify_title_fail(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'title'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(False, [])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertFalse(should_notify)
        self.assertEqual(0, len(matched_rules))
        processor.check_key.assert_called_once()

    def test_should_notify_all_title(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'all'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(True, ['TEST RETURN'])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertTrue(should_notify)
        self.assertEqual(1, len(matched_rules))
        self.assertEqual('all (title)', matched_rules[0]['type'])
        processor.check_key.assert_called_once()

    def test_should_notify_all_title_fail(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'all'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(False, []), (False, [])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertFalse(should_notify)
        self.assertEqual(0, len(matched_rules))
        self.assertEqual(2, processor.check_key.call_count)

    def test_should_notify_all_body(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'all'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(False, []), (True, ['TEST RETURN'])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertTrue(should_notify)
        self.assertEqual(1, len(matched_rules))
        self.assertEqual('all (body)', matched_rules[0]['type'])
        self.assertEqual(2, processor.check_key.call_count)

    def test_should_notify_all_body_fail(self):
        sub = MagicMock()
        config.configuration.scraper[0]['type'] = 'body'
        sub.__setattr__('selftext', 'Hello world, how is it going?')
        sub.__setattr__('title', 'Yo yo yo, what\'s poppin\' B?')
        processor.check_key = MagicMock(side_effect=[(False, []), (False, [])])

        should_notify, matched_rules = processor.should_notify(sub, [0])
        self.assertFalse(should_notify)
        self.assertEqual(0, len(matched_rules))
        processor.check_key.assert_called_once()


class FindAndReplaceByExpressionTests(unittest.TestCase):

    def test_find_and_replace_by_expression(self):
        conf = [
            {'expression': ['yellow', '!orange']}
        ]
        replaced = processor.find_and_replace_by_expression('Hello world, how is it going? Is it yellow?', conf)
        self.assertEqual('Hello world, how is it going? Is it __yellow__?', replaced)

    def test_find_and_replace_by_expression_regex(self):
        conf = [
            {'expression': ['/i[st] ?/']}
        ]
        replaced = processor.find_and_replace_by_expression('Hello world, how is it going? Is it yellow?', conf)
        self.assertEqual('hello world, how __is ____it __going? __is ____it __yellow?', replaced)

    def test_find_and_replace_by_expression_regex_complex(self):
        conf = [
            {'expression': ['/s ?/', '~Hello', 'lo']},
        ]
        replaced = processor.find_and_replace_by_expression('Hello world, how is it going? Is it yellow?', conf)
        self.assertEqual('hel__lo__ world, how i__s __it going? i__s __it yel__lo__w?', replaced)

    def test_find_and_replace_by_expression_regex_case_sensitive(self):
        conf = [
            {'expression': ['~/H/']},
        ]
        replaced = processor.find_and_replace_by_expression('Hello world, how is it going? Is it yellow?', conf)
        self.assertEqual('__H__ello world, how is it going? Is it yellow?', replaced)


if __name__ == '__main__':
    unittest.main()
