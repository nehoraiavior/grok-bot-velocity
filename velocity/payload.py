from velocity.grade import kind_from_lookup
from velocity.identity import post_id_of, public_counts


def _post_id(value):
    try:
        return post_id_of(value)
    except ValueError:
        return None


def _status_of(entry):
    if type(entry) is not dict:
        return None
    for key in ("http_status", "status"):
        value = entry.get(key)
        if type(value) is int and not isinstance(value, bool):
            return value
    return None


def _timeout(entry):
    if type(entry) is not dict:
        return False
    if entry.get("timeout") is True:
        return True
    return entry.get("error") == "timeout"


def _fetched(entry):
    if type(entry) is not dict:
        return None
    fetched = entry.get("fetched_at")
    if type(fetched) is str:
        return fetched
    return None


def _author(entry):
    if type(entry) is not dict:
        return None
    author = entry.get("author_id")
    if type(author) is str and author:
        return author
    if type(author) is int and not isinstance(author, bool):
        return str(author)
    return None


def _metrics(entry):
    if type(entry) is not dict:
        return {}
    if type(entry.get("public_metrics")) is dict:
        return public_counts(entry["public_metrics"])
    return public_counts(entry)


def timeline_posts(payload):
    if type(payload) is list:
        return [item for item in payload if type(item) is dict]
    if type(payload) is not dict:
        return []
    data = payload.get("data")
    if type(data) is list:
        return [item for item in data if type(item) is dict]
    if type(data) is dict:
        return [data]
    if _post_id(payload.get("id") if "id" in payload else payload.get("post_id")):
        return [payload]
    return []


def _error_id(error):
    if type(error) is not dict:
        return None
    for key in ("value", "resource_id", "post_id", "id"):
        if key not in error:
            continue
        found = _post_id(error.get(key))
        if found is not None:
            return found
    return None


def classify_entry(entry):
    empty = {"snapshot": False, "kind": "retry", "counts": {}, "author_id": None, "fetched_at": None}
    if type(entry) is not dict:
        return empty
    timeout = _timeout(entry)
    status = _status_of(entry)
    body = entry["body"] if "body" in entry else entry
    kind = kind_from_lookup(status, body, timeout)
    fetched = _fetched(entry) or (_fetched(body) if type(body) is dict else None)
    author = _author(body if type(body) is dict else None)
    counts = _metrics(body if type(body) is dict else {})
    snapshot = False
    if kind == "ok":
        snapshot = True
    elif kind == "retry" and not timeout and status in (None, 200) and type(body) is dict:
        raw_id = body.get("id") if "id" in body else body.get("post_id")
        if _post_id(raw_id) is not None:
            snapshot = True
    if kind != "ok":
        counts = {}
    return {
        "snapshot": snapshot,
        "kind": kind,
        "counts": counts,
        "author_id": author,
        "fetched_at": fetched,
    }


def _is_id_map(payload):
    if type(payload) is not dict or not payload:
        return False
    return all(_post_id(key) is not None for key in payload)


def by_id_index(payload):
    if payload is None or type(payload) is str:
        return {}, False
    if type(payload) is dict and _status_of(payload) == 429 and not _is_id_map(payload):
        return {}, True
    if type(payload) is dict and payload.get("error") == "rate_limit":
        return {}, True
    errors = payload.get("errors") if type(payload) is dict else None
    if (
        type(errors) is list
        and "data" not in payload
        and not _is_id_map(payload)
        and any(type(item) is dict and _status_of(item) == 429 for item in errors)
    ):
        return {}, True
    if _is_id_map(payload):
        index = {}
        for key, value in payload.items():
            index[_post_id(key)] = classify_entry(value if type(value) is dict else {"body": value})
        return index, False

    index = {}
    posts = timeline_posts(payload)
    error_items = errors if type(errors) is list else []
    for post in posts:
        raw_id = post.get("id") if "id" in post else post.get("post_id")
        post_id = _post_id(raw_id)
        if post_id is None:
            continue
        index[post_id] = classify_entry(post)
    global_rate_limit = False
    for error in error_items:
        if type(error) is not dict:
            continue
        post_id = _error_id(error)
        if post_id is None and _status_of(error) == 429:
            global_rate_limit = True
            continue
        if post_id is None:
            continue
        index[post_id] = classify_entry(error)
    return index, global_rate_limit
