from typing import Any


# ============================================================
# IN-MEMORY CONVERSATION STORE
# ============================================================

_SESSIONS: dict[str, dict[str, Any]] = {}


# ============================================================
# GET SESSION
# ============================================================

def get_session(
    session_id: str,
) -> dict[str, Any]:
    """
    Return an existing BI session or create a new one.
    """

    if not session_id:
        raise ValueError(
            "Session ID is required."
        )

    session_id = str(
        session_id
    ).strip()

    if not session_id:
        raise ValueError(
            "Session ID is required."
        )

    if session_id not in _SESSIONS:

        _SESSIONS[session_id] = {
            "dataset_id": None,
            "filename": None,
            "last_question": None,
            "last_result": None,
            "history": [],
        }

    return _SESSIONS[session_id]


# ============================================================
# UPDATE SESSION
# ============================================================

def update_session(
    session_id: str,
    dataset_id: str | None = None,
    filename: str | None = None,
    question: str | None = None,
    result: dict | None = None,
):
    """
    Store the current BI conversation state.
    """

    session = get_session(
        session_id
    )

    if dataset_id is not None:
        session["dataset_id"] = dataset_id

    if filename is not None:
        session["filename"] = filename

    if question is not None:
        session["last_question"] = question

    if result is not None:
        session["last_result"] = result

    if question is not None:

        session["history"].append(
            {
                "question": question,
                "result": result,
            }
        )

        # Keep memory bounded.
        session["history"] = session[
            "history"
        ][-10:]

    return session


# ============================================================
# CLEAR SESSION
# ============================================================

def clear_session(
    session_id: str,
):
    """
    Delete a BI conversation session.
    """

    if session_id:

        _SESSIONS.pop(
            str(session_id).strip(),
            None,
        )


# ============================================================
# SESSION CONTEXT
# ============================================================

def get_session_context(
    session_id: str,
) -> dict:
    """
    Return compact context for the next BI question.
    """

    session = get_session(
        session_id
    )

    return {
        "dataset_id": session.get(
            "dataset_id"
        ),
        "filename": session.get(
            "filename"
        ),
        "last_question": session.get(
            "last_question"
        ),
        "last_result": session.get(
            "last_result"
        ),
        "history": session.get(
            "history",
            [],
        ),
    }