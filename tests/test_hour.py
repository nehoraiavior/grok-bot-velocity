import json

from velocity.hour import run_hour
from velocity.lines import complete_rows


def _line(row):
    return json.dumps(row, separators=(",", ":")) + "\n"


def _waiting(label_id, post_id, check_time, threshold):
    return {
        "id": label_id,
        "rule_id": "velocity-like_count",
        "post_id": post_id,
        "metric": "like_count",
        "op": ">=",
        "comparison": ">=",
        "threshold": threshold,
        "check_time": check_time,
        "grade": "waiting",
    }


def test_hour_stores_a_second_snapshot_and_one_waiting_claim():
    observations = _line(
        {
            "post_id": "1",
            "source": "timeline",
            "fetched_at": "2026-10-15T16:00:00Z",
            "like_count": 10,
        }
    )
    by_id = {
        "1": {
            "id": "1",
            "public_metrics": {"like_count": 20, "reply_count": 1},
            "fetched_at": "2026-10-15T16:01:40Z",
        }
    }
    result = run_hour(observations, "", None, by_id, "2026-10-15T16:01:40Z")
    rows = complete_rows(result["observations"])
    assert [row["fetched_at"] for row in rows] == [
        "2026-10-15T16:00:00Z",
        "2026-10-15T16:01:40Z",
    ]
    claims = [row for row in complete_rows(result["labels"]) if row["grade"] == "waiting"]
    assert len(claims) == 1
    assert claims[0]["rule_id"] == "velocity-like_count"
    assert claims[0]["threshold"] == 380
    assert claims[0]["check_time"] == "2026-10-15T17:01:40Z"
    assert result["rules"]["velocity-like_count"]["waiting"] == 1
    assert result["rules"]["velocity-like_count"]["rate"] == "no rate"


def test_same_claim_is_not_appended_twice():
    observations = _line(
        {
            "post_id": "1",
            "source": "timeline",
            "fetched_at": "2026-10-15T16:00:00Z",
            "like_count": 10,
        }
    )
    by_id = {
        "1": {
            "id": "1",
            "public_metrics": {"like_count": 20},
            "fetched_at": "2026-10-15T16:01:40Z",
        }
    }
    now = "2026-10-15T16:01:40Z"
    first = run_hour(observations, "", None, by_id, now)
    second = run_hour(first["observations"], first["labels"], None, by_id, now)
    assert second["labels"] == first["labels"]
    assert second["observations"] == first["observations"]


def test_timeline_snapshot_has_no_keyword_and_one_snapshot_writes_no_claim():
    timeline = {"data": [{"id": "4", "author_id": "8", "public_metrics": {"like_count": 1}}]}
    result = run_hour("", "", timeline, {}, "2026-10-15T16:00:00Z")
    rows = complete_rows(result["observations"])
    assert len(rows) == 1
    assert rows[0]["source"] == "timeline"
    assert rows[0]["post_id"] == "4"
    assert result["labels"] == ""
    assert result["rules"] == {}


def test_grades_a_due_claim_and_stops_on_rate_limit():
    observations = ""
    labels = _line(_waiting("a", "1", "2026-10-15T17:00:00Z", 5))
    labels += _line(_waiting("b", "2", "2026-10-15T17:00:00Z", 5))
    by_id = {
        "1": {"status": 429},
        "2": {
            "id": "2",
            "public_metrics": {"like_count": 9},
            "fetched_at": "2026-10-15T17:30:00Z",
        },
    }
    result = run_hour(observations, labels, None, by_id, "2026-10-15T17:30:00Z")
    grades = [row["grade"] for row in complete_rows(result["labels"])]
    assert grades == ["waiting", "waiting"]
    assert "matched" not in result["labels"]


def test_not_found_is_terminal_and_a_miss_counts_in_the_rate():
    labels = _line(_waiting("keep", "1", "2026-10-15T17:00:00Z", 100))
    by_id = {
        "1": {
            "id": "1",
            "public_metrics": {"like_count": 3},
            "fetched_at": "2026-10-15T17:10:00Z",
        }
    }
    missed = run_hour("", labels, None, by_id, "2026-10-15T17:10:00Z")
    assert missed["rules"]["velocity-like_count"]["missed"] == 1
    assert missed["rules"]["velocity-like_count"]["rate"] == (0, 1)

    unavailable = run_hour(
        "",
        _line(_waiting("gone", "9", "2026-10-15T17:00:00Z", 1)),
        None,
        {"errors": [{"value": "9", "status": 404, "title": "Not Found Error"}]},
        "2026-10-15T17:10:00Z",
    )
    assert unavailable["rules"]["velocity-like_count"]["unavailable"] == 1
    assert unavailable["rules"]["velocity-like_count"]["rate"] == "no rate"
    again = run_hour("", unavailable["labels"], None, {"9": {"status": 200, "public_metrics": {"like_count": 50}}}, "2026-10-15T18:00:00Z")
    assert again["labels"] == unavailable["labels"]


def test_missing_metric_key_is_unavailable():
    labels = _line(_waiting("gap", "3", "2026-10-15T17:00:00Z", 1))
    by_id = {"3": {"id": "3", "public_metrics": {"reply_count": 4}, "fetched_at": "2026-10-15T17:05:00Z"}}
    result = run_hour("", labels, None, by_id, "2026-10-15T17:05:00Z")
    grades = [row["grade"] for row in complete_rows(result["labels"])]
    assert grades == ["waiting", "unavailable"]
    assert result["rules"]["velocity-like_count"]["unavailable"] == 1
    assert result["rules"]["velocity-like_count"]["rate"] == "no rate"


def test_hour_does_not_delete_a_rule():
    labels = _line(_waiting("a", "1", "2026-10-15T17:00:00Z", 1))
    labels += _line(
        {
            "id": "other",
            "rule_id": "velocity-reply_count",
            "post_id": "1",
            "metric": "reply_count",
            "op": ">=",
            "comparison": ">=",
            "threshold": 1,
            "check_time": "2026-10-15T17:00:00Z",
            "grade": "waiting",
        }
    )
    result = run_hour("", labels, None, {"status": 401}, "2026-10-15T17:30:00Z")
    assert set(result["rules"]) == {"velocity-like_count", "velocity-reply_count"}
    assert result["labels"] == labels
