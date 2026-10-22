from velocity.grade import comparison_holds, decide
from velocity.lines import complete_rows
from velocity.logstore import append_line, effective_grades


def _comparison(row):
    if "op" in row:
        return row["op"]
    return row["comparison"]


def grade_due(text, now, lookup):
    grades = effective_grades(text)
    seen = set()
    for row in complete_rows(text):
        label_id = row.get("id")
        if label_id is None or label_id in seen:
            continue
        seen.add(label_id)
        if grades.get(label_id) != "waiting":
            continue
        check_time = row.get("check_time")
        if type(check_time) is not str or check_time > now:
            continue
        post_id = row.get("post_id")
        result = lookup(post_id)
        if result["kind"] == "rate_limit":
            return text
        counts = result.get("counts")
        metric = row.get("metric")
        if "metric_present" in result:
            present = result["metric_present"]
        elif result["kind"] == "ok" and type(counts) is dict and type(metric) is str:
            present = metric in counts
        else:
            present = False
        if "holds" in result:
            holds = result["holds"]
        elif present:
            holds = comparison_holds(_comparison(row), counts[metric], row["threshold"])
        else:
            holds = False
        grade = decide(result["kind"], present, holds)
        if grade == "waiting":
            continue
        line = {
            "id": label_id,
            "post_id": post_id,
            "check_time": check_time,
            "grade": grade,
        }
        if "rule_id" in row:
            line["rule_id"] = row["rule_id"]
        if "counts" in result and (grade in ("matched", "missed") or result["kind"] == "ok"):
            line["counts_at_fetch"] = result["counts"]
        if "fetched_at" in result and (grade in ("matched", "missed") or result["kind"] == "ok"):
            line["fetched_at"] = result["fetched_at"]
        text = append_line(text, line)
    return text
