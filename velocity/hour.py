from velocity.faucet import append_observation, grouped_snapshots, observation_from_post, pair
from velocity.identity import parse_time
from velocity.logstore import append_line, rule_counts
from velocity.payload import by_id_index, timeline_posts
from velocity.predictor import claims_for_pair
from velocity.run import grade_due


def _lookup_result(entry, now):
    result = {"kind": entry["kind"]}
    if entry["kind"] == "ok":
        result["counts"] = entry["counts"]
        result["fetched_at"] = entry["fetched_at"] or now
    return result


def run_hour(observations, labels, timeline, by_id, now):
    parse_time(now)
    for post in timeline_posts(timeline):
        try:
            observation = observation_from_post(post, "timeline", now)
        except ValueError:
            continue
        observations = append_observation(observations, observation)

    index, global_rate_limit = by_id_index(by_id)
    if not global_rate_limit:
        grouped, _order = grouped_snapshots(observations)
        for post_id, rows in grouped.items():
            if len(rows) != 1:
                continue
            entry = index.get(post_id)
            if entry is None or not entry["snapshot"]:
                continue
            fetched = entry["fetched_at"] or now
            try:
                parse_time(fetched)
            except ValueError:
                fetched = now
            post = {"id": post_id, "fetched_at": fetched, "public_metrics": entry["counts"]}
            if entry["author_id"]:
                post["author_id"] = entry["author_id"]
            try:
                observation = observation_from_post(post, "timeline", fetched)
            except ValueError:
                continue
            observations = append_observation(observations, observation)

    grouped, order = grouped_snapshots(observations)
    for post_id in order:
        chosen = pair(grouped[post_id])
        if chosen is None:
            continue
        for claim in claims_for_pair(chosen[0], chosen[1], now):
            labels = append_line(labels, claim)

    def lookup(post_id):
        if global_rate_limit:
            return {"kind": "rate_limit", "metric_present": False, "holds": False}
        entry = index.get(post_id)
        if entry is None:
            return {"kind": "retry", "metric_present": False, "holds": False}
        if entry["kind"] == "rate_limit":
            return {"kind": "rate_limit", "metric_present": False, "holds": False}
        return _lookup_result(entry, now)

    labels = grade_due(labels, now, lookup)
    return {"observations": observations, "labels": labels, "rules": rule_counts(labels)}
