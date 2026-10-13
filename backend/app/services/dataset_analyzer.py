import os
import re
from typing import Any

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

MAX_TOP_VALUES = 10
MAX_SAMPLE_ROWS = 5
MAX_CORRELATIONS = 20


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value: Any):
    """
    Convert a pandas/numpy numeric value into a normal
    Python float. Return None when conversion fails.
    """

    try:

        if pd.isna(value):
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


def _normalize_column_name(
    column: Any,
) -> str:
    """
    Normalize a column name for matching.
    """

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        str(column).strip().lower(),
    ).strip("_")


def _find_column(
    columns,
    keywords,
):
    """
    Find the first column whose normalized name matches
    one of the supplied keywords.
    """

    normalized_columns = []

    for column in columns:

        normalized = _normalize_column_name(
            column
        )

        normalized_columns.append(
            (
                column,
                normalized,
            )
        )

    # Exact matches first
    for keyword in keywords:

        keyword_normalized = (
            _normalize_column_name(
                keyword
            )
        )

        for column, normalized in normalized_columns:

            if normalized == keyword_normalized:

                return column

    # Partial matches second
    for keyword in keywords:

        keyword_normalized = (
            _normalize_column_name(
                keyword
            )
        )

        for column, normalized in normalized_columns:

            if keyword_normalized in normalized:

                return column

    return None


def _top_values(
    df: pd.DataFrame,
    column,
):
    """
    Return the most common values for a categorical column.
    """

    try:

        counts = (
            df[column]
            .dropna()
            .astype(str)
            .value_counts()
            .head(MAX_TOP_VALUES)
        )

        return [
            {
                "value": str(value),
                "count": int(count),
            }
            for value, count in counts.items()
        ]

    except Exception:

        return []


def _numeric_statistics(
    df: pd.DataFrame,
):
    """
    Calculate statistics for all numeric columns.
    """

    statistics = {}

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        series = df[column]

        statistics[str(column)] = {
            "count": int(
                series.count()
            ),
            "mean": _safe_float(
                series.mean()
            ),
            "median": _safe_float(
                series.median()
            ),
            "min": _safe_float(
                series.min()
            ),
            "max": _safe_float(
                series.max()
            ),
            "sum": _safe_float(
                series.sum()
            ),
            "std": _safe_float(
                series.std()
            ),
        }

    return statistics


def _correlations(
    df: pd.DataFrame,
):
    """
    Calculate meaningful correlations between numeric columns.
    """

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] < 2:
        return {}

    try:

        correlation_matrix = (
            numeric_df.corr()
        )

    except Exception:

        return {}

    result = {}

    columns = list(
        correlation_matrix.columns
    )

    count = 0

    for i in range(
        len(columns)
    ):

        for j in range(
            i + 1,
            len(columns),
        ):

            column_a = columns[i]
            column_b = columns[j]

            value = correlation_matrix.loc[
                column_a,
                column_b,
            ]

            if pd.isna(value):
                continue

            result[
                f"{column_a} vs {column_b}"
            ] = round(
                float(value),
                4,
            )

            count += 1

            if count >= MAX_CORRELATIONS:

                return result

    return result


def _business_metric(
    df: pd.DataFrame,
    column,
):
    """
    Calculate useful business metrics for a detected
    business-related numeric column.
    """

    if column is None:
        return None

    try:

        series = pd.to_numeric(
            df[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        return {
            "column": str(column),
            "count": int(
                series.count()
            ),
            "total": _safe_float(
                series.sum()
            ),
            "average": _safe_float(
                series.mean()
            ),
            "median": _safe_float(
                series.median()
            ),
            "minimum": _safe_float(
                series.min()
            ),
            "maximum": _safe_float(
                series.max()
            ),
        }

    except Exception:

        return None


def _grouped_business_analysis(
    df: pd.DataFrame,
    category_column,
    value_column,
):
    """
    Calculate totals by product, customer, region, etc.
    """

    if category_column is None:
        return []

    if value_column is None:
        return []

    try:

        working = df[
            [
                category_column,
                value_column,
            ]
        ].copy()

        working[value_column] = pd.to_numeric(
            working[value_column],
            errors="coerce",
        )

        working = working.dropna(
            subset=[
                category_column,
                value_column,
            ]
        )

        if working.empty:
            return []

        grouped = (
            working
            .groupby(
                category_column
            )[value_column]
            .agg(
                total="sum",
                average="mean",
                count="count",
            )
            .sort_values(
                "total",
                ascending=False,
            )
            .head(
                MAX_TOP_VALUES
            )
        )

        results = []

        for index, row in grouped.iterrows():

            results.append(
                {
                    "name": str(index),

                    "total": _safe_float(
                        row["total"]
                    ),

                    "average": _safe_float(
                        row["average"]
                    ),

                    "count": int(
                        row["count"]
                    ),
                }
            )

        return results

    except Exception:

        return []

def _grouped_detailed_business_analysis(
    df: pd.DataFrame,
    category_column,
    revenue_column,
    profit_column=None,
    cost_column=None,
    quantity_column=None,
):
    """
    Calculate detailed business metrics grouped by a category.
    """

    if category_column is None:
        return []

    try:
        columns = [category_column]

        for column in [
            revenue_column,
            profit_column,
            cost_column,
            quantity_column,
        ]:
            if column is not None and column not in columns:
                columns.append(column)

        working = df[columns].copy()

        for column in columns:
            if column != category_column:
                working[column] = pd.to_numeric(
                    working[column],
                    errors="coerce",
                )

        working = working.dropna(
            subset=[category_column]
        )

        if working.empty:
            return []

        results = []

        for name, group in working.groupby(category_column):

            revenue = (
                group[revenue_column].sum()
                if revenue_column is not None
                else 0
            )

            profit = (
                group[profit_column].sum()
                if profit_column is not None
                else None
            )

            cost = (
                group[cost_column].sum()
                if cost_column is not None
                else None
            )

            quantity = (
                group[quantity_column].sum()
                if quantity_column is not None
                else None
            )

            revenue = _safe_float(revenue)
            profit = _safe_float(profit)
            cost = _safe_float(cost)
            quantity = _safe_float(quantity)

            margin = None

            if (
                revenue is not None
                and revenue != 0
                and profit is not None
            ):
                margin = (
                    profit / revenue
                ) * 100

            results.append(
                {
                    "name": str(name),
                    "revenue": revenue,
                    "profit": profit,
                    "cost": cost,
                    "quantity": quantity,
                    "profit_margin_percent": (
                        _safe_float(margin)
                    ),
                    "count": int(len(group)),
                }
            )

        return sorted(
            results,
            key=lambda item: (
                item.get("revenue") or 0
            ),
            reverse=True,
        )

    except Exception:
        return []

def _detect_date_column(
    df: pd.DataFrame,
):
    """
    Detect a likely date column.
    """

    date_keywords = [
        "date",
        "day",
        "month",
        "year",
        "time",
        "timestamp",
        "created_at",
        "order_date",
        "sale_date",
    ]

    column = _find_column(
        df.columns,
        date_keywords,
    )

    if column is not None:
        return column

    # Try existing datetime columns
    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):

            return column

    return None


def _date_trend(
    df: pd.DataFrame,
    date_column,
    value_column,
):
    """
    Generate monthly business trends when a date and
    numeric business column are available.
    """

    if date_column is None:
        return []

    if value_column is None:
        return []

    try:

        working = df[
            [
                date_column,
                value_column,
            ]
        ].copy()

        working[date_column] = pd.to_datetime(
            working[date_column],
            errors="coerce",
        )

        working[value_column] = pd.to_numeric(
            working[value_column],
            errors="coerce",
        )

        working = working.dropna(
            subset=[
                date_column,
                value_column,
            ]
        )

        if working.empty:
            return []

        working["period"] = (
            working[date_column]
            .dt.to_period("M")
            .astype(str)
        )

        grouped = (
            working
            .groupby(
                "period"
            )[value_column]
            .agg(
                total="sum",
                average="mean",
                count="count",
            )
            .sort_index()
        )

        results = []

        for period, row in grouped.iterrows():

            results.append(
                {
                    "period": str(period),

                    "total": _safe_float(
                        row["total"]
                    ),

                    "average": _safe_float(
                        row["average"]
                    ),

                    "count": int(
                        row["count"]
                    ),
                }
            )

        return results[-24:]

    except Exception:

        return []


# ============================================================
# ANALYZE DATAFRAME
# ============================================================

def analyze_dataframe(
    df: pd.DataFrame,
):
    """
    Analyze an already-loaded pandas DataFrame.

    This is the core analysis function used by both:
    - analyze_dataset()
    - filtered dashboard analysis
    """

    if not isinstance(
        df,
        pd.DataFrame,
    ):

        raise ValueError(
            "Input must be a pandas DataFrame."
        )

    # --------------------------------------------------------
    # Make a copy so filtering/cleaning never mutates
    # the original DataFrame.
    # --------------------------------------------------------

    df = df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Empty dataset
    # --------------------------------------------------------

    if df.empty:

        return {
            "rows": 0,
            "columns": int(
                len(df.columns)
            ),

            "column_names": [
                str(column)
                for column in df.columns
            ],

            "columns_info": [],
            "numeric_columns": [],
            "categorical_columns": [],
            "numeric_statistics": {},
            "categorical_statistics": {},
            "missing_values": {},
            "correlations": {},
            "detected_business_columns": {},
            "business_metrics": {},
            "products": [],
            "customers": [],
            "regions": [],
            "trends": [],
            "sample_data": [],

            "message": (
                "Dataset is empty."
            ),
        }

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    row_count = int(
        len(df)
    )

    column_count = int(
        len(df.columns)
    )

    # --------------------------------------------------------
    # Column information
    # --------------------------------------------------------

    columns_info = []

    numeric_columns = []
    categorical_columns = []

    for column in df.columns:

        series = df[column]

        dtype = str(
            series.dtype
        )

        missing = int(
            series.isna().sum()
        )

        unique = int(
            series.nunique(
                dropna=True
            )
        )

        info = {
            "name": str(column),
            "dtype": dtype,
            "missing_values": missing,
            "unique_values": unique,
        }

        columns_info.append(
            info
        )

        if pd.api.types.is_numeric_dtype(
            series
        ):

            numeric_columns.append(
                str(column)
            )

        else:

            categorical_columns.append(
                str(column)
            )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    missing_values = {}

    for column in df.columns:

        count = int(
            df[column].isna().sum()
        )

        if count > 0:

            missing_values[
                str(column)
            ] = count

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    numeric_statistics = _numeric_statistics(
        df
    )

    # --------------------------------------------------------
    # Categorical summaries
    # --------------------------------------------------------

    categorical_statistics = {}

    for column in df.columns:

        if str(column) in numeric_columns:
            continue

        values = _top_values(
            df,
            column,
        )

        if values:

            categorical_statistics[
                str(column)
            ] = values

    # --------------------------------------------------------
    # Detect revenue
    # --------------------------------------------------------

    revenue_column = _find_column(
        df.columns,
        [
            "revenue",
            "sales_revenue",
            "total_revenue",
            "gross_revenue",
            "net_revenue",
            "turnover",
            "income",
            "sales_amount",
            "total_sales",
            "sales",
            "amount",
        ],
    )

    # --------------------------------------------------------
    # Detect profit
    # --------------------------------------------------------

    profit_column = _find_column(
        df.columns,
        [
            "profit",
            "net_profit",
            "gross_profit",
            "profit_amount",
            "earnings",
        ],
    )

    # --------------------------------------------------------
    # Detect cost
    # --------------------------------------------------------

    cost_column = _find_column(
        df.columns,
        [
            "cost",
            "total_cost",
            "cost_price",
            "expense",
            "expenses",
        ],
    )

    # --------------------------------------------------------
    # Detect quantity
    # --------------------------------------------------------

    quantity_column = _find_column(
        df.columns,
        [
            "quantity",
            "qty",
            "units",
            "units_sold",
            "volume",
        ],
    )

    # --------------------------------------------------------
    # Detect product
    # --------------------------------------------------------

    product_column = _find_column(
        df.columns,
        [
            "product",
            "product_name",
            "item",
            "item_name",
            "sku",
            "product_id",
        ],
    )

    # --------------------------------------------------------
    # Detect customer
    # --------------------------------------------------------

    customer_column = _find_column(
        df.columns,
        [
            "customer",
            "customer_name",
            "customer_id",
            "client",
            "client_name",
        ],
    )

    # --------------------------------------------------------
    # Detect region
    # --------------------------------------------------------

    region_column = _find_column(
        df.columns,
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
    # Detect date
    # --------------------------------------------------------

    date_column = _detect_date_column(
        df
    )

    # --------------------------------------------------------
    # Business metrics
    # --------------------------------------------------------

    business_metrics = {
        "revenue": _business_metric(
            df,
            revenue_column,
        ),

        "profit": _business_metric(
            df,
            profit_column,
        ),

        "cost": _business_metric(
            df,
            cost_column,
        ),

        "quantity": _business_metric(
            df,
            quantity_column,
        ),
    }

    # --------------------------------------------------------
    # Product analysis
    # --------------------------------------------------------

    products = _grouped_business_analysis(
        df,
        product_column,
        revenue_column,
    )

    if not products:

        products = _grouped_business_analysis(
            df,
            product_column,
            profit_column,
        )


    detailed_products = _grouped_detailed_business_analysis(
         df,
         product_column,
         revenue_column,
         profit_column,
         cost_column,
         quantity_column,
        )

    # --------------------------------------------------------
    # Customer analysis
    # --------------------------------------------------------

    customers = _grouped_business_analysis(
        df,
        customer_column,
        revenue_column,
    )

    if not customers:

        customers = _grouped_business_analysis(
            df,
            customer_column,
            profit_column,
        )

    # --------------------------------------------------------
    # Regional analysis
    # --------------------------------------------------------

    regions = _grouped_business_analysis(
        df,
        region_column,
        revenue_column,
    )

    if not regions:

        regions = _grouped_business_analysis(
            df,
            region_column,
            profit_column,
        )

    detailed_regions = _grouped_detailed_business_analysis(
         df,
         region_column,
         revenue_column,
         profit_column,
         cost_column,
         quantity_column,
        )   
    
    # --------------------------------------------------------
    # Trends
    # --------------------------------------------------------

    trend_value_column = (
        revenue_column
        or profit_column
        or quantity_column
    )

    trends = _date_trend(
        df,
        date_column,
        trend_value_column,
    )

    # --------------------------------------------------------
    # Correlations
    # --------------------------------------------------------

    correlations = _correlations(
        df
    )

    # --------------------------------------------------------
    # Sample data
    # --------------------------------------------------------

    sample_df = (
        df.head(
            MAX_SAMPLE_ROWS
        )
        .copy()
    )

    sample_df = sample_df.fillna("")

    sample_data = (
        sample_df
        .to_dict(
            orient="records"
        )
    )

    # --------------------------------------------------------
    # Detected business columns
    # --------------------------------------------------------

    detected_business_columns = {
        "revenue": (
            str(revenue_column)
            if revenue_column is not None
            else None
        ),

        "profit": (
            str(profit_column)
            if profit_column is not None
            else None
        ),

        "cost": (
            str(cost_column)
            if cost_column is not None
            else None
        ),

        "quantity": (
            str(quantity_column)
            if quantity_column is not None
            else None
        ),

        "product": (
            str(product_column)
            if product_column is not None
            else None
        ),

        "customer": (
            str(customer_column)
            if customer_column is not None
            else None
        ),

        "region": (
            str(region_column)
            if region_column is not None
            else None
        ),

        "date": (
            str(date_column)
            if date_column is not None
            else None
        ),
    }

    # --------------------------------------------------------
    # Final analysis
    # --------------------------------------------------------

    return {
        "rows": row_count,
        "columns": column_count,

        "column_names": [
            str(column)
            for column in df.columns
        ],

        "columns_info": columns_info,

        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,

        "numeric_statistics": numeric_statistics,
        "categorical_statistics": (
            categorical_statistics
        ),

        "missing_values": missing_values,

        "correlations": correlations,

        "detected_business_columns": (
            detected_business_columns
        ),

        "business_metrics": business_metrics,

        "products": products,
        "customers": customers,
        "regions": regions,

        "trends": trends,

        "sample_data": sample_data,
    }


# ============================================================
# LOAD AND ANALYZE DATASET FILE
# ============================================================

def analyze_dataset(
    filepath: str,
):
    """
    Analyze a CSV or Excel business dataset.

    Loads the file once and delegates the actual analysis
    to analyze_dataframe().
    """

    # --------------------------------------------------------
    # Validate filepath
    # --------------------------------------------------------

    if not filepath:

        raise ValueError(
            "Dataset filepath is required."
        )

    if not isinstance(
        filepath,
        str,
    ):

        raise ValueError(
            "Dataset filepath must be a string."
        )

    if not os.path.isfile(
        filepath
    ):

        raise FileNotFoundError(
            f"Dataset file not found: {filepath}"
        )

    # --------------------------------------------------------
    # Determine extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        filepath
    )[1].lower()

    if extension not in {
        ".csv",
        ".xlsx",
        ".xls",
    }:

        raise ValueError(
            "Unsupported dataset format. "
            "Only CSV and Excel files are supported."
        )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    try:

        if extension == ".csv":

            df = pd.read_csv(
                filepath
            )

        else:

            df = pd.read_excel(
                filepath
            )

    except Exception as e:

        raise ValueError(
            f"Unable to read dataset: {str(e)}"
        ) from e

    # --------------------------------------------------------
    # Delegate analysis
    # --------------------------------------------------------

    return analyze_dataframe(
        df
    )