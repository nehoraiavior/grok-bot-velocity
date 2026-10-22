from velocity.rules import may_delete


def test_peer_with_better_rate_and_enough_grades_deletes():
    victim = {"metric": "like_count", "rate": (3, 10), "graded": 10}
    peer = {"metric": "like_count", "rate": (8, 10), "graded": 10}
    assert may_delete(victim, peer) is True


def test_no_rate_cannot_delete_or_be_deleted():
    victim = {"metric": "like_count", "rate": None, "graded": 0}
    peer = {"metric": "like_count", "rate": (1, 1), "graded": 1}
    assert may_delete(victim, peer) is False
    assert may_delete(peer, victim) is False


def test_smaller_peer_cannot_delete():
    victim = {"metric": "like_count", "rate": (3, 10), "graded": 10}
    peer = {"metric": "like_count", "rate": (1, 1), "graded": 1}
    assert may_delete(victim, peer) is False


def test_different_metric_cannot_delete():
    victim = {"metric": "like_count", "rate": (0, 4), "graded": 4}
    peer = {"metric": "reply_count", "rate": (4, 4), "graded": 4}
    assert may_delete(victim, peer) is False


def test_tie_keeps_both():
    victim = {"metric": "like_count", "rate": (2, 3), "graded": 3}
    peer = {"metric": "like_count", "rate": (4, 6), "graded": 6}
    assert may_delete(victim, peer) is False
