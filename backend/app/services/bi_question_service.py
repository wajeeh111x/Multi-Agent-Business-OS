from typing import Any

from app.services.chart_query_service import (
    generate_chart_from_question,
)


# ============================================================
# HELPERS
# ============================================================

def _normalize(
    value: Any,
) -> str:
    if value is None:
        return ""

    return str(
        value
    ).strip().casefold()


def _contains(
    text: str,
    keywords: list[str],
) -> bool:
    normalized = _normalize(text)

    return any(
        _normalize(keyword) in normalized
        for keyword in keywords
    )


# ============================================================
# ANALYZE QUESTION
# ============================================================

def analyze_bi_question(
    question: str,
    analysis: dict,
    kpis: dict,
) -> dict:
    """
    Route a natural-language BI question to either:

    - business analysis
    - chart generation
    """

    if not isinstance(
        question,
        str,
    ) or not question.strip():

        return {
            "type": "validation",
            "answer": "Please provide a question.",
            "chart": None,
        }

    question = question.strip()

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    if not isinstance(
        kpis,
        dict,
    ):
        kpis = {}

    # ========================================================
    # CHART DETECTION
    # ========================================================

    chart_words = [
        "chart",
        "graph",
        "plot",
        "visualize",
        "visualise",
        "show",
        "display",
    ]

    chart_request = _contains(
        question,
        chart_words,
    )

    comparison_request = _contains(
        question,
        [
            "compare",
            "versus",
            "vs",
        ],
    )

    trend_request = _contains(
        question,
        [
            "trend",
            "over time",
            "timeline",
            "monthly",
            "period",
        ],
    )

    if (
        chart_request
        or comparison_request
        or trend_request
    ):

        chart_result = generate_chart_from_question(
            question=question,
            analysis=analysis,
        )

        if isinstance(
            chart_result,
            dict,
        ) and chart_result.get(
            "chart"
        ) is not None:

            return {
                "type": chart_result.get(
                    "type",
                    "chart",
                ),
                "answer": chart_result.get(
                    "answer",
                    "",
                ),
                "chart": chart_result.get(
                    "chart"
                ),
            }

    # ========================================================
    # BUSINESS ANALYSIS
    # ========================================================

    revenue = kpis.get(
        "revenue"
    )

    profit = kpis.get(
        "profit"
    )

    cost = kpis.get(
        "cost"
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "revenue",
            "sales",
        ],
    ):

        if isinstance(
            revenue,
            dict,
        ):

            total = revenue.get(
                "total"
            )

            average = revenue.get(
                "average"
            )

            return {
                "type": "revenue_analysis",
                "answer": (
                    f"Total revenue is "
                    f"{total:,.2f}, with an average "
                    f"of {average:,.2f} per record."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "profit",
            "earnings",
        ],
    ):

        if isinstance(
            profit,
            dict,
        ):

            total = profit.get(
                "total"
            )

            average = profit.get(
                "average"
            )

            return {
                "type": "profit_analysis",
                "answer": (
                    f"Total profit is "
                    f"{total:,.2f}, with an average "
                    f"of {average:,.2f} per record."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Cost
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "cost",
            "expense",
        ],
    ):

        if isinstance(
            cost,
            dict,
        ):

            total = cost.get(
                "total"
            )

            average = cost.get(
                "average"
            )

            return {
                "type": "cost_analysis",
                "answer": (
                    f"Total cost is "
                    f"{total:,.2f}, with an average "
                    f"of {average:,.2f} per record."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Profit margin
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "margin",
            "profit margin",
        ],
    ):

        margin = kpis.get(
            "profit_margin_percent"
        )

        if margin is not None:

            return {
                "type": "margin_analysis",
                "answer": (
                    f"The profit margin is "
                    f"{margin:.2f}%."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Top product
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "best product",
            "top product",
            "leading product",
        ],
    ):

        product = kpis.get(
            "top_product"
        )

        if isinstance(
            product,
            dict,
        ):

            return {
                "type": "top_product_analysis",
                "answer": (
                    f"{product.get('name')} is the "
                    f"top product with total value "
                    f"{product.get('total'):,.2f}."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Top region
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "best region",
            "top region",
            "leading region",
        ],
    ):

        region = kpis.get(
            "top_region"
        )

        if isinstance(
            region,
            dict,
        ):

            return {
                "type": "top_region_analysis",
                "answer": (
                    f"{region.get('name')} is the "
                    f"top region with total value "
                    f"{region.get('total'):,.2f}."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Best period
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "best period",
            "best month",
            "highest period",
            "highest month",
        ],
    ):

        period = kpis.get(
            "best_period"
        )

        if isinstance(
            period,
            dict,
        ):

            return {
                "type": "best_period_analysis",
                "answer": (
                    f"The best available period is "
                    f"{period.get('period')} with total "
                    f"value {period.get('total'):,.2f}."
                ),
                "chart": None,
            }

    # --------------------------------------------------------
    # Worst period
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "worst period",
            "worst month",
            "lowest period",
            "lowest month",
        ],
    ):

        period = kpis.get(
            "worst_period"
        )

        if isinstance(
            period,
            dict,
        ):

            return {
                "type": "worst_period_analysis",
                "answer": (
                    f"The worst available period is "
                    f"{period.get('period')} with total "
                    f"value {period.get('total'):,.2f}."
                ),
                "chart": None,
            }

    # ========================================================
    # FALLBACK
    # ========================================================

    return {
        "type": "general_analysis",
        "answer": (
            "I could not determine the requested "
            "business analysis from the available data."
        ),
        "chart": None,
    }