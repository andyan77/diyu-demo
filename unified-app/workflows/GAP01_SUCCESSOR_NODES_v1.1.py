#!/usr/bin/env python3
"""Source fragment for the single bounded GAP-01 G2 successor."""

from __future__ import annotations

PROMISE_HELPER = r'''

def _user_expected_change_as_promise(value, user_query):
    """Return an exact user-supported promise equivalent, or fail closed.

    A stated outcome of watching/reading the content can satisfy both the
    audience-change and content-promise identities.  The value is never
    rewritten: it must be supported by the current utterance and contain an
    explicit consumption outcome.
    """
    val = _norm(value)
    if not val or not _supported(val, user_query):
        return ""
    if not re.search(r"(?:看完|读完|听完).{0,8}(?:知道|明白|理解|学会|拿到|获得)", val):
        return ""
    return val
'''


PROMISE_PROJECTION = r'''
    # GAP-01 successor: a current-turn, user-supported consumption outcome is
    # a valid equivalent content promise.  Preserve the exact value and keep
    # expression subject independent; do not make any professional wording.
    gap01_promise_projection_status = "NOT_APPLICABLE"
    if cap == "CONTENT_BRIEF" and "content.promise" in gaps:
        existing_promise = found.get(SPEC["content.promise"]["k"])
        expected = found.get(SPEC["audience.expected_change"]["k"])
        if existing_promise and not _missing(existing_promise.get("v")):
            gap01_promise_projection_status = "ALREADY_PRESENT"
        elif expected:
            equivalent = _user_expected_change_as_promise(expected.get("v"), uq)
            if equivalent:
                _set(lines, found, "content.promise", equivalent)
                gaps.remove("content.promise")
                gap01_promise_projection_status = "PROJECTED_EXACT_USER_EQUIVALENT"
            else:
                gap01_promise_projection_status = "REJECTED_NOT_USER_SUPPORTED_EQUIVALENT"
        else:
            gap01_promise_projection_status = "REJECTED_EXPECTED_CHANGE_ABSENT"
'''


OUTPUT_FIELD = r'''
        "gap01_promise_projection_status": gap01_promise_projection_status,
'''
