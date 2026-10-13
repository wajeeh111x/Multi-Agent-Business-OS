from datetime import datetime, timezone
from typing import Any, Optional


# ============================================================
# DASHBOARD SERVICE
# ============================================================

def _safe_value(
    value: Any,
):
    """
    Convert values into JSON-safe Python values.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        (int, float, str),
    ):
        return value

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return str(value)


# ============================================================
# BUILD DASHBOARD DATA
# ============================================================

def build_dashboard(
    dataset_id: str,
    filename: str,
    analysis: dict,
    kpis: dict,
    insights: dict,
    products: list,
    regions: list,
    trends: list,
    filters: Optional[dict] = None,
):
    """
    Build one dashboard-ready response.

    The frontend can use this response for:

    - KPI cards
    - charts
    - tables
    - insights
    - recommendations
    - active filters
    """

    # --------------------------------------------------------
    # Normalize inputs
    # --------------------------------------------------------

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

    if not isinstance(
        insights,
        dict,
    ):
        insights = {}

    if not isinstance(
        products,
        list,
    ):
        products = []

    if not isinstance(
        regions,
        list,
    ):
        regions = []

    if not isinstance(
        trends,
        list,
    ):
        trends = []

    # --------------------------------------------------------
    # Normalize filters
    # --------------------------------------------------------

    if not isinstance(
        filters,
        dict,
    ):
        filters = {}

    normalized_filters = {
        "product": filters.get(
            "product"
        ),
        "region": filters.get(
            "region"
        ),
        "start_date": filters.get(
            "start_date"
        ),
        "end_date": filters.get(
            "end_date"
        ),
    }

    # --------------------------------------------------------
    # Normalize insight fields
    # --------------------------------------------------------

    summary = insights.get(
        "summary",
        "",
    )

    if not isinstance(
        summary,
        str,
    ):
        summary = str(summary)

    insight_items = insights.get(
        "insights",
        [],
    )

    if not isinstance(
        insight_items,
        list,
    ):
        insight_items = []

    recommendations = insights.get(
        "recommendations",
        [],
    )

    if not isinstance(
        recommendations,
        list,
    ):
        recommendations = []

    # --------------------------------------------------------
    # Build dashboard
    # --------------------------------------------------------

    return {
        "dataset": {
            "dataset_id": dataset_id,
            "filename": filename,

            "rows": _safe_value(
                analysis.get(
                    "rows",
                    0,
                )
            ),

            "columns": _safe_value(
                analysis.get(
                    "columns",
                    0,
                )
            ),

            "filters": normalized_filters,

            "generated_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        },

        # ----------------------------------------------------
        # KPI cards
        # ----------------------------------------------------

        "kpis": kpis,

        # ----------------------------------------------------
        # Chart/table data
        # ----------------------------------------------------

        "charts": {
            "products": products,
            "regions": regions,
            "trends": trends,
        },

        # ----------------------------------------------------
        # Insights
        # ----------------------------------------------------

        "insights": {
            "summary": summary,
            "items": insight_items,
            "recommendations": recommendations,
        },
    }