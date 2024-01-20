import hashlib
import json
import datetime


def get_score(
    store,
    phone=None,
    email=None,
    birthday=None,
    gender=None,
    first_name=None,
    last_name=None,
):
    key_parts = [
        first_name or "",
        last_name or "",
        str(phone) or "",
        datetime.datetime.strptime(birthday, "%d.%m.%Y").strftime("%Y%m%d")
        if birthday is not None
        else "",
    ]
    # print("HERE: ", key_parts)
    key = "uid:" + hashlib.md5(bytes("".join(key_parts), "utf-8")).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        # print("REDIS!!!! ", score)
        return float(score.decode("utf-8"))
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    if r and isinstance(r, bytes):
        r = eval(r.decode("utf-8"))
    return r
