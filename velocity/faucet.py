from velocity.identity import METRICS, parse_time, post_id_of, public_counts
from velocity.lines import append_json, complete_rows

SOURCES = ("timeline", "search", "news")


def observation_from_post(post, source, fetched_at):
    if source not in SOURCES:
        raise ValueError("source")
    if type(post) is not dict:
        raise ValueError("post")
    raw_id = post["post_id"] if "post_id" in post else post.get("id")
    post_id = post_id_of(raw_id)
    fetched = post.get("fetched_at") or fetched_at
    try:
        parse_time(fetched)
    except ValueError:
        fetched = fetched_at
        parse_time(fetched)
    observation = {"post_id": post_id, "source": source, "fetched_at": fetched}
    author = post.get("author_id")
    if type(author) is str and author:
        observation["author_id"] = author
    elif type(author) is int and not isinstance(author, bool):
        observation["author_id"] = str(author)
    metrics = post["public_metrics"] if type(post.get("public_metrics")) is dict else post
    for metric, value in public_counts(metrics).items():
        observation[metric] = value
    return observation


def append_observation(text, observation):
    key = (observation["post_id"], observation["fetched_at"])
    for row in complete_rows(text):
        if (row.get("post_id"), row.get("fetched_at")) == key:
            return text
    return append_json(text, observation)


def grouped_snapshots(text):
    grouped = {}
    order = []
    for row in complete_rows(text):
        post_id = row.get("post_id")
        fetched = row.get("fetched_at")
        if type(post_id) is not str or type(fetched) is not str:
            continue
        try:
            parse_time(fetched)
        except ValueError:
            continue
        if post_id not in grouped:
            order.append(post_id)
            grouped[post_id] = []
        grouped[post_id].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: row["fetched_at"])
    return grouped, order


def pair(rows):
    if len(rows) < 2:
        return None
    return rows[0], rows[-1]


def elapsed_seconds(earlier, later):
    return int((parse_time(later) - parse_time(earlier)).total_seconds())


def rates(earlier, later):
    elapsed = elapsed_seconds(earlier["fetched_at"], later["fetched_at"])
    if elapsed <= 0:
        return {}
    found = {}
    for metric in METRICS:
        if metric not in earlier or metric not in later:
            continue
        if type(earlier[metric]) is not int or type(later[metric]) is not int:
            continue
        if isinstance(earlier[metric], bool) or isinstance(later[metric], bool):
            continue
        found[metric] = (later[metric] - earlier[metric]) / elapsed
    return found


def ordered_ids(text):
    grouped, order = grouped_snapshots(text)
    ranked = []
    for post_id in order:
        chosen = pair(grouped[post_id])
        if chosen is None:
            continue
        top = rates(chosen[0], chosen[1])
        if not top:
            continue
        ranked.append((max(top.values()), post_id))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [post_id for _, post_id in ranked]


def holding_ids(text):
    grouped, order = grouped_snapshots(text)
    return sorted(post_id for post_id in order if len(grouped[post_id]) == 1)


def gather(posts, fetched_at, query=None, topic=None, timeline=False):
    if query:
        source = "search"
    elif topic:
        source = "news"
    elif timeline:
        source = "timeline"
    else:
        return []
    observations = []
    for post in posts or []:
        try:
            observations.append(observation_from_post(post, source, fetched_at))
        except ValueError:
            continue
    return observations
