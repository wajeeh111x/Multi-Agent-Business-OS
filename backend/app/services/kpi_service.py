from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _safe_number(value: Any):
    """
    Convert a value into a normal JSON-safe number.
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


def _safe_divide(
    numerator,
    denominator,
):
    """
    Safely divide two numbers.
    """

    if numerator is None:
        return None

    if denominator is None:
        return None

    try:

        denominator = float(
            denominator
        )

        if denominator == 0:
            return None

        return float(numerator) / denominator

    except (
        TypeError,
        ValueError,
        ZeroDivisionError,
    ):

        return None


def _percentage(
    value,
    total,
):
    """
    Calculate value as a percentage of total.

    Rounded to 2 decimal places.
    """

    ratio = _safe_divide(
        value,
        total,
    )

    if ratio is None:
        return None

    return round(
        ratio * 100,
        2,
    )


# ============================================================
# TOP ITEM
# ============================================================

def _top_item(
    items,
):
    """
    Return the first valid dictionary item.
    """

    if not isinstance(
        items,
        list,
    ):
        return None

    for item in items:

        if isinstance(
            item,
            dict,
        ):
            return item

    return None


# ============================================================
# PERIOD ANALYSIS
# ============================================================

def _period_analysis(
    trends,
):
    """
    Calculate:

    - best period
    - worst period
    - first available period
    - latest available period
    - percentage change from first to latest
    """

    if not isinstance(
        trends,
        list,
    ):

        return {
            "best_period": None,
            "worst_period": None,
            "first_period": None,
            "latest_period": None,
            "period_change_percent": None,
        }

    valid_trends = []

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
            item.get(
                "total"
            )
        )

        if (
            period is None
            or total is None
        ):
            continue

        valid_trends.append(
            {
                "period": str(period),
                "total": total,
            }
        )

    if not valid_trends:

        return {
            "best_period": None,
            "worst_period": None,
            "first_period": None,
            "latest_period": None,
            "period_change_percent": None,
        }

    # --------------------------------------------------------
    # Best period
    # --------------------------------------------------------

    best = max(
        valid_trends,
        key=lambda item: item["total"],
    )

    # --------------------------------------------------------
    # Worst period
    # --------------------------------------------------------

    worst = min(
        valid_trends,
        key=lambda item: item["total"],
    )

    # --------------------------------------------------------
    # First and latest available periods
    # --------------------------------------------------------

    first = valid_trends[0]
    latest = valid_trends[-1]

    first_total = first["total"]
    latest_total = latest["total"]

    # --------------------------------------------------------
    # Percentage change
    # --------------------------------------------------------

    if first_total == 0:

        period_change_percent = None

    else:

        period_change_percent = round(
            (
                (
                    latest_total
                    - first_total
                )
                / first_total
            )
            * 100,
            2,
        )

    return {
        "best_period": {
            "period": best["period"],
            "total": best["total"],
        },

        "worst_period": {
            "period": worst["period"],
            "total": worst["total"],
        },

        "first_period": {
            "period": first["period"],
            "total": first["total"],
        },

        "latest_period": {
            "period": latest["period"],
            "total": latest["total"],
        },

        "period_change_percent": (
            period_change_percent
        ),
    }


# ============================================================
# BUILD KPIs
# ============================================================

def build_kpis(
    analysis: dict,
) -> dict:
    """
    Build advanced dashboard-ready KPIs.
    """

    if not isinstance(
        analysis,
        dict,
    ):

        return {
            "rows": 0,
            "columns": 0,
            "revenue": None,
            "profit": None,
            "cost": None,
            "quantity": None,
            "profit_margin_percent": None,
            "average_revenue_per_record": None,
            "top_product": None,
            "top_product_contribution_percent": None,
            "top_customer": None,
            "top_region": None,
            "top_region_contribution_percent": None,
            "best_period": None,
            "worst_period": None,
            "first_period": None,
            "latest_period": None,
            "period_change_percent": None,
        }

    business_metrics = analysis.get(
        "business_metrics",
        {},
    )

    if not isinstance(
        business_metrics,
        dict,
    ):
        business_metrics = {}

    products = analysis.get(
        "products",
        [],
    )

    customers = analysis.get(
        "customers",
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

    # --------------------------------------------------------
    # Business metrics
    # --------------------------------------------------------

    revenue = business_metrics.get(
        "revenue"
    )

    profit = business_metrics.get(
        "profit"
    )

    cost = business_metrics.get(
        "cost"
    )

    quantity = business_metrics.get(
        "quantity"
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue_total = (
        _safe_number(
            revenue.get("total")
        )
        if isinstance(
            revenue,
            dict,
        )
        else None
    )

    revenue_average = (
        _safe_number(
            revenue.get("average")
        )
        if isinstance(
            revenue,
            dict,
        )
        else None
    )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit_total = (
        _safe_number(
            profit.get("total")
        )
        if isinstance(
            profit,
            dict,
        )
        else None
    )

    profit_average = (
        _safe_number(
            profit.get("average")
        )
        if isinstance(
            profit,
            dict,
        )
        else None
    )

    # --------------------------------------------------------
    # Cost
    # --------------------------------------------------------

    cost_total = (
        _safe_number(
            cost.get("total")
        )
        if isinstance(
            cost,
            dict,
        )
        else None
    )

    cost_average = (
        _safe_number(
            cost.get("average")
        )
        if isinstance(
            cost,
            dict,
        )
        else None
    )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    quantity_total = (
        _safe_number(
            quantity.get("total")
        )
        if isinstance(
            quantity,
            dict,
        )
        else None
    )

    quantity_average = (
        _safe_number(
            quantity.get("average")
        )
        if isinstance(
            quantity,
            dict,
        )
        else None
    )

    # --------------------------------------------------------
    # Top items
    # --------------------------------------------------------

    top_product = _top_item(
        products
    )

    top_customer = _top_item(
        customers
    )

    top_region = _top_item(
        regions
    )

    # --------------------------------------------------------
    # Profit margin
    # --------------------------------------------------------

    profit_margin = _percentage(
        profit_total,
        revenue_total,
    )

    # --------------------------------------------------------
    # Top product contribution
    # --------------------------------------------------------

    top_product_total = (
        _safe_number(
            top_product.get(
                "total"
            )
        )
        if top_product
        else None
    )

    top_product_contribution = _percentage(
        top_product_total,
        revenue_total,
    )

    # --------------------------------------------------------
    # Top region contribution
    # --------------------------------------------------------

    top_region_total = (
        _safe_number(
            top_region.get(
                "total"
            )
        )
        if top_region
        else None
    )

    top_region_contribution = _percentage(
        top_region_total,
        revenue_total,
    )

    # --------------------------------------------------------
    # Period analysis
    # --------------------------------------------------------

    period_data = _period_analysis(
        trends
    )

    # --------------------------------------------------------
    # Final KPI response
    # --------------------------------------------------------

    return {
        "rows": _safe_number(
            analysis.get(
                "rows",
                0,
            )
        ),

        "columns": _safe_number(
            analysis.get(
                "columns",
                0,
            )
        ),

        "revenue": {
            "total": revenue_total,
            "average": revenue_average,
        },

        "profit": {
            "total": profit_total,
            "average": profit_average,
        },

        "cost": {
            "total": cost_total,
            "average": cost_average,
        },

        "quantity": {
            "total": quantity_total,
            "average": quantity_average,
        },

        "profit_margin_percent": (
            profit_margin
        ),

        "average_revenue_per_record": (
            revenue_average
        ),

        "top_product": top_product,

        "top_product_contribution_percent": (
            top_product_contribution
        ),

        "top_customer": top_customer,

        "top_region": top_region,

        "top_region_contribution_percent": (
            top_region_contribution
        ),

        "best_period": period_data[
            "best_period"
        ],

        "worst_period": period_data[
            "worst_period"
        ],

        "first_period": period_data[
            "first_period"
        ],

        "latest_period": period_data[
            "latest_period"
        ],

        "period_change_percent": (
            period_data[
                "period_change_percent"
            ]
        ),
    }


# ============================================================
# PRODUCT DATA
# ============================================================

def get_products(
    analysis: dict,
) -> list:
    """
    Return product-level performance.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return []

    products = analysis.get(
        "products",
        [],
    )

    if not isinstance(
        products,
        list,
    ):
        return []

    return [
        item
        for item in products
        if isinstance(
            item,
            dict,
        )
    ]


# ============================================================
# REGION DATA
# ============================================================

def get_regions(
    analysis: dict,
) -> list:
    """
    Return region-level performance.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return []

    regions = analysis.get(
        "regions",
        [],
    )

    if not isinstance(
        regions,
        list,
    ):
        return []

    return [
        item
        for item in regions
        if isinstance(
            item,
            dict,
        )
    ]


# ============================================================
# TREND DATA
# ============================================================

def get_trends(
    analysis: dict,
) -> list:
    """
    Return time-based business trends.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return []

    trends = analysis.get(
        "trends",
        [],
    )

    if not isinstance(
        trends,
        list,
    ):
        return []

    return [
        item
        for item in trends
        if isinstance(
            item,
            dict,
        )
    ]