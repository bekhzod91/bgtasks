def merge(obj, field, merge_dicts: list, merge_field, raise_exception=False):
    for m in merge_dicts:
        if type(m) in [list, tuple]:
            merge_value = [i[merge_field] for i in m]
        else:
            merge_value = m.get(merge_field)

        if isinstance(obj, dict):
            value = obj.get(field)
            if value == merge_value:
                obj[field] = m
                return obj
        if isinstance(obj, object):
            value = getattr(obj, field, None)
            if value == merge_value:
                setattr(obj, field, m[merge_field])
                return obj
    if raise_exception:
        raise ValueError('Can not merge as data is not found')
    return


def merge_dict(obj: dict, field, merge_dicts: list,
               merge_field, raise_exception=False):
    value = obj.get(field, None)
    for m in merge_dicts:
        if value == m.get(merge_field):
            obj[field] = m
            return obj
    if raise_exception:
        raise ValueError('Can not merge as data is not found')
    return


def merge_obj(obj: object, field, merge_dicts: list,
              merge_field, raise_exception=False):
    value = getattr(obj, field, None)
    for m in merge_dicts:
        if value == m.get(merge_field):
            setattr(obj, field, m)
            return obj
    if raise_exception:
        raise ValueError('Can not merge as data is not found')
    return
