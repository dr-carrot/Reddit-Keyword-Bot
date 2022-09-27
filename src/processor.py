import logger
import re


def match_string(key, text):
    # regex matches are case-sensitive.
    # If the string starts with // and ends with /, it isn't a regex, but an escaped slash
    if key.startswith('!'):
        is_negated = True
        n_key = key[1:]
    else:
        is_negated = False
        n_key = key

    if n_key.startswith('//') and n_key.endswith('/'):
        return (n_key[1:].lower() in text.lower()) != is_negated
    if n_key.startswith('/') and n_key.endswith('/') and not n_key.startswith('//'):
        logger.debug('Checking regex: ' + n_key[1:-1])
        return bool(re.search(re.compile(n_key[1:-1]), text)) != is_negated
    else:
        return (n_key.lower() in text.lower()) != is_negated


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


def should_notify(submission, cfg):
    if len(cfg) == 0:
        return True, None

    is_found = False
    found_data = None
    found_key = None

    if 'title' in cfg:
        is_found, found_data = check_key(cfg['title'], submission.title)
        if is_found:
            found_key = 'title'

    if 'body' in cfg and not is_found:
        is_found, found_data = check_key(cfg['body'], submission.body)
        if is_found:
            found_key = 'body'

    if 'all' in cfg and not is_found:
        is_found, found_data = check_key(cfg['all'], submission.title)
        if not is_found:
            is_found, found_data = check_key(cfg['all'], submission.body)
            if is_found:
                found_key = 'all (body)'
        else:
            found_key = 'all (title)'

    return is_found, found_data, found_key
