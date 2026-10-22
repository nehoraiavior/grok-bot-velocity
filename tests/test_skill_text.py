from pathlib import Path


def test_skill_names_the_clock_and_the_log():
    text = Path("/agent/grok/SKILL.md").read_text()
    assert "once an hour" in text
    assert "/workspace/labeler/labels.jsonl" in text
    assert "rule_id" in text
    assert "does not post" in text
    assert "run_hour" in text


def test_routine_is_not_a_script_clock():
    text = Path("/agent/grok/routine.md").read_text()
    assert "once an hour" in text
    assert "Grade due labels" in text
