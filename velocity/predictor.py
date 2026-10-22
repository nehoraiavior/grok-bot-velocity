from velocity.faucet import rates
from velocity.identity import METRICS, add_seconds, canonical_id, parse_time


def _nearest(value):
    if value >= 0:
        return int(value + 0.5)
    return int(value - 0.5)


def _score_counts(snapshot):
    counts = {}
    for metric in METRICS:
        value = snapshot.get(metric)
        if type(value) is int and not isinstance(value, bool):
            counts[metric] = value
    return counts


def claims_for_pair(earlier, later, scored_at):
    parse_time(scored_at)
    if earlier.get("post_id") != later.get("post_id"):
        return []
    rate_map = rates(earlier, later)
    written = []
    for metric in METRICS:
        rate = rate_map.get(metric)
        if rate is None or rate <= 0:
            continue
        later_count = later[metric]
        threshold = _nearest(later_count + rate * 3600)
        if threshold < later_count:
            threshold = later_count
        check_time = add_seconds(later["fetched_at"], 3600)
        rule_id = "velocity-" + metric
        comparison = ">="
        post_id = later["post_id"]
        claim = {
            "rule_id": rule_id,
            "post_id": post_id,
            "metric": metric,
            "comparison": comparison,
            "threshold": threshold,
            "check_time": check_time,
        }
        written.append(
            {
                "id": canonical_id(rule_id, post_id, metric, comparison, threshold, check_time),
                "rule_id": rule_id,
                "post_id": post_id,
                "metric": metric,
                "op": comparison,
                "comparison": comparison,
                "threshold": threshold,
                "check_time": check_time,
                "scored_at": scored_at,
                "counts_at_score": _score_counts(later),
                "grade": "waiting",
                "claim": claim,
            }
        )
    return written
