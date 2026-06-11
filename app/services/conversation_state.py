"""
Temporary conversation memory service.

Stores conversation state per:

    business_id + session_id

Example key:

    1:test-session

This is an in-memory implementation for Week 3.
It can later be replaced by LangGraph/Postgres persistence.
"""

_state_store: dict[str, dict] = {}


def build_state_key(
    business_id: int,
    session_id: str,
) -> str:
    """
    Build unique state key.
    """

    return f"{business_id}:{session_id}"


def load_state(
    business_id: int,
    session_id: str,
) -> dict:
    """
    Load conversation state.

    Returns empty dict if no state exists.
    """

    key = build_state_key(
        business_id,
        session_id,
    )

    return _state_store.get(key, {}).copy()


def save_state(
    business_id: int,
    session_id: str,
    state: dict,
) -> None:
    """
    Save conversation state.
    """

    key = build_state_key(
        business_id,
        session_id,
    )

    _state_store[key] = state