def hit_rate(matched, missed):
    graded = matched + missed
    if graded < 1:
        return None
    return matched, graded


def higher(left, right):
    return left[0] * right[1] > right[0] * left[1]
