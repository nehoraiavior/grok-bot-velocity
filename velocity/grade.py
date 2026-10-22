_PRIVATE_WORDS = ("private", "protected", "not authorized", "not visible", "forbidden")


def comparison_holds(op, value, threshold):
    if type(value) is not int or isinstance(value, bool):
        raise ValueError("value")
    if type(threshold) is not int or isinstance(threshold, bool):
        raise ValueError("threshold")
    if op == ">":
        return value > threshold
    if op == ">=":
        return value >= threshold
    if op == "=":
        return value == threshold
    if op == "<=":
        return value <= threshold
    if op == "<":
        return value < threshold
    raise ValueError("op")


def decide(kind, metric_present, holds):
    if kind in ("not_found", "private"):
        return "unavailable"
    if kind in ("retry", "rate_limit"):
        return "waiting"
    if kind != "ok":
        raise ValueError("kind")
    if not metric_present:
        return "unavailable"
    if holds:
        return "matched"
    return "missed"


def _error_text(body):
    if type(body) is not dict:
        return ""
    parts = []
    for key in ("title", "detail", "error", "reason", "message"):
        value = body.get(key)
        if type(value) is str:
            parts.append(value)
    errors = body.get("errors")
    if type(errors) is list:
        for item in errors:
            if type(item) is not dict:
                continue
            for key in ("title", "detail", "message"):
                value = item.get(key)
                if type(value) is str:
                    parts.append(value)
    return " ".join(parts).lower()


def kind_from_lookup(status, body, timeout=False):
    if timeout:
        return "retry"
    if status == 429:
        return "rate_limit"
    if status == 401:
        return "retry"
    if type(status) is int and 500 <= status <= 599:
        return "retry"
    text = _error_text(body)
    if status == 404 or "not found" in text:
        return "not_found"
    if status == 403:
        if type(body) is not dict:
            return "retry"
        if any(word in text for word in _PRIVATE_WORDS):
            return "private"
        return "retry"
    if body is None or body == "":
        return "retry"
    if type(body) is str:
        return "retry"
    if type(body) is not dict:
        return "retry"
    if "public_metrics" in body:
        return "ok"
    return "retry"
