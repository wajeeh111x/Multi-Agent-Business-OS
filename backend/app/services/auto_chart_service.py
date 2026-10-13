from typing import Any


# ============================================================
# SAFE NUMBER
# ============================================================

def _number(
    value: Any,
):
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
# PRODUCT CHART
# ============================================================

def _product_chart(
    products: list,
):
    """
    Build product revenue chart data.
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
    Build regional revenue chart data.
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
# CUSTOMER CHART
# ============================================================

def _customer_chart(
    customers: list,
):
    """
    Build customer revenue chart data.
    """

    if not isinstance(
        customers,
        list,
    ):
        return None

    data = []

    for item in customers:

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
        "title": "Revenue by Customer",
        "x_axis": "Customer",
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
    Build revenue-over-time chart data.
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
    Build revenue vs profit comparison chart.
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
        revenue.get(
            "total"
        )
    )

    profit_total = _number(
        profit.get(
            "total"
        )
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
    Build revenue vs cost comparison chart.
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
        revenue.get(
            "total"
        )
    )

    cost_total = _number(
        cost.get(
            "total"
        )
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
# QUANTITY CHART
# ============================================================

def _quantity_chart(
    business_metrics: dict,
):
    """
    Build quantity KPI visualization data.
    """

    if not isinstance(
        business_metrics,
        dict,
    ):
        return None

    quantity = business_metrics.get(
        "quantity"
    )

    if not isinstance(
        quantity,
        dict,
    ):
        return None

    total = _number(
        quantity.get(
            "total"
        )
    )

    if total is None:
        return None

    return {
        "type": "bar",
        "title": "Quantity Performance",
        "x_axis": "Metric",
        "y_axis": "Quantity",
        "data": [
            {
                "label": "Total Quantity",
                "value": total,
            }
        ],
    }


# ============================================================
# MISSING VALUES CHART
# ============================================================

def _missing_values_chart(
    missing_values: dict,
):
    """
    Build missing-value chart data.
    """

    if not isinstance(
        missing_values,
        dict,
    ):
        return None

    data = []

    for column, count in missing_values.items():

        numeric_count = _number(
            count
        )

        if numeric_count is None:
            continue

        data.append(
            {
                "label": str(column),
                "value": numeric_count,
            }
        )

    if not data:
        return None

    return {
        "type": "bar",
        "title": "Missing Values",
        "x_axis": "Column",
        "y_axis": "Missing Values",
        "data": data,
    }


# ============================================================
# BUILD AUTOMATIC CHARTS
# ============================================================

def build_automatic_charts(
    analysis: dict,
):
    """
    Generate all chart data supported by the dataset.
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

    regions = analysis.get(
        "regions",
        [],
    )

    customers = analysis.get(
        "customers",
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

    missing_values = analysis.get(
        "missing_values",
        {},
    )

    charts = []

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    chart = _product_chart(
        products
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Region
    # --------------------------------------------------------

    chart = _region_chart(
        regions
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    chart = _customer_chart(
        customers
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    chart = _trend_chart(
        trends
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Revenue / Profit
    # --------------------------------------------------------

    chart = _revenue_profit_chart(
        business_metrics
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Revenue / Cost
    # --------------------------------------------------------

    chart = _revenue_cost_chart(
        business_metrics
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    chart = _quantity_chart(
        business_metrics
    )

    if chart is not None:

        charts.append(
            chart
        )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    chart = _missing_values_chart(
        missing_values
    )

    if chart is not None:

        charts.append(
            chart
        )

    return charts