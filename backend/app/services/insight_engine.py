import json

from app.ai.ollama_client import ask_llm


# ============================================================
# CONFIGURATION
# ============================================================

MAX_ANALYSIS_CHARS = 8000

MAX_INSIGHTS = 5
MAX_RECOMMENDATIONS = 4

MAX_PRODUCTS = 10
MAX_CUSTOMERS = 5
MAX_REGIONS = 10
MAX_TRENDS = 12


# ============================================================
# COMPACT ANALYSIS
# ============================================================

def _compact_analysis(analysis: dict) -> dict:
    """
    Prepare a small, business-focused payload for Ollama.
    """

    if not isinstance(analysis, dict):
        return {}

    compact = {
        "rows": analysis.get("rows", 0),
        "columns": analysis.get("columns", 0),

        "detected_business_columns": analysis.get(
            "detected_business_columns",
            {},
        ),

        "business_metrics": analysis.get(
            "business_metrics",
            {},
        ),

        "products": analysis.get(
            "products",
            [],
        )[:MAX_PRODUCTS],

        "customers": analysis.get(
            "customers",
            [],
        )[:MAX_CUSTOMERS],

        "regions": analysis.get(
            "regions",
            [],
        )[:MAX_REGIONS],

        "trends": analysis.get(
            "trends",
            [],
        )[-MAX_TRENDS:],

        "missing_values": analysis.get(
            "missing_values",
            {},
        ),

        "numeric_statistics": analysis.get(
            "numeric_statistics",
            {},
        ),
    }

    # --------------------------------------------------------
    # Keep only useful numeric statistics
    # --------------------------------------------------------

    numeric_statistics = compact.get(
        "numeric_statistics",
        {},
    )

    if isinstance(numeric_statistics, dict):

        cleaned_statistics = {}

        for column, stats in numeric_statistics.items():

            if not isinstance(stats, dict):
                continue

            cleaned_statistics[str(column)] = {
                "count": stats.get("count"),
                "mean": stats.get("mean"),
                "median": stats.get("median"),
                "min": stats.get("min"),
                "max": stats.get("max"),
                "sum": stats.get("sum"),
            }

        compact["numeric_statistics"] = (
            cleaned_statistics
        )

    # --------------------------------------------------------
    # Serialize
    # --------------------------------------------------------

    try:

        text = json.dumps(
            compact,
            separators=(",", ":"),
            default=str,
        )

    except Exception:

        return {
            "rows": analysis.get("rows", 0),
            "columns": analysis.get("columns", 0),
            "business_metrics": analysis.get(
                "business_metrics",
                {},
            ),
            "detected_business_columns": analysis.get(
                "detected_business_columns",
                {},
            ),
        }

    # --------------------------------------------------------
    # Reduce progressively if too large
    # --------------------------------------------------------

    if len(text) > MAX_ANALYSIS_CHARS:

        compact.pop("customers", None)

        text = json.dumps(
            compact,
            separators=(",", ":"),
            default=str,
        )

    if len(text) > MAX_ANALYSIS_CHARS:

        compact.pop("missing_values", None)

        text = json.dumps(
            compact,
            separators=(",", ":"),
            default=str,
        )

    if len(text) > MAX_ANALYSIS_CHARS:

        compact.pop("numeric_statistics", None)

        text = json.dumps(
            compact,
            separators=(",", ":"),
            default=str,
        )

    if len(text) > MAX_ANALYSIS_CHARS:

        compact["products"] = compact.get(
            "products",
            [],
        )[:5]

        compact["regions"] = compact.get(
            "regions",
            [],
        )[:5]

        compact["trends"] = compact.get(
            "trends",
            [],
        )[-6:]

    return compact


# ============================================================
# CLEAN RESPONSE
# ============================================================

def _clean_response(response) -> str:
    """
    Remove common markdown/code-fence formatting.
    """

    if response is None:
        return ""

    response = str(response).strip()

    if not response:
        return ""

    if response.startswith("```json"):
        response = response[len("```json"):].strip()

    elif response.startswith("```JSON"):
        response = response[len("```JSON"):].strip()

    elif response.startswith("```"):
        response = response[len("```"):].strip()

    if response.endswith("```"):
        response = response[:-len("```")].strip()

    return response


# ============================================================
# DECODE NESTED JSON
# ============================================================

def _decode_nested_json(
    value,
    depth: int = 0,
):
    """
    Recursively decode JSON strings.
    """

    if depth > 5:
        return value

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return value

        cleaned = _clean_response(value)

        try:

            decoded = json.loads(cleaned)

        except (
            json.JSONDecodeError,
            TypeError,
        ):

            return cleaned

        return _decode_nested_json(
            decoded,
            depth + 1,
        )

    if isinstance(value, dict):

        result = {}

        for key, item in value.items():

            result[key] = _decode_nested_json(
                item,
                depth + 1,
            )

        return result

    if isinstance(value, list):

        return [
            _decode_nested_json(
                item,
                depth + 1,
            )
            for item in value
        ]

    return value


# ============================================================
# EXTRACT JSON
# ============================================================

def _extract_json(response):
    """
    Extract a JSON object from an Ollama response.
    """

    if response is None:
        return None

    response = _clean_response(response)

    if not response:
        return None

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        result = json.loads(response)

        result = _decode_nested_json(result)

        if isinstance(result, dict):
            return result

    except (
        json.JSONDecodeError,
        TypeError,
    ):

        pass

    # --------------------------------------------------------
    # JSON embedded inside text
    # --------------------------------------------------------

    decoder = json.JSONDecoder()

    for index, character in enumerate(response):

        if character != "{":
            continue

        candidate = response[index:]

        try:

            result, _ = decoder.raw_decode(candidate)

            result = _decode_nested_json(result)

            if isinstance(result, dict):
                return result

        except (
            json.JSONDecodeError,
            TypeError,
        ):

            continue

    return None


# ============================================================
# VALIDATE LIST
# ============================================================

def _validate_list(value):
    """
    Keep only dictionary objects from an LLM list.
    """

    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


# ============================================================
# LOCAL FALLBACK / PRIMARY BI INSIGHTS
# ============================================================

def _build_fallback_insights(
    analysis: dict,
):
    """
    Generate deterministic business insights locally.

    These calculations do not depend on Ollama.
    """

    insights = []
    recommendations = []

    rows = analysis.get("rows", 0)
    columns = analysis.get("columns", 0)

    business_metrics = analysis.get(
        "business_metrics",
        {},
    )

    products = analysis.get(
        "products",
        [],
    )

    customers = analysis.get(
        "customers",
        [],
    )

    regions = analysis.get(
        "regions",
        [],
    )

    trends = analysis.get(
        "trends",
        [],
    )

    missing_values = analysis.get(
        "missing_values",
        {},
    )

    # --------------------------------------------------------
    # Dataset overview
    # --------------------------------------------------------

    if rows:

        insights.append(
            {
                "title": "Dataset Overview",
                "description": (
                    f"The dataset contains {rows} "
                    f"records across {columns} columns."
                ),
                "importance": "medium",
            }
        )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue = business_metrics.get("revenue")

    if isinstance(revenue, dict):

        total = revenue.get("total")
        average = revenue.get("average")

        if total is not None:

            description = (
                f"Total revenue is approximately "
                f"{total:,.2f}"
            )

            if average is not None:

                description += (
                    f", with an average of "
                    f"{average:,.2f} per record."
                )

            insights.append(
                {
                    "title": "Revenue Performance",
                    "description": description,
                    "importance": "high",
                }
            )

            recommendations.append(
                {
                    "title": "Monitor Revenue Trends",
                    "description": (
                        "Track revenue regularly to identify "
                        "growth and decline periods."
                    ),
                    "priority": "high",
                }
            )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    profit = business_metrics.get("profit")

    if isinstance(profit, dict):

        total = profit.get("total")
        average = profit.get("average")

        if total is not None:

            description = (
                f"Total profit is approximately "
                f"{total:,.2f}"
            )

            if average is not None:

                description += (
                    f", averaging "
                    f"{average:,.2f} per record."
                )

            insights.append(
                {
                    "title": "Profit Performance",
                    "description": description,
                    "importance": "high",
                }
            )

    # --------------------------------------------------------
    # Top product
    # --------------------------------------------------------

    if products:

        top_product = products[0]

        if isinstance(top_product, dict):

            name = top_product.get("name")
            total = top_product.get("total")

            if name:

                description = (
                    f"{name} is the leading product"
                )

                if total is not None:

                    description += (
                        f", with approximately "
                        f"{total:,.2f} in total value."
                    )

                insights.append(
                    {
                        "title": "Top Product",
                        "description": description,
                        "importance": "high",
                    }
                )

                recommendations.append(
                    {
                        "title": "Review Top Product",
                        "description": (
                            f"Analyze why {name} performs "
                            "strongly and maintain its "
                            "availability where appropriate."
                        ),
                        "priority": "medium",
                    }
                )

    # --------------------------------------------------------
    # Top customer
    # --------------------------------------------------------

    if customers:

        top_customer = customers[0]

        if isinstance(top_customer, dict):

            name = top_customer.get("name")

            if name:

                insights.append(
                    {
                        "title": "Top Customer",
                        "description": (
                            f"{name} is the highest-value "
                            "customer in the available "
                            "customer breakdown."
                        ),
                        "importance": "medium",
                    }
                )

    # --------------------------------------------------------
    # Top region
    # --------------------------------------------------------

    if regions:

        top_region = regions[0]

        if isinstance(top_region, dict):

            name = top_region.get("name")
            total = top_region.get("total")

            if name:

                description = (
                    f"{name} is the highest-value "
                    "region in the available data."
                )

                if total is not None:

                    description += (
                        f" Its total is approximately "
                        f"{total:,.2f}."
                    )

                insights.append(
                    {
                        "title": "Regional Performance",
                        "description": description,
                        "importance": "medium",
                    }
                )

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    if len(trends) >= 2:

        first = trends[0]
        latest = trends[-1]

        first_total = first.get("total")
        latest_total = latest.get("total")

        if (
            isinstance(first_total, (int, float))
            and isinstance(latest_total, (int, float))
        ):

            if latest_total > first_total:

                trend_text = (
                    "The latest available period "
                    "has a higher total than the earliest "
                    "available period."
                )

            elif latest_total < first_total:

                trend_text = (
                    "The latest available period "
                    "has a lower total than the earliest "
                    "available period."
                )

            else:

                trend_text = (
                    "The earliest and latest available "
                    "periods have the same total."
                )

            insights.append(
                {
                    "title": "Time Trend",
                    "description": trend_text,
                    "importance": "medium",
                }
            )

            recommendations.append(
                {
                    "title": "Monitor Periodic Trends",
                    "description": (
                        "Compare performance across periods "
                        "to identify growth and decline."
                    ),
                    "priority": "medium",
                }
            )

    # --------------------------------------------------------
    # Missing data
    # --------------------------------------------------------

    if missing_values:

        missing_count = len(missing_values)

        insights.append(
            {
                "title": "Missing Data",
                "description": (
                    f"{missing_count} column(s) contain "
                    "missing values that may affect "
                    "analysis quality."
                ),
                "importance": "high",
            }
        )

        recommendations.append(
            {
                "title": "Review Missing Values",
                "description": (
                    "Investigate incomplete fields and "
                    "decide how missing values should "
                    "be handled."
                ),
                "priority": "high",
            }
        )

    # --------------------------------------------------------
    # Guarantee insight
    # --------------------------------------------------------

    if not insights:

        insights.append(
            {
                "title": "Dataset Structure",
                "description": (
                    f"The dataset contains {rows} records "
                    f"and {columns} columns available "
                    "for analysis."
                ),
                "importance": "medium",
            }
        )

    # --------------------------------------------------------
    # Guarantee recommendation
    # --------------------------------------------------------

    if not recommendations:

        recommendations.append(
            {
                "title": "Establish KPI Monitoring",
                "description": (
                    "Use the available business metrics "
                    "to establish consistent KPI tracking."
                ),
                "priority": "medium",
            }
        )

    return (
        insights[:MAX_INSIGHTS],
        recommendations[:MAX_RECOMMENDATIONS],
    )


# ============================================================
# OPTIONAL AI ENHANCEMENT
# ============================================================

def _generate_ai_insights(
    analysis: dict,
):
    """
    Try to generate an AI interpretation.

    This is optional and must never block the deterministic
    BI response.
    """

    compact_analysis = _compact_analysis(
        analysis
    )

    try:

        analysis_json = json.dumps(
            compact_analysis,
            separators=(",", ":"),
            default=str,
        )

    except Exception:

        return None, "Unable to serialize analysis."

    prompt = f"""
You are a Business Intelligence analyst.

Analyze ONLY the following business data:

{analysis_json}

Return a concise JSON object containing:
- one factual summary
- up to 5 insights
- up to 4 recommendations

Rules:
- Never invent numbers.
- Use only the provided data.
- Do not compare unrelated numeric fields.
- Keep all descriptions short.

Return ONLY JSON.
"""

    try:

        response = ask_llm(prompt)

    except Exception as e:

        return None, str(e)

    result = _extract_json(response)

    if not isinstance(result, dict):

        return None, "Invalid AI JSON response."

    return result, None


# ============================================================
# GENERATE BUSINESS INSIGHTS
# ============================================================

def generate_business_insights(
    analysis: dict,
):
    """
    Generate business insights.

    Deterministic Python analysis is the primary source of
    truth. AI enhancement is optional.
    """

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not isinstance(analysis, dict):

        return {
            "summary": (
                "No valid dataset analysis was provided."
            ),
            "insights": [],
            "recommendations": [],
            "warning": "Invalid analysis data.",
        }

    if not analysis:

        return {
            "summary": "The dataset analysis is empty.",
            "insights": [],
            "recommendations": [],
            "warning": "No analysis data was available.",
        }

    # --------------------------------------------------------
    # PRIMARY PATH: deterministic BI
    # --------------------------------------------------------

    insights, recommendations = (
        _build_fallback_insights(
            analysis
        )
    )

    summary = (
        f"The dataset contains "
        f"{analysis.get('rows', 0)} rows "
        f"and "
        f"{analysis.get('columns', 0)} columns. "
        "Business metrics and dataset structure "
        "were analyzed."
    )

    # --------------------------------------------------------
    # Return deterministic result immediately
    #
    # This prevents Ollama from blocking /insights.
    # --------------------------------------------------------

    return {
        "summary": summary,
        "insights": insights,
        "recommendations": recommendations,
    }