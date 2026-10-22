from velocity.rate import higher


def may_delete(victim, peer):
    if victim["metric"] != peer["metric"]:
        return False
    if victim["rate"] is None or peer["rate"] is None:
        return False
    if peer["graded"] < victim["graded"]:
        return False
    return higher(peer["rate"], victim["rate"])
