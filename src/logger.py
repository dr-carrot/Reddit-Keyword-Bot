import re
import sys
import config
import json

logLevels = {
    "none": 0,
    "error": 1,
    "warn": 2,
    "info": 3,
    "debug": 4
}

hasShownLevelWarning = False


def log_level():
    global hasShownLevelWarning
    if config.configuration is not None and 'logLevel' in config.configuration.__dict__ and config.configuration.logLevel is not None:
        return logLevels[config.configuration.logLevel]
    if not hasShownLevelWarning:
        write_log('Log level was not provided by the configuration. Using info', logLevels['warn'], None)
        hasShownLevelWarning = True
    return logLevels['info']


def write_log(message, level, dict_msg):
    log_obj = {
        "level": level,
        "message": str(message)
    }
    if dict_msg is not None and dict_msg:
        log_obj["data"] = dict_msg
    print(json.dumps(log_obj))


def error(message, err=None, dict_msg=None):
    if log_level() >= logLevels["error"]:
        log_obj = {
            "level": "error",
            "message": str(message)
        }
        if dict_msg is not None and dict_msg:
            log_obj["data"] = dict_msg
        if err is not None and err:
            log_obj["error"] = {
                "message": str(err),
                "type": re.sub("<class '([a-zA-Z]+)'>", '\\1', str(type(err)))
            }
        sys.stderr.write(json.dumps(log_obj) + '\n')


def warn(message, dict_msg=None):
    if log_level() >= logLevels["warn"]:
        write_log(message, "warn", dict_msg)


def info(message, dict_msg=None):
    if log_level() >= logLevels["info"]:
        write_log(message, "info", dict_msg)


def debug(message, dict_msg=None):
    if log_level() >= logLevels["debug"]:
        write_log(message, "debug", dict_msg)
