from velocity.predictor import claims_for_pair


def test_one_claim_per_rising_count():
    earlier = {
        "post_id": "1",
        "fetched_at": "2026-10-15T16:00:00Z",
        "like_count": 10,
        "reply_count": 5,
    }
    later = {
        "post_id": "1",
        "fetched_at": "2026-10-15T16:10:00Z",
        "like_count": 20,
        "reply_count": 5,
    }
    written = claims_for_pair(earlier, later, "2026-10-15T16:10:00Z")
    assert len(written) == 1
    claim = written[0]
    assert claim["rule_id"] == "velocity-like_count"
    assert claim["comparison"] == ">="
    assert claim["threshold"] == 80
    assert claim["check_time"] == "2026-10-15T17:10:00Z"
    assert claim["grade"] == "waiting"
    assert claim["counts_at_score"]["like_count"] == 20


def test_half_second_rate_rounds_to_nearest_and_stays_at_least_the_later_count():
    earlier = {"post_id": "1", "fetched_at": "2026-10-15T16:00:00Z", "like_count": 10}
    later = {"post_id": "1", "fetched_at": "2026-10-15T18:00:00Z", "like_count": 11}
    written = claims_for_pair(earlier, later, "2026-10-15T18:00:00Z")
    assert written[0]["threshold"] == 12

    earlier_tiny = {"post_id": "1", "fetched_at": "2026-10-15T16:00:00Z", "like_count": 9}
    tiny_later = {"post_id": "1", "fetched_at": "2026-10-16T19:46:40Z", "like_count": 10}
    tiny = claims_for_pair(earlier_tiny, tiny_later, "2026-10-16T19:46:40Z")
    assert tiny[0]["threshold"] == 10


def test_check_time_crosses_midnight():
    earlier = {"post_id": "1", "fetched_at": "2026-10-15T22:00:00Z", "like_count": 1}
    later = {"post_id": "1", "fetched_at": "2026-10-15T23:30:00Z", "like_count": 2}
    written = claims_for_pair(earlier, later, "2026-10-15T23:30:00Z")
    assert written[0]["check_time"] == "2026-10-16T00:30:00Z"


def test_flat_or_falling_count_writes_no_claim():
    earlier = {"post_id": "1", "fetched_at": "2026-10-15T16:00:00Z", "like_count": 5}
    later = {"post_id": "1", "fetched_at": "2026-10-15T17:00:00Z", "like_count": 4}
    assert claims_for_pair(earlier, later, "2026-10-15T17:00:00Z") == []
