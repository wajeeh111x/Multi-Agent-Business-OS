import requests

from app.config import settings


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = settings.OLLAMA_MODEL

OLLAMA_TIMEOUT = settings.OLLAMA_TIMEOUT


# ============================================================
# ASK LLM
# ============================================================

def ask_llm(prompt: str) -> str:
    """
    Send a prompt to Ollama and return the model response.

    Raises RuntimeError when Ollama fails.
    """

    # --------------------------------------------------------
    # Validate prompt
    # --------------------------------------------------------

    if not isinstance(prompt, str):
        raise ValueError(
            "Prompt must be a string."
        )

    if not prompt.strip():
        raise ValueError(
            "No prompt provided."
        )

    # --------------------------------------------------------
    # JSON schema for Business OS insights
    # --------------------------------------------------------

    response_schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string"
            },
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "importance": {
                            "type": "string",
                            "enum": [
                                "high",
                                "medium",
                                "low"
                            ]
                        }
                    },
                    "required": [
                        "title",
                        "description",
                        "importance"
                    ]
                }
            },
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "priority": {
                            "type": "string",
                            "enum": [
                                "high",
                                "medium",
                                "low"
                            ]
                        }
                    },
                    "required": [
                        "title",
                        "description",
                        "priority"
                    ]
                }
            }
        },
        "required": [
            "summary",
            "insights",
            "recommendations"
        ]
    }

    # --------------------------------------------------------
    # Ollama payload
    # --------------------------------------------------------

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,

        # Qwen3 thinking disabled for faster responses
        "think": False,

        # Structured JSON output
        "format": response_schema,

        "options": {
            "temperature": 0.1,
            "num_predict": 400,
        }
    }

    # --------------------------------------------------------
    # Send request
    # --------------------------------------------------------

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout as e:

        print(
            f"[OLLAMA] Timeout after "
            f"{OLLAMA_TIMEOUT} seconds."
        )

        raise RuntimeError(
            f"Ollama request timed out after "
            f"{OLLAMA_TIMEOUT} seconds."
        ) from e

    except requests.exceptions.ConnectionError as e:

        print(
            "[OLLAMA] Connection failed."
        )

        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from e

    except requests.exceptions.HTTPError as e:

        status_code = response.status_code

        print(
            f"[OLLAMA] HTTP error "
            f"{status_code}: {e}"
        )

        raise RuntimeError(
            f"Ollama returned HTTP "
            f"{status_code}: {e}"
        ) from e

    except requests.exceptions.RequestException as e:

        print(
            f"[OLLAMA] Request error: {e}"
        )

        raise RuntimeError(
            f"Ollama request failed: {e}"
        ) from e

    # --------------------------------------------------------
    # Parse response
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError as e:

        raise RuntimeError(
            "Ollama returned invalid JSON."
        ) from e

    # --------------------------------------------------------
    # Check Ollama error
    # --------------------------------------------------------

    if isinstance(data, dict):

        ollama_error = data.get(
            "error"
        )

        if ollama_error:

            raise RuntimeError(
                f"Ollama error: {ollama_error}"
            )

    # --------------------------------------------------------
    # Get model response
    # --------------------------------------------------------

    answer = data.get(
        "response",
        ""
    )

    if answer is None:
        answer = ""

    if not isinstance(answer, str):
        answer = str(answer)

    answer = answer.strip()

    # --------------------------------------------------------
    # Empty response
    # --------------------------------------------------------

    if not answer:

        raise RuntimeError(
            "Ollama returned an empty response."
        )

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print(
        f"[OLLAMA] Model: {OLLAMA_MODEL}"
    )

    print(
        f"[OLLAMA] Timeout: {OLLAMA_TIMEOUT}s"
    )

    print(
        f"[OLLAMA] Response length: "
        f"{len(answer)} characters"
    )

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return answer