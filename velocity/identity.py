import re
from datetime import datetime, timedelta, timezone

METRICS = (
    "retweet_count",
    "quote_count",
    "like_count",
    "reply_count",
    "impression_count",
    "bookmark_count",
)
OPS = (">", ">=", "=", "<=", "<")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_POST_ID = re.compile(r"^[0-9]+$")


def parse_time(value):
    if type(value) is not str or _TIME.fullmatch(value) is None:
        raise ValueError("check_time")
    try:
        parsed = datetime.strptime(value, TIME_FORMAT)
    except ValueError:
        raise ValueError("check_time") from None
    return parsed.replace(tzinfo=timezone.utc)


def format_time(value):
    return value.astimezone(timezone.utc).strftime(TIME_FORMAT)


def add_seconds(stamp, seconds):
    return format_time(parse_time(stamp) + timedelta(seconds=seconds))


def post_id_of(value):
    if type(value) is int and not isinstance(value, bool) and value >= 0:
        return str(value)
    if type(value) is str and _POST_ID.fullmatch(value) is not None:
        return value
    raise ValueError("post_id")


def public_counts(source):
    if type(source) is not dict:
        return {}
    counts = {}
    for metric in METRICS:
        value = source.get(metric)
        if type(value) is int and not isinstance(value, bool):
            counts[metric] = value
    return counts


def canonical_id(rule_id, post_id, metric, op, threshold, check_time):
    if type(rule_id) is not str:
        raise ValueError("rule_id")
    if type(post_id) is not str:
        raise ValueError("post_id")
    post_id_of(post_id)
    if metric not in METRICS:
        raise ValueError("metric")
    if op not in OPS:
        raise ValueError("op")
    if type(threshold) is not int or isinstance(threshold, bool):
        raise ValueError("threshold")
    parse_time(check_time)
    return "|".join([rule_id, post_id, metric, op, str(threshold), check_time])
