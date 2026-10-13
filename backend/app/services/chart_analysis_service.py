from typing import Any

from app.services.chart_intelligence import (
    detect_dataset_features,
    recommend_charts,
)

from app.services.auto_chart_service import (
    build_automatic_charts,
)


# ============================================================
# CHART ANALYSIS SERVICE
# ============================================================

def build_chart_analysis(
    analysis: dict,
) -> dict:
    """
    Build a complete automatic chart analysis.

    Returns:
        - detected dataset features
        - recommended charts
        - generated chart data
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return {
            "dataset_features": {},
            "recommended_charts": [],
            "charts": [],
        }

    # --------------------------------------------------------
    # Detect dataset characteristics
    # --------------------------------------------------------

    try:

        features = detect_dataset_features(
            analysis
        )

    except Exception:

        features = {}

    # --------------------------------------------------------
    # Recommend visualizations
    # --------------------------------------------------------

    try:

        recommendations = recommend_charts(
            analysis
        )

    except Exception:

        recommendations = []

    # --------------------------------------------------------
    # Generate chart data
    # --------------------------------------------------------

    try:

        charts = build_automatic_charts(
            analysis
        )

    except Exception:

        charts = []

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "dataset_features": features,
        "recommended_charts": recommendations,
        "charts": charts,
    }