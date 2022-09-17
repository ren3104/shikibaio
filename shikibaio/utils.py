from typing import Any, Dict


def dict_diff(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for k, v in a.items():
        if k in b:
            if isinstance(v, dict):
                recursion_result = dict_diff(v, b[k])
                if recursion_result:
                    result[k] = recursion_result
            elif v != b[k]:
                result[k] = v
    return result
