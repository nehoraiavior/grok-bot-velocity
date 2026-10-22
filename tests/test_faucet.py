from velocity.faucet import (
    append_observation,
    gather,
    holding_ids,
    observation_from_post,
    ordered_ids,
    rates,
)
from velocity.lines import complete_rows


def _obs(post_id, fetched_at, **counts):
    post = {"id": post_id, "public_metrics": counts, "author_id": "7"}
    return observation_from_post(post, "timeline", fetched_at)


def _text(*observations):
    text = ""
    for observation in observations:
        text = append_observation(text, observation)
    return text


def test_later_snapshot_does_not_replace_the_earlier():
    text = _text(
        _obs("1", "2026-10-15T16:00:00Z", like_count=1),
        _obs("1", "2026-10-15T17:00:00Z", like_count=4),
    )
    rows = complete_rows(text)
    assert len(rows) == 2
    assert rows[0]["like_count"] == 1
    assert rows[1]["like_count"] == 4


def test_one_snapshot_stays_in_holding():
    text = _text(_obs("1", "2026-10-15T16:00:00Z", like_count=1))
    assert ordered_ids(text) == []
    assert holding_ids(text) == ["1"]


def test_higher_largest_rate_is_ahead():
    text = _text(
        _obs("2", "2026-10-15T16:00:00Z", like_count=0),
        _obs("2", "2026-10-15T16:00:10Z", like_count=10),
        _obs("1", "2026-10-15T16:00:00Z", like_count=0),
        _obs("1", "2026-10-15T16:00:10Z", like_count=100),
    )
    assert ordered_ids(text) == ["1", "2"]
    assert holding_ids(text) == []


def test_missing_count_has_no_rate():
    earlier = _obs("1", "2026-10-15T16:00:00Z", like_count=1)
    later = {"post_id": "1", "source": "timeline", "fetched_at": "2026-10-15T16:00:10Z"}
    assert "like_count" not in rates(earlier, later)


def test_non_positive_elapsed_has_no_rate():
    earlier = _obs("1", "2026-10-15T16:00:00Z", like_count=1)
    later = _obs("1", "2026-10-15T16:00:00Z", like_count=5)
    assert rates(earlier, later) == {}


def test_automatic_gather_without_timeline_is_empty():
    posts = [{"id": "1", "public_metrics": {"like_count": 1}}]
    assert gather(posts, "2026-10-15T16:00:00Z") == []


def test_query_and_topic_set_source():
    posts = [{"id": "1", "public_metrics": {"like_count": 1}}]
    stamp = "2026-10-15T16:00:00Z"
    assert gather(posts, stamp, query="cats")[0]["source"] == "search"
    assert gather(posts, stamp, topic="space")[0]["source"] == "news"
    assert gather(posts, stamp, timeline=True)[0]["source"] == "timeline"


def test_observation_keeps_only_present_counts_and_author():
    observation = observation_from_post(
        {"id": "15", "author_id": "9", "public_metrics": {"like_count": 2, "view_count": 8}},
        "timeline",
        "2026-10-15T16:00:00Z",
    )
    assert observation["post_id"] == "15"
    assert observation["author_id"] == "9"
    assert observation["like_count"] == 2
    assert "view_count" not in observation
    assert "reply_count" not in observation
