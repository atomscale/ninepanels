import hashlib
import os

from . import exceptions

def instance_to_dict(instance):
    _dict = {}
    for key in instance.__mapper__.c.keys():
        _dict[key] = getattr(instance, key)
    return _dict


def generate_random_hash() -> str:
    """Generate a random hash

    Returns
        hash: 64 character hexademcial string

    """

    random_bytes = os.urandom(32)
    hash_bytes = hashlib.sha256(random_bytes)
    hash = hash_bytes.hexdigest()

    return hash

def parse_sort_by(model, sort_by: str):
    """ split validate that the sort key is present on the target model"""

    sort_key, sort_direction = sort_by.split('.')

    if hasattr(model, sort_key) and sort_direction in ['asc', 'desc']:
        return sort_key, sort_direction
    else:
        raise exceptions.ParseSortBy(detail="invalid sort_by value", context_data={"sort_by": {sort_by}})