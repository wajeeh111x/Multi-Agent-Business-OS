from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _normalize(
    value: Any,
) -> str:
    """
    Normalize text for column-name matching.
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )


def _is_numeric_column(
    column_info: dict,
) -> bool:
    """
    Determine whether a column is numeric.
    """

    if not isinstance(
        column_info,
        dict,
    ):
        return False

    dtype = str(
        column_info.get(
            "dtype",
            "",
        )
    ).lower()

    return any(
        token in dtype
        for token in (
            "int",
            "float",
            "number",
            "decimal",
        )
    )


def _find_column_by_keywords(
    columns,
    keywords,
):
    """
    Find a dataset column by exact or partial match.
    """

    if not isinstance(
        columns,
        (list, tuple),
    ):
        return None

    normalized_columns = []

    for column in columns:

        normalized_columns.append(
            (
                column,
                _normalize(column),
            )
        )

    # --------------------------------------------------------
    # Exact matches
    # --------------------------------------------------------

    for keyword in keywords:

        keyword_normalized = _normalize(
            keyword
        )

        for column, normalized in normalized_columns:

            if normalized == keyword_normalized:

                return str(column)

    # --------------------------------------------------------
    # Partial matches
    # --------------------------------------------------------

    for keyword in keywords:

        keyword_normalized = _normalize(
            keyword
        )

        for column, normalized in normalized_columns:

            if (
                keyword_normalized in normalized
                or normalized in keyword_normalized
            ):

                return str(column)

    return None


# ============================================================
# DETECT DATASET FEATURES
# ============================================================

def detect_dataset_features(
    analysis: dict,
) -> dict:
    """
    Detect important dataset characteristics.

    Used by the automatic chart engine to determine
    which visualizations make sense for the dataset.
    """

    if not isinstance(
        analysis,
        dict,
    ):

        return {
            "numeric_columns": [],
            "categorical_columns": [],
            "date_column": None,
            "revenue_column": None,
            "profit_column": None,
            "cost_column": None,
            "quantity_column": None,
            "product_column": None,
            "region_column": None,
            "customer_column": None,
        }

    column_names = analysis.get(
        "column_names",
        [],
    )

    columns_info = analysis.get(
        "columns_info",
        [],
    )

    detected = analysis.get(
        "detected_business_columns",
        {},
    )

    if not isinstance(
        detected,
        dict,
    ):
        detected = {}

    numeric_columns = []
    categorical_columns = []

    # --------------------------------------------------------
    # Numeric / categorical columns
    # --------------------------------------------------------

    if isinstance(
        columns_info,
        list,
    ):

        for column_info in columns_info:

            if not isinstance(
                column_info,
                dict,
            ):
                continue

            name = column_info.get(
                "name"
            )

            if name is None:
                continue

            if _is_numeric_column(
                column_info
            ):

                numeric_columns.append(
                    str(name)
                )

            else:

                categorical_columns.append(
                    str(name)
                )

    # --------------------------------------------------------
    # Fallback to analyzer lists
    # --------------------------------------------------------

    if not numeric_columns:

        numeric_columns = [
            str(column)
            for column in analysis.get(
                "numeric_columns",
                [],
            )
        ]

    if not categorical_columns:

        categorical_columns = [
            str(column)
            for column in analysis.get(
                "categorical_columns",
                [],
            )
        ]

    # --------------------------------------------------------
    # Date column
    # --------------------------------------------------------

    date_column = detected.get(
        "date"
    )

    if not date_column:

        date_column = _find_column_by_keywords(
            column_names,
            [
                "date",
                "order_date",
                "sale_date",
                "sales_date",
                "transaction_date",
                "created_at",
                "timestamp",
                "datetime",
                "month",
                "year",
            ],
        )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue_column = detected.get(
        "revenue"
    )

    if not revenue_column:

        revenue_column = _find_column_by_keywords(
            column_names,
            [
                "revenue",
                "sales_revenue",
                "total_revenue",
                "gross_revenue",
                "sales",
                "total_sales",
                "amount",
            ],
        )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit_column = detected.get(
        "profit"
    )

    if not profit_column:

        profit_column = _find_column_by_keywords(
            column_names,
            [
                "profit",
                "net_profit",
                "gross_profit",
                "profit_amount",
                "earnings",
            ],
        )

    # --------------------------------------------------------
    # Cost
    # --------------------------------------------------------

    cost_column = detected.get(
        "cost"
    )

    if not cost_column:

        cost_column = _find_column_by_keywords(
            column_names,
            [
                "cost",
                "total_cost",
                "cost_price",
                "expense",
                "expenses",
            ],
        )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    quantity_column = detected.get(
        "quantity"
    )

    if not quantity_column:

        quantity_column = _find_column_by_keywords(
            column_names,
            [
                "quantity",
                "qty",
                "units",
                "units_sold",
                "volume",
            ],
        )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product_column = detected.get(
        "product"
    )

    if not product_column:

        product_column = _find_column_by_keywords(
            column_names,
            [
                "product",
                "product_name",
                "item",
                "item_type",
                "item_name",
                "sku",
                "product_id",
            ],
        )

    # --------------------------------------------------------
    # Region
    # --------------------------------------------------------

    region_column = detected.get(
        "region"
    )

    if not region_column:

        region_column = _find_column_by_keywords(
            column_names,
            [
                "region",
                "area",
                "territory",
                "location",
                "city",
                "country",
            ],
        )

    # --------------------------------------------------------
    # Customer
    # --------------------------------------------------------

    customer_column = detected.get(
        "customer"
    )

    if not customer_column:

        customer_column = _find_column_by_keywords(
            column_names,
            [
                "customer",
                "customer_name",
                "customer_id",
                "client",
                "client_name",
            ],
        )

    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,

        "date_column": (
            str(date_column)
            if date_column
            else None
        ),

        "revenue_column": (
            str(revenue_column)
            if revenue_column
            else None
        ),

        "profit_column": (
            str(profit_column)
            if profit_column
            else None
        ),

        "cost_column": (
            str(cost_column)
            if cost_column
            else None
        ),

        "quantity_column": (
            str(quantity_column)
            if quantity_column
            else None
        ),

        "product_column": (
            str(product_column)
            if product_column
            else None
        ),

        "region_column": (
            str(region_column)
            if region_column
            else None
        ),

        "customer_column": (
            str(customer_column)
            if customer_column
            else None
        ),
    }


# ============================================================
# RECOMMEND CHARTS
# ============================================================

def recommend_charts(
    analysis: dict,
) -> list:
    """
    Automatically recommend useful charts based on
    the available dataset structure and metrics.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return []

    features = detect_dataset_features(
        analysis
    )

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

    if not isinstance(
        business_metrics,
        dict,
    ):
        business_metrics = {}

    recommendations = []

    # ========================================================
    # PRODUCT REVENUE
    # ========================================================

    if (
        features.get("product_column")
        and isinstance(products, list)
        and len(products) >= 1
    ):

        recommendations.append(
            {
                "chart_type": "bar",
                "chart_key": "product_revenue",
                "title": "Revenue by Product",
                "reason": (
                    "The dataset contains product-level "
                    "performance data."
                ),
                "priority": "high",
            }
        )

    # ========================================================
    # REGION REVENUE
    # ========================================================

    if (
        features.get("region_column")
        and isinstance(regions, list)
        and len(regions) >= 1
    ):

        recommendations.append(
            {
                "chart_type": "bar",
                "chart_key": "regional_revenue",
                "title": "Revenue by Region",
                "reason": (
                    "The dataset contains regional "
                    "performance data."
                ),
                "priority": "high",
            }
        )

    # ========================================================
    # CUSTOMER REVENUE
    # ========================================================

    if (
        features.get("customer_column")
        and isinstance(customers, list)
        and len(customers) >= 1
    ):

        recommendations.append(
            {
                "chart_type": "bar",
                "chart_key": "customer_revenue",
                "title": "Revenue by Customer",
                "reason": (
                    "The dataset contains customer-level "
                    "performance data."
                ),
                "priority": "medium",
            }
        )

    # ========================================================
    # REVENUE TREND
    # ========================================================

    if (
        features.get("date_column")
        and isinstance(trends, list)
        and len(trends) >= 2
    ):

        recommendations.append(
            {
                "chart_type": "line",
                "chart_key": "revenue_trend",
                "title": "Revenue Trend",
                "reason": (
                    "The dataset contains date information "
                    "and multiple time periods."
                ),
                "priority": "high",
            }
        )

    # ========================================================
    # REVENUE VS PROFIT
    # ========================================================

    if (
        features.get("revenue_column")
        and features.get("profit_column")
        and business_metrics.get("revenue")
        and business_metrics.get("profit")
    ):

        recommendations.append(
            {
                "chart_type": "comparison",
                "chart_key": "revenue_profit",
                "title": "Revenue vs Profit",
                "reason": (
                    "Both revenue and profit are available."
                ),
                "priority": "high",
            }
        )

    # ========================================================
    # REVENUE VS COST
    # ========================================================

    if (
        features.get("revenue_column")
        and features.get("cost_column")
        and business_metrics.get("revenue")
        and business_metrics.get("cost")
    ):

        recommendations.append(
            {
                "chart_type": "comparison",
                "chart_key": "revenue_cost",
                "title": "Revenue vs Cost",
                "reason": (
                    "Both revenue and cost are available."
                ),
                "priority": "medium",
            }
        )

    # ========================================================
    # QUANTITY
    # ========================================================

    if (
        features.get("quantity_column")
        and business_metrics.get("quantity")
    ):

        recommendations.append(
            {
                "chart_type": "bar",
                "chart_key": "quantity",
                "title": "Quantity Performance",
                "reason": (
                    "The dataset contains quantity "
                    "measurements."
                ),
                "priority": "medium",
            }
        )

    # ========================================================
    # MISSING VALUES
    # ========================================================

    missing_values = analysis.get(
        "missing_values",
        {},
    )

    if isinstance(
        missing_values,
        dict,
    ) and missing_values:

        recommendations.append(
            {
                "chart_type": "bar",
                "chart_key": "missing_values",
                "title": "Missing Values",
                "reason": (
                    "The dataset contains missing values "
                    "that may require attention."
                ),
                "priority": "low",
            }
        )

    return recommendations