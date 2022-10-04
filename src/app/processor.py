from . import logger
import re
from . import config


def parse_query_string(key: str) -> (str, bool, bool):
    # regex matches are case-sensitive.
    # If the string starts with // and ends with /, it isn't a regex, but an escaped slash
    if key.startswith('!!'):
        is_negated = False
        n_key = key[1:]
    elif key.startswith('!'):
        is_negated = True
        n_key = key[1:]
    else:
        is_negated = False
        n_key = key

    if n_key.startswith('~~'):
        is_case_sensitive = False
        n_key = n_key[1:]
    elif n_key.startswith('~'):
        is_case_sensitive = True
        n_key = n_key[1:]
    else:
        is_case_sensitive = False
        n_key = n_key

    if n_key.startswith('//') and n_key.endswith('/'):
        parsed = n_key[1:]
        is_regex = False
    elif n_key.startswith('/') and n_key.endswith('/') and not n_key.startswith('//'):
        parsed = n_key[1:-1]
        is_regex = True
    else:
        parsed = n_key
        is_regex = False
    return parsed, is_negated, is_regex, is_case_sensitive


def match_string(key: str, text: str):
    parsed_query, is_negated, is_regex, is_case_sensitive = parse_query_string(key)
    logger.debug('Checking query: ' + parsed_query)
    if is_case_sensitive:
        if is_regex:
            return bool(re.search(re.compile(parsed_query), text)) != is_negated
        else:
            return bool(re.search(re.compile(re.escape(parsed_query)), text)) != is_negated
    else:
        if is_regex:
            return bool(re.search(re.compile(parsed_query, re.IGNORECASE), text)) != is_negated
        else:
            return bool(re.search(re.compile(re.escape(parsed_query), re.IGNORECASE), text)) != is_negated


def check_key(cfg, text):
    or_check = False
    for orKey in cfg:
        and_check = True
        for andKey in orKey:
            and_check = and_check and match_string(andKey, text)
            if not and_check:
                # Short circuit. And block can never be true
                break
        or_check = or_check or and_check

        if or_check:
            # Short circuit. Or block will always be true
            return True, orKey
    return False, None


def should_notify(submission, config_keys):
    matched_rules = []
    for ix in config_keys:
        conf = config.configuration.scraper[ix]
        is_found, found_data, found_key = _should_notify(submission, conf)
        if is_found:
            matched_rules.append({
                "name": conf["name"],
                "expression": found_data,
                "type": found_key
            })
    return (len(matched_rules) > 0), matched_rules


def _should_notify(submission, cfg):
    is_found = False
    found_data = None
    found_key = None

    if 'title' == cfg['type']:
        is_found, found_data = check_key(cfg['expressions'], submission.title)
        if is_found:
            found_key = 'title'

    if 'body' == cfg['type'] and not is_found and 'selftext' in submission.__dict__:
        is_found, found_data = check_key(cfg['expressions'], submission.selftext)
        if is_found:
            found_key = 'body'

    if 'all' == cfg['type'] and not is_found:
        is_found, found_data = check_key(cfg['expressions'], submission.title)
        if not is_found:
            if 'selftext' in submission.__dict__:
                is_found, found_data = check_key(cfg['expressions'], submission.selftext)
                if is_found:
                    found_key = 'all (body)'
        else:
            found_key = 'all (title)'

    return is_found, found_data, found_key


def _replace_for_query(text: str, query: str, replRegex: str) -> str:
    parsed_query, is_negated, is_regex, is_case_sensitive = parse_query_string(query)
    if is_negated:
        return text
    if is_case_sensitive:
        if is_regex:
            return re.sub(re.compile('(' + parsed_query + ')'), replRegex, text)
        return re.sub(re.compile('(' + re.escape(parsed_query) + ')'), replRegex, text)
    else:
        if is_regex:
            return re.sub(re.compile('(' + parsed_query + ')', re.IGNORECASE), replRegex, text)
        return re.sub(re.compile('(' + re.escape(parsed_query) + ')', re.IGNORECASE), replRegex, text)


def find_and_replace_by_expression(text: str, match_data):
    for match in match_data:
        for query in match['expression']:
            text = _replace_for_query(text, query, '__\\1__')
    return text
