from velocity.run import grade_due


def lookup_ok(post_id):
    return {
        "kind": "ok",
        "metric_present": True,
        "holds": post_id == "1",
        "counts": {"like_count": 3},
        "fetched_at": "2026-10-15T17:05:00Z",
    }


def test_grades_only_due_waiting_labels():
    text = (
        '{"id":"a","post_id":"1","check_time":"2026-10-15T17:00:00Z","grade":"waiting"}\n'
        '{"id":"b","post_id":"2","check_time":"2026-10-15T18:00:00Z","grade":"waiting"}\n'
    )
    out = grade_due(text, "2026-10-15T17:30:00Z", lookup_ok)
    assert '"id":"a"' in out and '"grade":"matched"' in out
    assert out.count('"id":"b"') == 1


def test_rate_limit_stops_the_run():
    calls = {"n": 0}

    def lookup(post_id):
        calls["n"] += 1
        return {"kind": "rate_limit", "metric_present": True, "holds": False}

    text = (
        '{"id":"a","post_id":"1","check_time":"2026-10-15T17:00:00Z","grade":"waiting"}\n'
        '{"id":"c","post_id":"3","check_time":"2026-10-15T17:00:00Z","grade":"waiting"}\n'
    )
    out = grade_due(text, "2026-10-15T17:30:00Z", lookup)
    assert calls["n"] == 1
    assert out.count('"grade":"waiting"') == 2
