from app.business.analytics import (
    dataset_summary,
    preview_dataset,
    numeric_summary
)


def data_agent(
    tool: str,
    arguments: dict
):

    try:

        if tool == "dataset_summary":

            return {
                "answer": dataset_summary(
                    arguments["filepath"]
                ),
                "sources": []
            }

        if tool == "preview_dataset":

            return {
                "answer": preview_dataset(
                    arguments["filepath"],
                    arguments.get("rows", 5)
                ),
                "sources": []
            }

        if tool == "numeric_summary":

            return {
                "answer": numeric_summary(
                    arguments["filepath"]
                ),
                "sources": []
            }

        return {
            "answer": f"Unknown data tool: {tool}",
            "sources": []
        }

    except Exception as e:

        return {
            "answer": f"Data Agent Error: {str(e)}",
            "sources": []
        }