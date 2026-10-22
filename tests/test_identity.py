import pytest

from velocity.identity import canonical_id


def test_canonical_id_is_stable():
    args = ("rule-a", "99", "like_count", ">=", 100, "2026-10-15T16:00:00Z")
    assert canonical_id(*args) == canonical_id(*args)


def test_refuses_non_integer_threshold():
    with pytest.raises(ValueError):
        canonical_id("rule-a", "99", "like_count", ">=", 10.5, "2026-10-15T16:00:00Z")


def test_refuses_unknown_metric():
    with pytest.raises(ValueError):
        canonical_id("rule-a", "99", "view_count", ">=", 1, "2026-10-15T16:00:00Z")


def test_refuses_unknown_comparison():
    with pytest.raises(ValueError):
        canonical_id("rule-a", "99", "like_count", "==", 1, "2026-10-15T16:00:00Z")


def test_refuses_bad_check_time():
    with pytest.raises(ValueError):
        canonical_id("rule-a", "99", "like_count", ">=", 1, "2026-10-15 16:00:00Z")


def test_refuses_non_decimal_post_id():
    with pytest.raises(ValueError):
        canonical_id("rule-a", "abc", "like_count", ">=", 1, "2026-10-15T16:00:00Z")
