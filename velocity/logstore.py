from velocity.lines import append_json, complete_rows
from velocity.rate import hit_rate


def effective_grades(text):
    found = {}
    for row in complete_rows(text):
        if "id" not in row or "grade" not in row:
            continue
        if row["id"] in found and found[row["id"]] != "waiting":
            continue
        found[row["id"]] = row["grade"]
    return found


def append_line(text, line):
    grades = effective_grades(text)
    current = grades.get(line["id"])
    if line["grade"] == "waiting" and current is not None:
        return text
    if current not in (None, "waiting"):
        return text
    return append_json(text, line)


def rule_counts(text):
    grades = effective_grades(text)
    rule_of = {}
    for row in complete_rows(text):
        label_id = row.get("id")
        if label_id not in grades or label_id in rule_of:
            continue
        rule_id = row.get("rule_id")
        if type(rule_id) is not str:
            continue
        rule_of[label_id] = rule_id
    buckets = {}
    for label_id, grade in grades.items():
        rule_id = rule_of.get(label_id)
        if rule_id is None or grade not in ("waiting", "matched", "missed", "unavailable"):
            continue
        bucket = buckets.setdefault(
            rule_id,
            {"waiting": 0, "matched": 0, "missed": 0, "unavailable": 0},
        )
        bucket[grade] += 1
    for bucket in buckets.values():
        rate = hit_rate(bucket["matched"], bucket["missed"])
        bucket["rate"] = rate if rate is not None else "no rate"
    return buckets
