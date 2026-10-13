import pandas as pd


def load_dataset(filepath: str):
    """
    Load a CSV or Excel business dataset.
    """

    if filepath.lower().endswith(".csv"):
        return pd.read_csv(filepath)

    if filepath.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(filepath)

    raise ValueError(
        "Unsupported file format. Use CSV or Excel."
    )


def dataset_summary(filepath: str):

    df = load_dataset(filepath)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict()
    }


def preview_dataset(filepath: str, rows: int = 5):

    df = load_dataset(filepath)

    return df.head(rows).to_dict(
        orient="records"
    )


def numeric_summary(filepath: str):

    df = load_dataset(filepath)

    numeric = df.select_dtypes(
        include="number"
    )

    if numeric.empty:
        return {
            "message": "No numeric columns found."
        }

    return numeric.describe().to_dict()