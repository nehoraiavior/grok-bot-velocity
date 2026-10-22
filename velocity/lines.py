import json


def complete_rows(text):
    if not text or "\n" not in text:
        return []
    if not text.endswith("\n"):
        text = text[: text.rfind("\n") + 1]
    rows = []
    for line in text.split("\n"):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if type(row) is dict:
            rows.append(row)
    return rows


def append_json(text, row):
    return text + json.dumps(row, separators=(",", ":")) + "\n"
