from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _normalize(value: Any) -> str:
    """
    Normalize text for matching.
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .casefold()
    )


def _contains(
    question: str,
    keywords: list[str],
) -> bool:
    """
    Check whether a question contains any keyword.
    """

    text = _normalize(
        question
    )

    return any(
        _normalize(keyword) in text
        for keyword in keywords
    )


def _number(value: Any):
    """
    Convert a value to a number.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (int, float),
    ):

        return value

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# PRODUCT CHART
# ============================================================

def _product_chart(
    products: list,
    question: str,
):
    """
    Build a product chart.
    """

    if not isinstance(
        products,
        list,
    ):
        return None

    data = []

    for item in products:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        total = _number(
            item.get(
                "total"
            )
        )

        if (
            name is None
            or total is None
        ):
            continue

        data.append(
            {
                "label": str(name),
                "value": total,
            }
        )

    if not data:
        return None

    # --------------------------------------------------------
    # Top N
    # --------------------------------------------------------

    if _contains(
        question,
        [
            "top 5",
            "top five",
        ],
    ):

        data = data[:5]

    elif _contains(
        question,
        [
            "top 3",
            "top three",
        ],
    ):

        data = data[:3]

    return {
        "type": "bar",
        "title": "Revenue by Product",
        "x_axis": "Product",
        "y_axis": "Revenue",
        "data": data,
    }


# ============================================================
# REGION CHART
# ============================================================

def _region_chart(
    regions: list,
):
    """
    Build a region revenue chart.
    """

    if not isinstance(
        regions,
        list,
    ):
        return None

    data = []

    for item in regions:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        total = _number(
            item.get(
                "total"
            )
        )

        if (
            name is None
            or total is None
        ):
            continue

        data.append(
            {
                "label": str(name),
                "value": total,
            }
        )

    if not data:
        return None

    return {
        "type": "bar",
        "title": "Revenue by Region",
        "x_axis": "Region",
        "y_axis": "Revenue",
        "data": data,
    }


# ============================================================
# TREND CHART
# ============================================================

def _trend_chart(
    trends: list,
):
    """
    Build a revenue trend chart.
    """

    if not isinstance(
        trends,
        list,
    ):
        return None

    data = []

    for item in trends:

        if not isinstance(
            item,
            dict,
        ):
            continue

        period = item.get(
            "period"
        )

        total = _number(
            item.get(
                "total"
            )
        )

        if (
            period is None
            or total is None
        ):
            continue

        data.append(
            {
                "label": str(period),
                "value": total,
            }
        )

    if len(data) < 2:
        return None

    return {
        "type": "line",
        "title": "Revenue Trend",
        "x_axis": "Period",
        "y_axis": "Revenue",
        "data": data,
    }


# ============================================================
# REVENUE VS PROFIT
# ============================================================

def _revenue_profit_chart(
    business_metrics: dict,
):
    """
    Build a revenue vs profit chart.
    """

    if not isinstance(
        business_metrics,
        dict,
    ):
        return None

    revenue = business_metrics.get(
        "revenue"
    )

    profit = business_metrics.get(
        "profit"
    )

    if not isinstance(
        revenue,
        dict,
    ):
        return None

    if not isinstance(
        profit,
        dict,
    ):
        return None

    revenue_total = _number(
        revenue.get("total")
    )

    profit_total = _number(
        profit.get("total")
    )

    if (
        revenue_total is None
        or profit_total is None
    ):
        return None

    return {
        "type": "comparison",
        "title": "Revenue vs Profit",
        "x_axis": "Metric",
        "y_axis": "Value",
        "data": [
            {
                "label": "Revenue",
                "value": revenue_total,
            },
            {
                "label": "Profit",
                "value": profit_total,
            },
        ],
    }


# ============================================================
# REVENUE VS COST
# ============================================================

def _revenue_cost_chart(
    business_metrics: dict,
):
    """
    Build a revenue vs cost chart.
    """

    if not isinstance(
        business_metrics,
        dict,
    ):
        return None

    revenue = business_metrics.get(
        "revenue"
    )

    cost = business_metrics.get(
        "cost"
    )

    if not isinstance(
        revenue,
        dict,
    ):
        return None

    if not isinstance(
        cost,
        dict,
    ):
        return None

    revenue_total = _number(
        revenue.get("total")
    )

    cost_total = _number(
        cost.get("total")
    )

    if (
        revenue_total is None
        or cost_total is None
    ):
        return None

    return {
        "type": "comparison",
        "title": "Revenue vs Cost",
        "x_axis": "Metric",
        "y_axis": "Value",
        "data": [
            {
                "label": "Revenue",
                "value": revenue_total,
            },
            {
                "label": "Cost",
                "value": cost_total,
            },
        ],
    }


# ============================================================
# MAIN CHART QUERY
# ============================================================

def generate_chart_from_question(
    question: str,
    analysis: dict,
) -> dict:
    """
    Convert a natural-language chart request into
    a deterministic chart.
    """

    if not isinstance(
        question,
        str,
    ) or not question.strip():

        return {
            "answer": "Please provide a chart question.",
            "chart": None,
            "type": "validation",
        }

    if not isinstance(
        analysis,
        dict,
    ):
        return {
            "answer": "Dataset analysis is unavailable.",
            "chart": None,
            "type": "validation",
        }

    question = question.strip()

    products = analysis.get(
        "products",
        [],
    )

    regions = analysis.get(
        "regions",
        [],
    )

    trends = analysis.get(
        "trends",
        [],
    )

    business_metrics = analysis.get(
        "business_metrics",
        {},
    )

    # ========================================================
    # PRODUCT
    # ========================================================

    if _contains(
        question,
        [
            "product",
            "products",
            "item",
            "items",
        ],
    ) and _contains(
        question,
        [
            "chart",
            "graph",
            "show",
            "display",
            "revenue",
            "sales",
            "performance",
            "top",
        ],
    ):

        chart = _product_chart(
            products,
            question,
        )

        if chart:

            return {
                "answer": (
                    "Generated a revenue-by-product chart."
                ),
                "chart": chart,
                "type": "product_chart",
            }

    # ========================================================
    # REGION
    # ========================================================

    if _contains(
        question,
        [
            "region",
            "regions",
            "regional",
            "area",
        ],
    ) and _contains(
        question,
        [
            "chart",
            "graph",
            "show",
            "display",
            "revenue",
            "sales",
            "performance",
        ],
    ):

        chart = _region_chart(
            regions
        )

        if chart:

            return {
                "answer": (
                    "Generated a revenue-by-region chart."
                ),
                "chart": chart,
                "type": "region_chart",
            }

    # ========================================================
    # TREND
    # ========================================================

    if _contains(
        question,
        [
            "trend",
            "trends",
            "over time",
            "timeline",
            "monthly",
            "monthly trend",
        ],
    ):

        chart = _trend_chart(
            trends
        )

        if chart:

            return {
                "answer": (
                    "Generated a revenue trend chart."
                ),
                "chart": chart,
                "type": "trend_chart",
            }

    # ========================================================
    # REVENUE VS PROFIT
    # ========================================================

    if (
        _contains(
            question,
            [
                "revenue vs profit",
                "revenue versus profit",
                "revenue and profit",
                "profit vs revenue",
            ],
        )
        or (
            _contains(
                question,
                [
                    "compare",
                ],
            )
            and _contains(
                question,
                [
                    "revenue",
                    "profit",
                ],
            )
        )
    ):

        chart = _revenue_profit_chart(
            business_metrics
        )

        if chart:

            return {
                "answer": (
                    "Generated a revenue-versus-profit comparison."
                ),
                "chart": chart,
                "type": "revenue_profit_chart",
            }

    # ========================================================
    # REVENUE VS COST
    # ========================================================

    if (
        _contains(
            question,
            [
                "revenue vs cost",
                "revenue versus cost",
                "revenue and cost",
                "cost vs revenue",
            ],
        )
        or (
            _contains(
                question,
                [
                    "compare",
                ],
            )
            and _contains(
                question,
                [
                    "revenue",
                    "cost",
                ],
            )
        )
    ):

        chart = _revenue_cost_chart(
            business_metrics
        )

        if chart:

            return {
                "answer": (
                    "Generated a revenue-versus-cost comparison."
                ),
                "chart": chart,
                "type": "revenue_cost_chart",
            }

    # ========================================================
    # NO MATCH
    # ========================================================

    return {
        "answer": (
            "I could not determine the requested chart "
            "from the available dataset. Try asking for "
            "a product, region, revenue trend, revenue "
            "vs profit, or revenue vs cost chart."
        ),
        "chart": None,
        "type": "unsupported_chart_request",
    }