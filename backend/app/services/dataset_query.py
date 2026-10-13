import os
import re
import pandas as pd


# ============================================================
# LOAD DATASET
# ============================================================

def load_business_dataset(filepath: str) -> pd.DataFrame:
    """
    Load CSV or Excel business dataset.
    """

    if not filepath:
        raise ValueError("Dataset filepath is required.")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found: {filepath}"
        )

    extension = os.path.splitext(filepath)[1].lower()

    try:

        if extension == ".csv":
            df = pd.read_csv(filepath)

        elif extension in {".xlsx", ".xls"}:
            df = pd.read_excel(filepath)

        else:
            raise ValueError(
                "Unsupported dataset format."
            )

    except Exception as e:

        raise ValueError(
            f"Unable to read dataset: {str(e)}"
        )

    if df.empty:
        raise ValueError(
            "The dataset is empty."
        )

    return clean_dataset(df)


# ============================================================
# CLEAN DATASET
# ============================================================

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Remove empty rows
    df = df.dropna(
        how="all"
    )

    # Remove empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # Clean strings
    for column in df.select_dtypes(
        include=["object"]
    ).columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    return df


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value: str) -> str:

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value).lower()
    ).strip()


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(
    df: pd.DataFrame,
    keywords: list[str]
):
    """
    Flexible column matching.
    """

    columns = list(df.columns)

    normalized_columns = {
        column: normalize_text(column)
        for column in columns
    }

    # Exact match
    for column, normalized in normalized_columns.items():

        for keyword in keywords:

            if normalized == normalize_text(keyword):

                return column

    # Word-based match
    for column, normalized in normalized_columns.items():

        column_words = set(
            normalized.split()
        )

        for keyword in keywords:

            keyword_normalized = normalize_text(
                keyword
            )

            keyword_words = set(
                keyword_normalized.split()
            )

            if keyword_words.issubset(
                column_words
            ):

                return column

    # Partial match
    for column, normalized in normalized_columns.items():

        for keyword in keywords:

            keyword_normalized = normalize_text(
                keyword
            )

            if (
                keyword_normalized
                and keyword_normalized in normalized
            ):

                return column

    return None


# ============================================================
# FIND NUMERIC COLUMN
# ============================================================

def numeric_column(
    df: pd.DataFrame,
    keywords: list[str]
):

    column = find_column(
        df,
        keywords
    )

    if column is not None:

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if numeric_values.notna().sum() > 0:
            return column

    # Fallback:
    # Find a numeric column if the requested
    # keyword did not match a column.

    numeric_candidates = []

    for column in df.columns:

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        valid_count = numeric_values.notna().sum()

        if valid_count > 0:

            numeric_candidates.append(
                (
                    column,
                    valid_count
                )
            )

    if len(numeric_candidates) == 1:

        return numeric_candidates[0][0]

    return None


# ============================================================
# GET NUMERIC VALUES
# ============================================================

def get_numeric_values(
    df: pd.DataFrame,
    column
):

    if column is None:
        return None

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()


# ============================================================
# TOTAL
# ============================================================

def calculate_total(
    df: pd.DataFrame,
    keywords: list[str]
):

    column = numeric_column(
        df,
        keywords
    )

    if column is None:
        return None, None

    values = get_numeric_values(
        df,
        column
    )

    if values is None or values.empty:
        return None, None

    return column, values.sum()


# ============================================================
# AVERAGE
# ============================================================

def calculate_average(
    df: pd.DataFrame,
    keywords: list[str]
):

    column = numeric_column(
        df,
        keywords
    )

    if column is None:
        return None, None

    values = get_numeric_values(
        df,
        column
    )

    if values is None or values.empty:
        return None, None

    return column, values.mean()


# ============================================================
# MAXIMUM
# ============================================================

def calculate_maximum(
    df: pd.DataFrame,
    keywords: list[str]
):

    column = numeric_column(
        df,
        keywords
    )

    if column is None:
        return None, None

    values = get_numeric_values(
        df,
        column
    )

    if values is None or values.empty:
        return None, None

    return column, values.max()


# ============================================================
# MINIMUM
# ============================================================

def calculate_minimum(
    df: pd.DataFrame,
    keywords: list[str]
):

    column = numeric_column(
        df,
        keywords
    )

    if column is None:
        return None, None

    values = get_numeric_values(
        df,
        column
    )

    if values is None or values.empty:
        return None, None

    return column, values.min()


# ============================================================
# TOP CATEGORY
# ============================================================

def top_category(
    df: pd.DataFrame,
    category_keywords: list[str],
    value_keywords: list[str]
):

    category_column = find_column(
        df,
        category_keywords
    )

    value_column = numeric_column(
        df,
        value_keywords
    )

    if (
        category_column is None
        or value_column is None
    ):
        return None

    temp = df.copy()

    temp[value_column] = pd.to_numeric(
        temp[value_column],
        errors="coerce"
    )

    temp = temp.dropna(
        subset=[value_column]
    )

    if temp.empty:
        return None

    grouped = (
        temp
        .groupby(category_column)[value_column]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if grouped.empty:
        return None

    category = grouped.index[0]
    value = grouped.iloc[0]

    return {
        "category": str(category),
        "value": float(value),
        "category_column": category_column,
        "value_column": value_column
    }


# ============================================================
# DATASET SUMMARY
# ============================================================

def dataset_summary(
    filepath: str
):

    df = load_business_dataset(
        filepath
    )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [
            str(column)
            for column in df.columns
        ]
    }


# ============================================================
# AVAILABLE NUMERIC COLUMNS
# ============================================================

def get_numeric_columns(
    df: pd.DataFrame
):

    numeric_columns = []

    for column in df.columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if values.notna().sum() > 0:

            numeric_columns.append(
                str(column)
            )

    return numeric_columns


# ============================================================
# ANSWER BUSINESS QUESTION
# ============================================================

def answer_business_question(
    filepath: str,
    question: str
):

    if not question or not question.strip():

        return {
            "answer": "Question is required.",
            "result": None
        }

    df = load_business_dataset(
        filepath
    )

    text = normalize_text(
        question
    )

    # ========================================================
    # DATASET SUMMARY
    # ========================================================

    summary_words = [
        "summary",
        "overview",
        "dataset information",
        "what is in this dataset",
        "what does this dataset contain",
        "show columns",
        "list columns",
        "columns",
        "dataset details"
    ]

    if any(
        phrase in text
        for phrase in summary_words
    ):

        result = dataset_summary(
            filepath
        )

        return {
            "answer": (
                f"The dataset contains "
                f"{result['rows']} rows and "
                f"{result['columns']} columns.\n\n"
                f"Columns: "
                f"{', '.join(result['column_names'])}"
            ),
            "result": result
        }

    # ========================================================
    # SHOW NUMERIC COLUMNS
    # ========================================================

    if (
        "numeric columns" in text
        or "number columns" in text
    ):

        columns = get_numeric_columns(
            df
        )

        return {
            "answer": (
                "Numeric columns: "
                + (
                    ", ".join(columns)
                    if columns
                    else "None found."
                )
            ),
            "result": {
                "numeric_columns": columns
            }
        }

    # ========================================================
    # NUMBER OF ORDERS / RECORDS / ROWS
    # ========================================================

    order_words = [
        "number of orders",
        "how many orders",
        "total orders",
        "count of orders",
        "number of records",
        "how many records",
        "total records",
        "how many sales",
        "number of sales",
        "how many rows",
        "number of rows"
    ]

    if any(
        phrase in text
        for phrase in order_words
    ):

        order_column = find_column(
            df,
            [
                "order id",
                "order_id",
                "order",
                "id"
            ]
        )

        if order_column:

            count = (
                df[order_column]
                .dropna()
                .nunique()
            )

        else:

            count = len(df)

        return {
            "answer": (
                f"The dataset contains "
                f"{count:,} orders/records."
            ),
            "result": {
                "count": int(count)
            }
        }

    # ========================================================
    # TOTAL SALES / REVENUE
    # ========================================================

    sales_words = [
        "total sales",
        "sales total",
        "sales revenue",
        "total revenue",
        "revenue",
        "how much sales",
        "how much revenue",
        "sales amount",
        "sales value",
        "total amount",
        "total sales amount"
    ]

    if any(
        phrase in text
        for phrase in sales_words
    ):

        column, total = calculate_total(
            df,
            [
                "sales",
                "sale",
                "revenue",
                "amount",
                "total sales",
                "sales amount",
                "sales value"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Total {column} is "
                    f"{total:,.2f}."
                ),
                "result": {
                    "column": column,
                    "total": float(total)
                }
            }

    # ========================================================
    # AVERAGE SALES
    # ========================================================

    if (
        "average sales" in text
        or "average revenue" in text
        or "average sale" in text
        or "mean sales" in text
        or "average sales amount" in text
    ):

        column, average = calculate_average(
            df,
            [
                "sales",
                "sale",
                "revenue",
                "amount",
                "sales amount"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Average {column} is "
                    f"{average:,.2f}."
                ),
                "result": {
                    "column": column,
                    "average": float(average)
                }
            }

    # ========================================================
    # TOTAL PROFIT
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "total profit",
            "profit total",
            "how much profit",
            "overall profit"
        ]
    ):

        column, total = calculate_total(
            df,
            [
                "profit",
                "net profit",
                "gross profit"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Total {column} is "
                    f"{total:,.2f}."
                ),
                "result": {
                    "column": column,
                    "total": float(total)
                }
            }

    # ========================================================
    # AVERAGE PROFIT
    # ========================================================

    if (
        "average profit" in text
        or "mean profit" in text
    ):

        column, average = calculate_average(
            df,
            [
                "profit",
                "net profit",
                "gross profit"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Average {column} is "
                    f"{average:,.2f}."
                ),
                "result": {
                    "column": column,
                    "average": float(average)
                }
            }

    # ========================================================
    # HIGHEST SALES
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "highest sales",
            "maximum sales",
            "largest sale",
            "highest revenue",
            "maximum revenue",
            "highest sale"
        ]
    ):

        column, maximum = calculate_maximum(
            df,
            [
                "sales",
                "sale",
                "revenue",
                "amount"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Highest {column} is "
                    f"{maximum:,.2f}."
                ),
                "result": {
                    "column": column,
                    "maximum": float(maximum)
                }
            }

    # ========================================================
    # LOWEST SALES
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "lowest sales",
            "minimum sales",
            "smallest sale",
            "lowest revenue",
            "minimum revenue",
            "lowest sale"
        ]
    ):

        column, minimum = calculate_minimum(
            df,
            [
                "sales",
                "sale",
                "revenue",
                "amount"
            ]
        )

        if column:

            return {
                "answer": (
                    f"Lowest {column} is "
                    f"{minimum:,.2f}."
                ),
                "result": {
                    "column": column,
                    "minimum": float(minimum)
                }
            }

    # ========================================================
    # TOP PRODUCT
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "top product",
            "best product",
            "best selling product",
            "highest selling product",
            "product with highest sales",
            "which product sold the most",
            "best performing product",
            "most profitable product"
        ]
    ):

        result = top_category(
            df,
            [
                "product",
                "product name",
                "item",
                "item name"
            ],
            [
                "sales",
                "revenue",
                "amount",
                "profit"
            ]
        )

        if result:

            return {
                "answer": (
                    f"Top product is "
                    f"{result['category']} "
                    f"with total "
                    f"{result['value_column']} of "
                    f"{result['value']:,.2f}."
                ),
                "result": result
            }

    # ========================================================
    # TOP REGION
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "top region",
            "best region",
            "highest sales region",
            "region with highest sales",
            "best performing region",
            "which region sells the most"
        ]
    ):

        result = top_category(
            df,
            [
                "region",
                "area",
                "territory",
                "location"
            ],
            [
                "sales",
                "revenue",
                "amount",
                "profit"
            ]
        )

        if result:

            return {
                "answer": (
                    f"Top region is "
                    f"{result['category']} "
                    f"with total "
                    f"{result['value_column']} of "
                    f"{result['value']:,.2f}."
                ),
                "result": result
            }

    # ========================================================
    # TOP CUSTOMER
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "top customer",
            "best customer",
            "highest spending customer",
            "customer with highest sales",
            "customer who spent the most"
        ]
    ):

        result = top_category(
            df,
            [
                "customer",
                "customer name",
                "client",
                "client name"
            ],
            [
                "sales",
                "revenue",
                "amount",
                "profit"
            ]
        )

        if result:

            return {
                "answer": (
                    f"Top customer is "
                    f"{result['category']} "
                    f"with total "
                    f"{result['value_column']} of "
                    f"{result['value']:,.2f}."
                ),
                "result": result
            }

    # ========================================================
    # FALLBACK
    # ========================================================

    return {
        "answer": (
            "I could not determine the requested "
            "business calculation from the dataset.\n\n"
            "Try asking about total sales, average sales, "
            "profit, number of orders, top product, "
            "top region, top customer, or dataset summary."
        ),
        "result": None
    }