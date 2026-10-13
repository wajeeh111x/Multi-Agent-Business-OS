from typing import Any


# ============================================================
# HELPERS
# ============================================================

def _number(
    value: Any,
):
    """
    Safely convert a value to a number.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return int(value)

    if isinstance(
        value,
        (int, float),
    ):
        return value

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _normalise(
    value: Any,
) -> str:
    """
    Normalize text for comparisons.
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .casefold()
    )


def _contains(
    question: str,
    words,
) -> bool:
    """
    Check whether any keyword exists in the question.
    """

    text = _normalise(
        question
    )

    return any(
        _normalise(word) in text
        for word in words
    )


def _find_item(
    items: list,
    name: str,
):
    """
    Find an item by its name.
    """

    if not isinstance(
        items,
        list,
    ):
        return None

    target = _normalise(
        name
    )

    for item in items:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item_name = _normalise(
            item.get("name")
        )

        if item_name == target:

            return item

    return None


def _extract_named_items(
    question: str,
    items: list,
):
    """
    Find dataset item names mentioned in the question.

    Uses exact names from the dataset.
    """

    if not isinstance(
        items,
        list,
    ):
        return []

    question_normalized = _normalise(
        question
    )

    matches = []

    for item in items:

        if not isinstance(
            item,
            dict,
        ):
            continue

        name = item.get(
            "name"
        )

        if name is None:
            continue

        name_text = _normalise(
            name
        )

        if (
            name_text
            and name_text in question_normalized
        ):

            matches.append(item)

    return matches


# ============================================================
# COMPARISON
# ============================================================

def _compare_items(
    question: str,
    items: list,
    item_type: str,
):
    """
    Compare two explicitly mentioned products/regions.
    """

    matches = _extract_named_items(
        question,
        items,
    )

    if len(matches) < 2:
        return None

    first = matches[0]
    second = matches[1]

    first_total = _number(
        first.get("total")
    )

    second_total = _number(
        second.get("total")
    )

    if (
        first_total is None
        or second_total is None
    ):
        return None

    first_name = first.get(
        "name"
    )

    second_name = second.get(
        "name"
    )

    if first_total > second_total:

        winner = first_name
        winner_total = first_total
        loser = second_name
        loser_total = second_total

    elif second_total > first_total:

        winner = second_name
        winner_total = second_total
        loser = first_name
        loser_total = first_total

    else:

        return {
            "answer": (
                f"{first_name} and {second_name} "
                f"have the same total value of "
                f"{first_total:,.2f}."
            ),
            "chart_type": (
                "products"
                if item_type == "product"
                else "regions"
            ),
            "type": f"{item_type}_comparison",
        }

    difference = (
        winner_total - loser_total
    )

    return {
        "answer": (
            f"{winner} performs better than "
            f"{loser} by "
            f"{difference:,.2f} in total value."
        ),
        "chart_type": (
            "products"
            if item_type == "product"
            else "regions"
        ),
        "type": f"{item_type}_comparison",
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_dashboard_question(
    question: str,
    analysis: dict,
    kpis: dict,
    products: list,
    regions: list,
    trends: list,
):
    """
    Analyze a natural-language business question.

    Uses deterministic business calculations as the
    source of truth.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        analysis = {}

    if not isinstance(
        kpis,
        dict,
    ):
        kpis = {}

    if not isinstance(
        products,
        list,
    ):
        products = []

    if not isinstance(
        regions,
        list,
    ):
        regions = []

    if not isinstance(
        trends,
        list,
    ):
        trends = []

    if not isinstance(
        question,
        str,
    ):
        question = ""

    question = question.strip()

    if not question:

        return {
            "answer": (
                "Please provide a business question."
            ),
            "chart_type": None,
            "type": "validation",
        }

    # ========================================================
    # PRODUCT COMPARISON
    # ========================================================

    if _contains(
        question,
        [
            "compare",
            "versus",
            "vs",
            "better than",
        ],
    ) and _contains(
        question,
        [
            "product",
            "products",
            "item",
        ],
    ):

        result = _compare_items(
            question,
            products,
            "product",
        )

        if result:
            return result

    # ========================================================
    # REGION COMPARISON
    # ========================================================

    if _contains(
        question,
        [
            "compare",
            "versus",
            "vs",
            "better than",
        ],
    ) and _contains(
        question,
        [
            "region",
            "regions",
            "country",
            "countries",
        ],
    ):

        result = _compare_items(
            question,
            regions,
            "region",
        )

        if result:
            return result

    # ========================================================
    # SPECIFIC PRODUCT
    # ========================================================

    product_matches = _extract_named_items(
        question,
        products,
    )

    if product_matches:

        selected = product_matches[0]

        name = selected.get(
            "name"
        )

        total = _number(
            selected.get("total")
        )

        average = _number(
            selected.get("average")
        )

        count = _number(
            selected.get("count")
        )

        if (
            total is not None
            and average is not None
        ):

            answer = (
                f"{name} generated "
                f"{total:,.2f} in total revenue "
                f"with an average of "
                f"{average:,.2f} per record."
            )

            if count is not None:

                answer += (
                    f" It appears in "
                    f"{int(count)} records."
                )

            return {
                "answer": answer,
                "chart_type": "products",
                "type": "product_analysis",
            }

    # ========================================================
    # TOP PRODUCT
    # ========================================================

    if _contains(
        question,
        [
            "top product",
            "best product",
            "highest product",
            "best-selling product",
            "best selling product",
            "which product",
        ],
    ):

        if products:

            top = products[0]

            name = top.get(
                "name"
            )

            total = _number(
                top.get("total")
            )

            if (
                name is not None
                and total is not None
            ):

                return {
                    "answer": (
                        f"{name} is the top-performing "
                        f"product with total revenue "
                        f"of {total:,.2f}."
                    ),
                    "chart_type": "products",
                    "type": "product_analysis",
                }

    # ========================================================
    # PRODUCT AVERAGE
    # ========================================================

    if _contains(
        question,
        [
            "highest average",
            "best average",
            "average product",
        ],
    ):

        valid = []

        for item in products:

            if not isinstance(
                item,
                dict,
            ):
                continue

            average = _number(
                item.get("average")
            )

            if average is not None:

                valid.append(
                    (
                        item.get("name"),
                        average,
                    )
                )

        if valid:

            name, average = max(
                valid,
                key=lambda x: x[1],
            )

            return {
                "answer": (
                    f"{name} has the highest "
                    f"average revenue per record "
                    f"at {average:,.2f}."
                ),
                "chart_type": "products",
                "type": "product_average_analysis",
            }

    # ========================================================
    # REGION QUESTIONS
    # ========================================================

    region_matches = _extract_named_items(
        question,
        regions,
    )

    if region_matches:

        selected = region_matches[0]

        name = selected.get(
            "name"
        )

        total = _number(
            selected.get("total")
        )

        average = _number(
            selected.get("average")
        )

        count = _number(
            selected.get("count")
        )

        if total is not None:

            answer = (
                f"{name} generated "
                f"{total:,.2f} in total revenue."
            )

            if average is not None:

                answer += (
                    f" Average revenue per "
                    f"record is "
                    f"{average:,.2f}."
                )

            if count is not None:

                answer += (
                    f" It contains "
                    f"{int(count)} records."
                )

            return {
                "answer": answer,
                "chart_type": "regions",
                "type": "regional_analysis",
            }

    # ========================================================
    # TOP REGION
    # ========================================================

    if _contains(
        question,
        [
            "top region",
            "best region",
            "highest region",
            "which region",
            "highest sales region",
        ],
    ):

        if regions:

            top_region = regions[0]

            name = top_region.get(
                "name"
            )

            total = _number(
                top_region.get("total")
            )

            if (
                name is not None
                and total is not None
            ):

                return {
                    "answer": (
                        f"{name} is the top-performing "
                        f"region with total revenue "
                        f"of {total:,.2f}."
                    ),
                    "chart_type": "regions",
                    "type": "regional_analysis",
                }

    # ========================================================
    # REVENUE
    # ========================================================

    if _contains(
        question,
        [
            "revenue",
            "sales",
            "income",
        ],
    ):

        revenue = kpis.get(
            "revenue"
        )

        if isinstance(
            revenue,
            dict,
        ):

            total = _number(
                revenue.get("total")
            )

            average = _number(
                revenue.get("average")
            )

            if total is not None:

                answer = (
                    f"Total revenue is "
                    f"{total:,.2f}."
                )

                if average is not None:

                    answer += (
                        f" Average revenue per "
                        f"record is "
                        f"{average:,.2f}."
                    )

                return {
                    "answer": answer,
                    "chart_type": "trends",
                    "type": "revenue_analysis",
                }

    # ========================================================
    # PROFIT MARGIN
    # ========================================================

    if _contains(
        question,
        [
            "profit margin",
            "margin",
        ],
    ):

        margin = _number(
            kpis.get(
                "profit_margin_percent"
            )
        )

        if margin is not None:

            return {
                "answer": (
                    f"The profit margin is "
                    f"{margin:.2f}%."
                ),
                "chart_type": None,
                "type": "profit_margin_analysis",
            }

    # ========================================================
    # PROFIT
    # ========================================================

    if _contains(
        question,
        [
            "profit",
            "earnings",
        ],
    ):

        profit = kpis.get(
            "profit"
        )

        if isinstance(
            profit,
            dict,
        ):

            total = _number(
                profit.get("total")
            )

            average = _number(
                profit.get("average")
            )

            if total is not None:

                answer = (
                    f"Total profit is "
                    f"{total:,.2f}."
                )

                if average is not None:

                    answer += (
                        f" Average profit per "
                        f"record is "
                        f"{average:,.2f}."
                    )

                return {
                    "answer": answer,
                    "chart_type": None,
                    "type": "profit_analysis",
                }

    # ========================================================
    # COST
    # ========================================================

    if _contains(
        question,
        [
            "cost",
            "costs",
            "expense",
            "expenses",
        ],
    ):

        cost = kpis.get(
            "cost"
        )

        if isinstance(
            cost,
            dict,
        ):

            total = _number(
                cost.get("total")
            )

            average = _number(
                cost.get("average")
            )

            if total is not None:

                answer = (
                    f"Total cost is "
                    f"{total:,.2f}."
                )

                if average is not None:

                    answer += (
                        f" Average cost per "
                        f"record is "
                        f"{average:,.2f}."
                    )

                return {
                    "answer": answer,
                    "chart_type": None,
                    "type": "cost_analysis",
                }

    # ========================================================
    # QUANTITY
    # ========================================================

    if _contains(
        question,
        [
            "quantity",
            "units",
            "volume sold",
        ],
    ):

        quantity = kpis.get(
            "quantity"
        )

        if isinstance(
            quantity,
            dict,
        ):

            total = _number(
                quantity.get("total")
            )

            average = _number(
                quantity.get("average")
            )

            if total is not None:

                answer = (
                    f"Total quantity is "
                    f"{total:,.0f}."
                )

                if average is not None:

                    answer += (
                        f" Average quantity per "
                        f"record is "
                        f"{average:,.2f}."
                    )

                return {
                    "answer": answer,
                    "chart_type": None,
                    "type": "quantity_analysis",
                }

    # ========================================================
    # BEST / WORST PERIOD
    # ========================================================

    if _contains(
        question,
        [
            "best period",
            "highest period",
            "best month",
            "highest month",
        ],
    ):

        best = kpis.get(
            "best_period"
        )

        if isinstance(
            best,
            dict,
        ):

            period = best.get(
                "period"
            )

            total = _number(
                best.get("total")
            )

            if (
                period is not None
                and total is not None
            ):

                return {
                    "answer": (
                        f"The best available period "
                        f"was {period} with revenue "
                        f"of {total:,.2f}."
                    ),
                    "chart_type": "trends",
                    "type": "best_period_analysis",
                }

    if _contains(
        question,
        [
            "worst period",
            "lowest period",
            "worst month",
            "lowest month",
        ],
    ):

        worst = kpis.get(
            "worst_period"
        )

        if isinstance(
            worst,
            dict,
        ):

            period = worst.get(
                "period"
            )

            total = _number(
                worst.get("total")
            )

            if (
                period is not None
                and total is not None
            ):

                return {
                    "answer": (
                        f"The weakest available period "
                        f"was {period} with revenue "
                        f"of {total:,.2f}."
                    ),
                    "chart_type": "trends",
                    "type": "worst_period_analysis",
                }

    # ========================================================
    # GROWTH / CHANGE
    # ========================================================

    if _contains(
        question,
        [
            "growth",
            "change",
            "increased",
            "decreased",
            "decline",
        ],
    ):

        change = _number(
            kpis.get(
                "period_change_percent"
            )
        )

        if change is not None:

            if change > 0:

                direction = "increased"

            elif change < 0:

                direction = "decreased"

            else:

                direction = "remained unchanged"

            return {
                "answer": (
                    f"Revenue {direction} by "
                    f"{abs(change):.2f}% from "
                    f"the first available period "
                    f"to the latest available period."
                ),
                "chart_type": "trends",
                "type": "growth_analysis",
            }

    # ========================================================
    # TREND
    # ========================================================

    if _contains(
        question,
        [
            "trend",
            "trends",
            "over time",
            "timeline",
            "monthly",
        ],
    ):

        if trends:

            return {
                "answer": (
                    "The available revenue trend is "
                    "shown across the recorded periods."
                ),
                "chart_type": "trends",
                "type": "trend_analysis",
            }

    # ========================================================
    # TOP CUSTOMER
    # ========================================================

    if _contains(
        question,
        [
            "customer",
            "customers",
            "client",
        ],
    ):

        top_customer = kpis.get(
            "top_customer"
        )

        if isinstance(
            top_customer,
            dict,
        ):

            name = top_customer.get(
                "name"
            )

            total = _number(
                top_customer.get("total")
            )

            if name:

                answer = (
                    f"{name} is the highest-value "
                    "customer"
                )

                if total is not None:

                    answer += (
                        f" with total value of "
                        f"{total:,.2f}."
                    )

                return {
                    "answer": answer,
                    "chart_type": None,
                    "type": "customer_analysis",
                }

        return {
            "answer": (
                "Customer-level data is not available "
                "for this dataset."
            ),
            "chart_type": None,
            "type": "customer_analysis",
        }

    # ========================================================
    # GENERAL
    # ========================================================

    rows = analysis.get(
        "rows",
        0,
    )

    columns = analysis.get(
        "columns",
        0,
    )

    return {
        "answer": (
            f"The dataset contains {rows} rows "
            f"and {columns} columns. "
            "Ask about revenue, profit, products, "
            "regions, costs, quantity, customers, "
            "periods, growth, or trends."
        ),
        "chart_type": None,
        "type": "general_analysis",
    }