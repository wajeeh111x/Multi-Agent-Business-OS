from typing import Optional

import pandas as pd


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def _normalize_column_name(
    column,
) -> str:
    """
    Normalize a column name for matching.
    """

    text = str(
        column
    ).strip().lower()

    for character in [
        " ",
        "-",
        "/",
    ]:
        text = text.replace(
            character,
            "_",
        )

    while "__" in text:
        text = text.replace(
            "__",
            "_",
        )

    return text.strip("_")


# ============================================================
# FIND COLUMN
# ============================================================

def _find_matching_column(
    columns,
    candidates,
):
    """
    Find a matching dataset column.
    """

    normalized_columns = []

    for column in columns:

        normalized_columns.append(
            (
                column,
                _normalize_column_name(
                    column
                ),
            )
        )

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for candidate in candidates:

        candidate_normalized = (
            _normalize_column_name(
                candidate
            )
        )

        for column, normalized in normalized_columns:

            if normalized == candidate_normalized:

                return column

    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    for candidate in candidates:

        candidate_normalized = (
            _normalize_column_name(
                candidate
            )
        )

        for column, normalized in normalized_columns:

            if (
                candidate_normalized in normalized
                or normalized in candidate_normalized
            ):

                return column

    return None


# ============================================================
# FIND DATE COLUMN
# ============================================================

def _find_date_column(
    columns,
):
    """
    Find a likely date column.
    """

    return _find_matching_column(
        columns,
        [
            "date",
            "order_date",
            "orderdate",
            "sale_date",
            "saledate",
            "sales_date",
            "salesdate",
            "transaction_date",
            "transactiondate",
            "created_at",
            "created_date",
            "timestamp",
            "datetime",
            "shipping_date",
            "ship_date",
            "delivery_date",
            "day",
            "month",
            "year",
        ],
    )


# ============================================================
# PARSE FILTER DATE
# ============================================================

def _parse_filter_date(
    value: Optional[str],
    is_end: bool = False,
):
    """
    Parse a date filter.

    Supports:

        YYYY-MM
        YYYY-MM-DD

    For YYYY-MM:

        start_date -> first day of month
        end_date   -> last day of month
    """

    if value is None:

        return None

    value = str(
        value
    ).strip()

    if not value:

        return None

    try:

        # ----------------------------------------------------
        # Month format
        # ----------------------------------------------------

        if len(value) == 7:

            period = pd.Period(
                value,
                freq="M",
            )

            if is_end:

                return (
                    period.end_time
                    .normalize()
                )

            return (
                period.start_time
                .normalize()
            )

        # ----------------------------------------------------
        # Full date
        # ----------------------------------------------------

        parsed = pd.Timestamp(
            value
        )

        return parsed.normalize()

    except Exception as e:

        raise ValueError(
            f"Invalid date filter '{value}'. "
            "Use YYYY-MM or YYYY-MM-DD."
        ) from e


# ============================================================
# FILTER DATAFRAME
# ============================================================

def filter_dataframe(
    df: pd.DataFrame,
    product: Optional[str] = None,
    region: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Filter a dataframe by:

    - product
    - region
    - start date
    - end date

    All supplied filters use AND logic.
    """

    if not isinstance(
        df,
        pd.DataFrame,
    ):

        raise ValueError(
            "Expected a pandas DataFrame."
        )

    filtered = df.copy()

    # ========================================================
    # PRODUCT FILTER
    # ========================================================

    if product is not None:

        product = str(
            product
        ).strip()

        if not product:

            raise ValueError(
                "Product filter cannot be empty."
            )

        product_column = _find_matching_column(
            filtered.columns,
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

        if product_column is None:

            raise ValueError(
                "Product column is not available "
                "in this dataset. Available columns: "
                + ", ".join(
                    str(column)
                    for column in filtered.columns
                )
            )

        filtered = filtered[
            filtered[product_column]
            .astype(str)
            .str.strip()
            .str.casefold()
            == product.casefold()
        ]

    # ========================================================
    # REGION FILTER
    # ========================================================

    if region is not None:

        region = str(
            region
        ).strip()

        if not region:

            raise ValueError(
                "Region filter cannot be empty."
            )

        region_column = _find_matching_column(
            filtered.columns,
            [
                "region",
                "area",
                "territory",
                "location",
                "city",
                "country",
            ],
        )

        if region_column is None:

            raise ValueError(
                "Region column is not available "
                "in this dataset. Available columns: "
                + ", ".join(
                    str(column)
                    for column in filtered.columns
                )
            )

        filtered = filtered[
            filtered[region_column]
            .astype(str)
            .str.strip()
            .str.casefold()
            == region.casefold()
        ]

    # ========================================================
    # DATE FILTER
    # ========================================================

    if (
        start_date is not None
        or end_date is not None
    ):

        date_column = _find_date_column(
            filtered.columns
        )

        if date_column is None:

            raise ValueError(
                "Date column is not available "
                "in this dataset. Available columns: "
                + ", ".join(
                    str(column)
                    for column in filtered.columns
                )
            )

        # ----------------------------------------------------
        # Convert dates
        # ----------------------------------------------------

        parsed_dates = pd.to_datetime(
            filtered[date_column],
            errors="coerce",
        )

        # ----------------------------------------------------
        # Parse boundaries
        # ----------------------------------------------------

        start = _parse_filter_date(
            start_date,
            is_end=False,
        )

        end = _parse_filter_date(
            end_date,
            is_end=True,
        )

        # ----------------------------------------------------
        # Validate range
        # ----------------------------------------------------

        if (
            start is not None
            and end is not None
            and start > end
        ):

            raise ValueError(
                "start_date cannot be later than end_date."
            )

        # ----------------------------------------------------
        # Start date
        # ----------------------------------------------------

        if start is not None:

            mask = (
                parsed_dates >= start
            )

            filtered = filtered[
                mask
            ]

            parsed_dates = parsed_dates[
                filtered.index
            ]

        # ----------------------------------------------------
        # End date
        # ----------------------------------------------------

        if end is not None:

            mask = (
                parsed_dates <= end
            )

            filtered = filtered[
                mask
            ]

    return filtered