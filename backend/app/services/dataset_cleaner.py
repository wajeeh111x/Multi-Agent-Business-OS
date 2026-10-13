import pandas as pd


def clean_dataframe(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    remove_empty_columns: bool = True,
    fill_missing_numeric: bool = True,
    fill_missing_text: bool = True,
):
    if df is None:
        raise ValueError(
            "Dataset is required."
        )

    if df.empty:
        return {
            "dataframe": df,
            "stats": {
                "original_rows": 0,
                "cleaned_rows": 0,
                "removed_duplicates": 0,
                "removed_empty_columns": 0,
                "filled_numeric_values": 0,
                "filled_text_values": 0,
            },
        }

    df = df.copy()

    original_rows = len(df)
    original_columns = len(df.columns)

    # --------------------------------------------------
    # Clean column names
    # --------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------
    # Remove completely empty columns
    # --------------------------------------------------

    empty_columns = []

    if remove_empty_columns:

        empty_columns = [
            column
            for column in df.columns
            if df[column].isna().all()
        ]

        if empty_columns:
            df = df.drop(
                columns=empty_columns
            )

    # --------------------------------------------------
    # Trim text values
    # --------------------------------------------------

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

        df[column] = df[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "null": pd.NA,
            }
        )

    # --------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------

    duplicates_before = int(
        df.duplicated().sum()
    )

    if remove_duplicates:
        df = df.drop_duplicates()

    # --------------------------------------------------
    # Fill missing numeric values
    # --------------------------------------------------

    filled_numeric_values = 0

    if fill_missing_numeric:

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_columns:

            missing = int(
                df[column].isna().sum()
            )

            if missing > 0:

                median = df[column].median()

                if pd.notna(median):

                    df[column] = (
                        df[column].fillna(
                            median
                        )
                    )

                    filled_numeric_values += (
                        missing
                    )

    # --------------------------------------------------
    # Fill missing text values
    # --------------------------------------------------

    filled_text_values = 0

    if fill_missing_text:

        text_columns = df.select_dtypes(
            include=["object", "string"]
        ).columns

        for column in text_columns:

            missing = int(
                df[column].isna().sum()
            )

            if missing > 0:

                df[column] = (
                    df[column].fillna(
                        "Unknown"
                    )
                )

                filled_text_values += (
                    missing
                )

    # --------------------------------------------------
    # Detect and convert date columns
    # --------------------------------------------------

    for column in df.columns:

        if (
            df[column].dtype
            in ["object", "string"]
        ):

            name = str(column).lower()

            looks_like_date = (
                "date" in name
                or "time" in name
                or "month" in name
            )

            if not looks_like_date:
                continue

            converted = pd.to_datetime(
                df[column],
                errors="coerce",
            )

            valid_count = int(
                converted.notna().sum()
            )

            if valid_count > 0:

                df[column] = converted

    # --------------------------------------------------
    # Reset index
    # --------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    cleaned_rows = len(df)
    cleaned_columns = len(df.columns)

    stats = {
        "original_rows": original_rows,
        "cleaned_rows": cleaned_rows,
        "original_columns": original_columns,
        "cleaned_columns": cleaned_columns,
        "removed_duplicates": (
            duplicates_before
            if remove_duplicates
            else 0
        ),
        "removed_empty_columns": len(
            empty_columns
        ),
        "filled_numeric_values": (
            filled_numeric_values
        ),
        "filled_text_values": (
            filled_text_values
        ),
        "rows_removed": (
            original_rows - cleaned_rows
        ),
        "columns_removed": (
            original_columns - cleaned_columns
        ),
    }

    return {
        "dataframe": df,
        "stats": stats,
    } 