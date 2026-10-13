import os

from app.services.dataset_query import (
    answer_business_question,
    dataset_summary,
)


BUSINESS_UPLOAD_DIR = "uploads/business"


# ============================================================
# FIND DATASET
# ============================================================

def find_dataset(dataset_id: str):
    """
    Find a stored business dataset by ID.
    """

    if not dataset_id:
        return None

    if not os.path.isdir(BUSINESS_UPLOAD_DIR):
        return None

    prefix = f"{dataset_id}_"

    try:
        for filename in os.listdir(BUSINESS_UPLOAD_DIR):

            if not filename.startswith(prefix):
                continue

            filepath = os.path.join(
                BUSINESS_UPLOAD_DIR,
                filename
            )

            if os.path.isfile(filepath):
                return filepath

    except OSError:
        return None

    return None


# ============================================================
# DATASET AGENT
# ============================================================

def dataset_agent(
    dataset_id: str,
    question: str
):
    """
    Answer a business question using
    an uploaded business dataset.
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        return {
            "answer": "Dataset ID is required.",
            "sources": []
        }

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question or not question.strip():

        return {
            "answer": "Question is required.",
            "sources": []
        }

    dataset_id = dataset_id.strip()
    question = question.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    filepath = find_dataset(dataset_id)

    if not filepath:

        return {
            "answer": "Dataset not found.",
            "sources": []
        }

    filename = os.path.basename(filepath)

    # --------------------------------------------------------
    # Answer business question
    # --------------------------------------------------------

    try:

        result = answer_business_question(
            filepath=filepath,
            question=question
        )

    except FileNotFoundError as e:

        return {
            "answer": str(e),
            "sources": [
                {
                    "type": "dataset",
                    "dataset_id": dataset_id,
                    "filename": filename
                }
            ]
        }

    except ValueError as e:

        return {
            "answer": str(e),
            "sources": [
                {
                    "type": "dataset",
                    "dataset_id": dataset_id,
                    "filename": filename
                }
            ]
        }

    except Exception as e:

        print(
            f"Dataset Agent Error: {type(e).__name__}: {e}"
        )

        return {
            "answer": (
                "Dataset analysis failed. "
                f"{str(e)}"
            ),
            "sources": [
                {
                    "type": "dataset",
                    "dataset_id": dataset_id,
                    "filename": filename
                }
            ]
        }

    # --------------------------------------------------------
    # Make sure result is a dictionary
    # --------------------------------------------------------

    if not isinstance(result, dict):

        return {
            "answer": str(result),
            "sources": [
                {
                    "type": "dataset",
                    "dataset_id": dataset_id,
                    "filename": filename
                }
            ]
        }

    # --------------------------------------------------------
    # Extract answer
    # --------------------------------------------------------

    answer = result.get(
        "answer",
        "No answer generated."
    )

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    response = {
        "answer": str(answer),
        "result": result.get("result"),
        "sources": [
            {
                "type": "dataset",
                "dataset_id": dataset_id,
                "filename": filename
            }
        ]
    }

    # --------------------------------------------------------
    # Preserve optional analysis information
    # --------------------------------------------------------

    if "columns" in result:
        response["columns"] = result["columns"]

    if "rows" in result:
        response["rows"] = result["rows"]

    if "calculation" in result:
        response["calculation"] = result["calculation"]

    return response