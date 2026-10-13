import pandas as pd


def analyze_data_quality(df: pd.DataFrame):

    if df is None or df.empty:
        return {
            "quality_score": 0,
            "status": "empty",
            "rows": 0,
            "columns": 0,
            "missing_values": {},
            "duplicate_rows": 0,
            "empty_columns": [],
            "constant_columns": [],
            "column_quality": [],
            "warnings": [
                "Dataset is empty."
            ],
            "recommendations": [
                "Upload a dataset containing records."
            ],
        }

    rows = len(df)
    columns = len(df.columns)

    # --------------------------------------------------
    # Missing values
    # --------------------------------------------------

    missing_values = {}

    for column in df.columns:

        missing = int(
            df[column].isna().sum()
        )

        if missing > 0:
            missing_values[str(column)] = {
                "count": missing,
                "percentage": round(
                    (missing / rows) * 100,
                    2
                ),
            }

    # --------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    # --------------------------------------------------
    # Empty columns
    # --------------------------------------------------

    empty_columns = []

    for column in df.columns:

        if df[column].isna().all():
            empty_columns.append(
                str(column)
            )

    # --------------------------------------------------
    # Constant columns
    # --------------------------------------------------

    constant_columns = []

    for column in df.columns:

        if df[column].nunique(
            dropna=True
        ) <= 1:

            constant_columns.append(
                str(column)
            )

    # --------------------------------------------------
    # Column quality
    # --------------------------------------------------

    column_quality = []

    for column in df.columns:

        series = df[column]

        missing = int(
            series.isna().sum()
        )

        unique = int(
            series.nunique(
                dropna=True
            )
        )

        column_quality.append({
            "column": str(column),
            "dtype": str(series.dtype),
            "rows": rows,
            "missing": missing,
            "missing_percentage": round(
                (missing / rows) * 100,
                2
            ),
            "unique_values": unique,
            "empty": bool(
                series.isna().all()
            ),
            "constant": bool(
                unique <= 1
            ),
        })

    # --------------------------------------------------
    # Warnings
    # --------------------------------------------------

    warnings = []

    if missing_values:
        warnings.append(
            "Dataset contains missing values."
        )

    if duplicate_rows > 0:
        warnings.append(
            f"Dataset contains {duplicate_rows} duplicate rows."
        )

    if empty_columns:
        warnings.append(
            "Dataset contains completely empty columns."
        )

    if constant_columns:
        warnings.append(
            "Dataset contains columns with only one unique value."
        )

    # --------------------------------------------------
    # Quality score
    # --------------------------------------------------

    score = 100.0

    if rows > 0:

        total_missing = sum(
            item["count"]
            for item in missing_values.values()
        )

        missing_ratio = (
            total_missing / (rows * columns)
            if columns > 0
            else 0
        )

        score -= min(
            missing_ratio * 40,
            40
        )

    if rows > 0:

        duplicate_ratio = (
            duplicate_rows / rows
        )

        score -= min(
            duplicate_ratio * 30,
            30
        )

    if columns > 0:

        empty_ratio = (
            len(empty_columns) / columns
        )

        score -= min(
            empty_ratio * 20,
            20
        )

    score = max(
        0,
        min(
            100,
            round(score, 2)
        )
    )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    if score >= 90:
        status = "excellent"
    elif score >= 75:
        status = "good"
    elif score >= 50:
        status = "needs_attention"
    else:
        status = "poor"

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    recommendations = []

    if missing_values:
        recommendations.append(
            "Review and handle missing values."
        )

    if duplicate_rows > 0:
        recommendations.append(
            "Remove or verify duplicate records."
        )

    if empty_columns:
        recommendations.append(
            "Remove completely empty columns."
        )

    if constant_columns:
        recommendations.append(
            "Review constant columns because they provide limited analytical value."
        )

    if not recommendations:
        recommendations.append(
            "Dataset quality is suitable for business analysis."
        )

    return {
        "quality_score": score,
        "status": status,
        "rows": rows,
        "columns": columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "empty_columns": empty_columns,
        "constant_columns": constant_columns,
        "column_quality": column_quality,
        "warnings": warnings,
        "recommendations": recommendations,
    }