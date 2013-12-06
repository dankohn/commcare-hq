from couchdbkit import ResourceNotFound
from django.core.cache import cache
from casexml.apps.case.models import CommCareCase
from corehq.apps.users.cases import get_wrapped_owner
from corehq.apps.users.models import CouchUser
from corehq.apps.users.util import cached_user_id_to_username, raw_username

"""
Module for transforms used in exports.
"""


def user_id_to_username(user_id, doc):
    return cached_user_id_to_username(user_id)


def owner_id_to_display(owner_id, doc):
    return _cached_owner_id_to_display(owner_id)


def _cached_owner_id_to_display(owner_id):
    key = 'owner_id_to_display_cache_{id}'.format(id=owner_id)
    ret = cache.get(key)
    if ret:
        return ret
    owner = get_wrapped_owner(owner_id)
    if owner is None:
        return None
    else:
        ret = raw_username(owner.username) if isinstance(owner, CouchUser) else owner.name
        cache.set(key, ret)
        return ret

def case_id_to_case_name(case_id, doc):
    return _cached_case_id_to_case_name(case_id)

def _cached_case_id_to_case_name(case_id):
    key = 'case_id_to_case_name_cache_{id}'.format(id=case_id)
    ret = cache.get(key)
    if ret:
        return ret
    try:
        case = CommCareCase.get_lite(case_id)
    except ResourceNotFound:
        return None
    return case['name'] if "name" in case else None
