from typing import Any

from app.services.bi_question_service import (
    analyze_bi_question,
)

from app.services.chart_query_service import (
    generate_chart_from_question,
)

from app.services.bi_memory import (
    get_session,
    update_session,
)


# ============================================================
# FOLLOW-UP DETECTION
# ============================================================

def _is_follow_up(
    question: str,
) -> bool:
    """
    Detect simple conversational follow-up language.
    """

    text = str(
        question
    ).strip().casefold()

    follow_up_phrases = [
        "what about",
        "how about",
        "show that",
        "show it",
        "compare that",
        "compare it",
        "what about that",
        "and profit",
        "and revenue",
        "and cost",
        "now show",
        "now compare",
        "same for",
    ]

    return any(
        phrase in text
        for phrase in follow_up_phrases
    )


# ============================================================
# RESOLVE QUESTION
# ============================================================

def resolve_question(
    question: str,
    session: dict[str, Any],
) -> str:
    """
    Resolve a simple follow-up question using
    previous conversational context.
    """

    if not _is_follow_up(
        question
    ):
        return question

    previous_question = session.get(
        "last_question"
    )

    if not previous_question:
        return question

    # --------------------------------------------------------
    # Chart follow-ups
    # --------------------------------------------------------

    text = question.strip().casefold()

    if (
        "show that" in text
        or "show it" in text
        or "as a chart" in text
        or "as chart" in text
    ):

        return (
            f"Create a chart for: "
            f"{previous_question}"
        )

    # --------------------------------------------------------
    # Generic contextual follow-up
    # --------------------------------------------------------

    return (
        f"Previous question: {previous_question}\n"
        f"Follow-up question: {question}"
    )


# ============================================================
# CONVERSATIONAL BI
# ============================================================

def process_bi_conversation(
    session_id: str,
    dataset_id: str,
    filename: str,
    question: str,
    analysis: dict,
    kpis: dict,
) -> dict:
    """
    Process a BI question while keeping short-term
    conversational memory.
    """

    session = get_session(
        session_id
    )

    resolved_question = resolve_question(
        question,
        session,
    )

    # --------------------------------------------------------
    # Direct chart request
    # --------------------------------------------------------

    chart_result = generate_chart_from_question(
        question=resolved_question,
        analysis=analysis,
    )

    chart = None

    if isinstance(
        chart_result,
        dict,
    ):

        chart = chart_result.get(
            "chart"
        )

    if chart is not None:

        result = {
            "type": chart_result.get(
                "type",
                "chart",
            ),
            "answer": chart_result.get(
                "answer",
                "",
            ),
            "chart": chart,
            "resolved_question": resolved_question,
        }

    else:

        # ----------------------------------------------------
        # Business analysis
        # ----------------------------------------------------

        result = analyze_bi_question(
            question=resolved_question,
            analysis=analysis,
            kpis=kpis,
        )

        if not isinstance(
            result,
            dict,
        ):

            result = {
                "type": "general_analysis",
                "answer": (
                    "Unable to analyze the question."
                ),
                "chart": None,
            }

        result["resolved_question"] = (
            resolved_question
        )

    # --------------------------------------------------------
    # Store conversation
    # --------------------------------------------------------

    update_session(
        session_id=session_id,
        dataset_id=dataset_id,
        filename=filename,
        question=question,
        result=result,
    )

    return result