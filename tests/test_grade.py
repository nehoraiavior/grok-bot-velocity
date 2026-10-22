import pytest

from velocity.grade import comparison_holds, decide, kind_from_lookup


def test_match_and_miss():
    assert decide("ok", True, True) == "matched"
    assert decide("ok", True, False) == "missed"


def test_missing_key_is_unavailable():
    assert decide("ok", False, False) == "unavailable"


def test_not_found_and_private_are_unavailable():
    assert decide("not_found", True, True) == "unavailable"
    assert decide("private", True, True) == "unavailable"


def test_retry_and_rate_limit_stay_waiting():
    assert decide("retry", True, True) == "waiting"
    assert decide("rate_limit", True, False) == "waiting"


def test_unknown_kind_raises():
    with pytest.raises(ValueError):
        decide("nope", True, True)


def test_comparison_operators():
    assert comparison_holds(">", 2, 1) is True
    assert comparison_holds(">=", 2, 2) is True
    assert comparison_holds("=", 2, 2) is True
    assert comparison_holds("<=", 2, 2) is True
    assert comparison_holds("<", 1, 2) is True
    assert comparison_holds(">", 1, 2) is False


def test_lookup_kinds():
    assert kind_from_lookup(200, {"public_metrics": {"like_count": 1}}) == "ok"
    assert kind_from_lookup(404, {"title": "Not Found Error"}) == "not_found"
    assert kind_from_lookup(403, {"detail": "protected"}) == "private"
    assert kind_from_lookup(403, None) == "retry"
    assert kind_from_lookup(401, {"title": "Unauthorized"}) == "retry"
    assert kind_from_lookup(500, {"title": "Error"}) == "retry"
    assert kind_from_lookup(429, {"title": "Too Many Requests"}) == "rate_limit"
    assert kind_from_lookup(200, "", timeout=True) == "retry"
    assert kind_from_lookup(200, "not-json") == "retry"
    assert kind_from_lookup(200, None) == "retry"
