import os
import pandas as pd


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load CSV or Excel dataset.
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            "Dataset file not found."
        )

    extension = os.path.splitext(filepath)[1].lower()

    if extension == ".csv":
        return pd.read_csv(filepath)

    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(filepath)

    raise ValueError(
        "Unsupported dataset format."
    )


# ============================================================
# DATASET OVERVIEW
# ============================================================

def dataset_overview(filepath: str):
    """
    Generate a basic BI overview of a dataset.
    """

    df = load_dataset(filepath)

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    overview = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_values": {
            column: int(df[column].isna().sum())
            for column in df.columns
        }
    }

    return overview


# ============================================================
# NUMERIC KPI SUMMARY
# ============================================================

def numeric_summary(filepath: str):
    """
    Generate statistics for numeric business columns.
    """

    df = load_dataset(filepath)

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.empty:
        return {}

    summary = {}

    for column in numeric_df.columns:

        series = numeric_df[column].dropna()

        if series.empty:
            continue

        summary[column] = {
            "sum": float(series.sum()),
            "average": float(series.mean()),
            "minimum": float(series.min()),
            "maximum": float(series.max()),
            "median": float(series.median())
        }

    return summary


# ============================================================
# TOP CATEGORIES
# ============================================================

def top_categories(
    filepath: str,
    limit: int = 10
):
    """
    Find the most common values in categorical columns.
    """

    df = load_dataset(filepath)

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns

    result = {}

    for column in categorical_columns:

        values = (
            df[column]
            .dropna()
            .value_counts()
            .head(limit)
        )

        result[column] = {
            str(key): int(value)
            for key, value in values.items()
        }

    return result


# ============================================================
# FULL BI ANALYSIS
# ============================================================

def generate_bi_analysis(filepath: str):

    overview = dataset_overview(filepath)

    statistics = numeric_summary(filepath)

    categories = top_categories(filepath)

    return {
        "overview": overview,
        "numeric_summary": statistics,
        "top_categories": categories
    }