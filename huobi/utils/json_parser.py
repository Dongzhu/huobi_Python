from huobi.utils.print_mix_object import *


def key_trans(key_origin):
    if key_origin and len(key_origin) > 1:
        return key_origin.replace("-", "_")
    else:
        return ""


def fill_obj(dict_data, class_name=object):
    if dict_data is None:
        return class_name()
    obj = class_name()
    for ks, vs in dict_data.items():
        obj_key = key_trans(ks)
        if hasattr(obj, obj_key):
            setattr(obj, obj_key, vs)
            continue
    return obj


def fill_obj_list(list_data, class_name):
    if list_data is None:
        return list()
    if (TypeCheck.is_list(list_data)):
        inner_obj_list = list()
        for idx, row in enumerate(list_data):
            if row is None:
                continue
            inner_obj = fill_obj(row, class_name)
            inner_obj_list.append(inner_obj)
        return inner_obj_list

    return list()


def default_parse(dict_data, outer_class_name=object, inner_class_name=object):
    if dict_data is None:
        return outer_class_name()
    from huobi.utils.print_mix_object import TypeCheck
    rsp_obj = outer_class_name()

    for outer_key, outer_value in dict_data.items():
        obj_key = key_trans(outer_key)
        if hasattr(rsp_obj, obj_key):
            new_value = outer_value
            if outer_value is None:
                continue
            if (TypeCheck.is_list(outer_value)):
                new_value = fill_obj_list(outer_value, inner_class_name)
            elif (TypeCheck.is_dict(outer_value)):
                new_value = fill_obj(outer_value, inner_class_name)

            setattr(rsp_obj, obj_key, new_value)
            continue

    return rsp_obj


def default_parse_data_as_long(ret_original_json, key_name=None, default_value=0):
    if ret_original_json:
        if key_name and len(key_name):
            data_json = ret_original_json.get("data", {})
            if data_json is None:
                return default_value
            ret_val = data_json.get(key_name, default_value)
        else:
            ret_val = ret_original_json.get("data", 0)
        if ret_val is None:
            return default_value
        try:
            return int(ret_val)
        except (ValueError, TypeError):
            return default_value
    else:
        return default_value


def default_parse_list_dict(inner_data, inner_class_name=object, default_value=None):
    from huobi.utils.print_mix_object import TypeCheck

    new_value = default_value
    if inner_data and len(inner_data):
        if (TypeCheck.is_list(inner_data)):
            new_value = fill_obj_list(inner_data, inner_class_name)
        elif (TypeCheck.is_dict(inner_data)):
            new_value = fill_obj(inner_data, inner_class_name)
        else:
            new_value = default_value

    return new_value


def default_parse_fill_directly(dict_data, outer_class_name=object):
    if dict_data is None:
        return outer_class_name()
    rsp_obj = outer_class_name()

    for outer_key, outer_value in dict_data.items():
        obj_key = key_trans(outer_key)
        if hasattr(rsp_obj, obj_key):
            new_value = outer_value
            setattr(rsp_obj, obj_key, new_value)
            continue

    return rsp_obj


def safe_get(dict_data, key, default_value=None):
    if dict_data is None:
        return default_value
    return dict_data.get(key, default_value)
