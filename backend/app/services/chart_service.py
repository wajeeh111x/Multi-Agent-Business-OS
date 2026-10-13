from typing import Any, Optional


# ============================================================
# SAFE NUMBER
# ============================================================

def _safe_number(
    value: Any,
) -> Optional[float]:
    """
    Convert a value to a JSON-safe number.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return int(value)

    if isinstance(
        value,
        (int, float),
    ):
        return value

    try:

        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# BAR CHART — PRODUCTS
# ============================================================

def build_product_chart(
    products: list,
    limit: int = 10,
):
    """
    Build chart-ready product data.
    """

    if not isinstance(
        products,
        list,
    ):
        return None

    data = []

    for item in products[:limit]:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        total = _safe_number(
            item.get("total")
        )

        if name is None or total is None:
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
        "title": "Revenue by Product",
        "x_axis": "Product",
        "y_axis": "Revenue",
        "data": data,
    }


# ============================================================
# BAR CHART — REGIONS
# ============================================================

def build_region_chart(
    regions: list,
    limit: int = 10,
):
    """
    Build chart-ready regional data.
    """

    if not isinstance(
        regions,
        list,
    ):
        return None

    data = []

    for item in regions[:limit]:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        total = _safe_number(
            item.get("total")
        )

        if name is None or total is None:
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
# LINE CHART — TRENDS
# ============================================================

def build_trend_chart(
    trends: list,
):
    """
    Build chart-ready time trend data.
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

        total = _safe_number(
            item.get("total")
        )

        if period is None or total is None:
            continue

        data.append(
            {
                "label": str(period),
                "value": total,
            }
        )

    if not data:
        return None

    return {
        "type": "line",
        "title": "Revenue Trend",
        "x_axis": "Period",
        "y_axis": "Revenue",
        "data": data,
    }


# ============================================================
# BUILD ALL CHARTS
# ============================================================

def build_charts(
    products: list,
    regions: list,
    trends: list,
):
    """
    Build all available dashboard charts.
    """

    charts = []

    product_chart = build_product_chart(
        products
    )

    if product_chart is not None:

        charts.append(
            product_chart
        )

    region_chart = build_region_chart(
        regions
    )

    if region_chart is not None:

        charts.append(
            region_chart
        )

    trend_chart = build_trend_chart(
        trends
    )

    if trend_chart is not None:

        charts.append(
            trend_chart
        )

    return charts