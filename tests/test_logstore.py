from velocity.logstore import append_line, effective_grades


def test_first_terminal_wins_over_later_waiting():
    text = ""
    text = append_line(text, {"id": "a", "grade": "waiting"})
    text = append_line(text, {"id": "a", "grade": "matched"})
    text = append_line(text, {"id": "a", "grade": "waiting"})
    assert effective_grades(text)["a"] == "matched"


def test_partial_trailing_line_is_ignored():
    text = '{"id":"a","grade":"matched"}\n{"id":"a","grade":"missed"}'
    assert effective_grades(text)["a"] == "matched"


def test_create_does_not_append_twice():
    text = append_line("", {"id": "a", "grade": "waiting"})
    again = append_line(text, {"id": "a", "grade": "waiting"})
    assert again == text
