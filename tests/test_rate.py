from velocity.rate import higher, hit_rate


def test_no_graded_labels_has_no_rate():
    assert hit_rate(0, 0) is None


def test_rate_is_the_integer_pair():
    assert hit_rate(8, 2) == (8, 10)


def test_two_thirds_ties_four_sixths():
    assert higher((2, 3), (4, 6)) is False
    assert higher((4, 6), (2, 3)) is False


def test_eight_of_ten_beats_three_of_ten():
    assert higher((8, 10), (3, 10)) is True
