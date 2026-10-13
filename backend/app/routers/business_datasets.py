import os
import uuid

import pandas as pd

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.dataset import Dataset

from app.services.dataset_version_service import (
    register_original_version,
    register_cleaned_version,
    activate_version,
    load_versions,
    get_active_version,
    get_active_dataset_file,
)

from app.services.dataset_version_service import (
    register_original_version,
    register_cleaned_version,
    activate_version,
    load_versions,
    get_active_version,
)

from app.services.dataset_cleaner import (
    clean_dataframe,
)

from app.services.dataset_quality import (
    analyze_data_quality,
)

from app.services.bi_conversation_service import (
    process_bi_conversation,
)

from app.services.bi_question_service import (
    analyze_bi_question,
)


from app.services.chart_query_service import (
    generate_chart_from_question,
)


from app.services.chart_analysis_service import (
    build_chart_analysis,
)
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Query,
)

from app.services.dataset_analyzer import (
    analyze_dataset,
    analyze_dataframe,
)

from app.services.dashboard_filter import (
    filter_dataframe,
)

from app.agents.dataset_agent import (
    dataset_agent,
)

from app.services.bi_analytics import (
    generate_bi_analysis,
)

from app.services.insight_engine import (
    generate_business_insights,
)

from app.services.kpi_service import (
    build_kpis,
    get_products,
    get_regions,
    get_trends,
)

from app.services.dashboard_service import (
    build_dashboard,
)

from app.services.agent_analysis import (
    analyze_dashboard_question,
)

from app.services.chart_service import (
    build_charts,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/business",
    tags=["Business Intelligence"],
)


# ============================================================
# CONFIGURATION
# ============================================================

BUSINESS_UPLOAD_DIR = "uploads/business"

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}

MAX_FILE_SIZE = 50 * 1024 * 1024


# ============================================================
# CREATE UPLOAD DIRECTORY
# ============================================================

os.makedirs(
    BUSINESS_UPLOAD_DIR,
    exist_ok=True,
)


# ============================================================
# FIND DATASET
# ============================================================

def find_dataset_file(
    dataset_id: str,
):
    """
    Find an uploaded business dataset.

    Returns:
        (filename, filepath) if found.
        None otherwise.
    """

    if not dataset_id:
        return None

    dataset_id = dataset_id.strip()

    if not dataset_id:
        return None

    if not os.path.isdir(
        BUSINESS_UPLOAD_DIR
    ):
        return None

    prefix = f"{dataset_id}_"

    try:

        for filename in os.listdir(
            BUSINESS_UPLOAD_DIR
        ):

            if not filename.startswith(
                prefix
            ):
                continue

            filepath = os.path.join(
                BUSINESS_UPLOAD_DIR,
                filename,
            )

            if os.path.isfile(
                filepath
            ):

                return (
                    filename,
                    filepath,
                )

    except OSError:

        return None

    return None

# ============================================================
# FIND ACTIVE DATASET
# ============================================================

def find_active_dataset_file(
    dataset_id: str,
):
    """
    Find the currently active dataset version.

    Returns:
        (filename, filepath, version)

    Falls back to the original uploaded dataset
    when version metadata is unavailable.
    """

    if not dataset_id:
        return None

    dataset_id = dataset_id.strip()

    if not dataset_id:
        return None

    try:

        active_dataset = (
            get_active_dataset_file(
                dataset_id
            )
        )

        if active_dataset is not None:

            return active_dataset

    except Exception:
        pass

    original_dataset = find_dataset_file(
        dataset_id
    )

    if original_dataset is None:
        return None

    filename, filepath, version = (
        original_dataset
    )

    return (
        filename,
        filepath,
        version,
        "original",
    )

# ============================================================
# UPLOAD BUSINESS DATASET
# ============================================================

@router.post(
    "/datasets/upload"
)
def upload_business_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a CSV or Excel business dataset.
    """

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    original_filename = os.path.basename(
        file.filename
    )

    if not original_filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only CSV and Excel files are allowed."
            ),
        )

    dataset_id = str(
        uuid.uuid4()
    )

    stored_filename = (
        f"{dataset_id}_{original_filename}"
    )

    filepath = os.path.join(
        BUSINESS_UPLOAD_DIR,
        stored_filename,
    )

    total_size = 0

    try:

        with open(
            filepath,
            "wb",
        ) as buffer:

            while True:

                chunk = file.file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "Dataset is too large. "
                            "Maximum size is 50 MB."
                        ),
                    )

                buffer.write(chunk)

    except HTTPException:

        if os.path.exists(
            filepath
        ):
            os.remove(filepath)

        raise

    except Exception as e:

        if os.path.exists(
            filepath
        ):
            os.remove(filepath)

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset upload failed: {str(e)}"
            ),
        )

    finally:

        try:
            file.file.close()
        except Exception:
            pass

        dataset = Dataset(
        id=dataset_id,
        user_id=current_user.id,
        filename=original_filename,
        filepath=filepath,
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    register_original_version(
    dataset_id=dataset_id,
    filename=original_filename,
    filepath=filepath,
  ) 
    return {
        "message": (
            "Business dataset uploaded successfully."
        ),
        "dataset_id": dataset_id,
        "filename": original_filename,
        "stored_filename": stored_filename,
        "filepath": filepath,
        "size_bytes": total_size,
        "extension": extension,
    }


# ============================================================
# ANALYZE DATASET
# ============================================================

@router.get(
    "/datasets/{dataset_id}/analyze"
)
def analyze_business_dataset(
    dataset_id: str,
):
    """
    Analyze an uploaded dataset.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_active_dataset_file(
    dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath, version = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "analysis": analysis,
    }


# ============================================================
# BUSINESS INTELLIGENCE
# ============================================================

@router.get(
    "/datasets/{dataset_id}/bi"
)
def business_intelligence(
    dataset_id: str,
):
    """
    Generate BI analysis.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_active_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        analysis = generate_bi_analysis(
            filepath
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"BI analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "analysis": analysis,
    }


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

@router.get(
    "/datasets/{dataset_id}/insights"
)
def business_insights(
    dataset_id: str,
):
    """
    Generate deterministic business insights.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_active_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath, version = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset analysis failed: {str(e)}"
            ),
        )

    try:

        insights = generate_business_insights(
            analysis
        )

    except Exception as e:

        insights = {
            "summary": (
                f"The dataset contains "
                f"{analysis.get('rows', 0)} rows "
                f"and "
                f"{analysis.get('columns', 0)} columns."
            ),
            "insights": [],
            "recommendations": [],
            "warning": (
                f"Insight generation failed: {str(e)}"
            ),
        }

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "insights": insights,
    }


# ============================================================
# KPI DASHBOARD
# ============================================================

@router.get(
    "/datasets/{dataset_id}/kpis"
)
def dataset_kpis(
    dataset_id: str,
):
    """
    Return dashboard-ready KPI values.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

        kpis = build_kpis(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"KPI generation failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "kpis": kpis,
    }


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

@router.get(
    "/datasets/{dataset_id}/products"
)
def dataset_products(
    dataset_id: str,
):
    """
    Return product performance.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

        products = get_products(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Product analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "products": products,
    }


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

@router.get(
    "/datasets/{dataset_id}/regions"
)
def dataset_regions(
    dataset_id: str,
):
    """
    Return regional performance.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

        regions = get_regions(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Regional analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "regions": regions,
    }


# ============================================================
# TRENDS
# ============================================================

@router.get(
    "/datasets/{dataset_id}/trends"
)
def dataset_trends(
    dataset_id: str,
):
    """
    Return time-based trends.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        analysis = analyze_dataset(
            filepath
        )

        trends = get_trends(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Trend analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "trends": trends,
    }


# ============================================================
# COMPLETE DASHBOARD WITH FILTERS
# ============================================================

@router.get(
    "/datasets/{dataset_id}/dashboard"
)
def dataset_dashboard(
    dataset_id: str,

    product: str | None = Query(
        default=None,
        description="Filter by product.",
    ),

    region: str | None = Query(
        default=None,
        description="Filter by region.",
    ),

    start_date: str | None = Query(
        default=None,
        description=(
            "Start date. Use YYYY-MM or YYYY-MM-DD."
        ),
    ),

    end_date: str | None = Query(
        default=None,
        description=(
            "End date. Use YYYY-MM or YYYY-MM-DD."
        ),
    ),
):
    """
    Return dashboard data with optional filters.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:

        extension = os.path.splitext(
            filepath
        )[1].lower()

        if extension == ".csv":

            df = pd.read_csv(
                filepath
            )

        elif extension in {
            ".xlsx",
            ".xls",
        }:

            df = pd.read_excel(
                filepath
            )

        else:

            raise ValueError(
                "Unsupported dataset format."
            )

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load dataset: {str(e)}"
            ),
        )

    original_rows = int(
        len(df)
    )

    try:

        filtered_df = filter_dataframe(
            df=df,
            product=product,
            region=region,
            start_date=start_date,
            end_date=end_date,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dashboard filtering failed: {str(e)}"
            ),
        )

    filtered_rows = int(
        len(filtered_df)
    )

    if filtered_df.empty:

        return {
            "dataset": {
                "dataset_id": dataset_id,
                "filename": filename,
                "rows": 0,
                "columns": int(
                    len(df.columns)
                ),
                "filters": {
                    "product": product,
                    "region": region,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                "original_rows": original_rows,
                "filtered_rows": 0,
                "message": (
                    "No records match the selected filters."
                ),
            },
            "kpis": {},
            "charts": {
                "products": [],
                "regions": [],
                "trends": [],
            },
            "insights": {
                "summary": (
                    "No records matched the selected filters."
                ),
                "items": [],
                "recommendations": [],
            },
        }

    try:

        analysis = analyze_dataframe(
            filtered_df
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Filtered dataset analysis failed: "
                f"{str(e)}"
            ),
        )

    try:

        kpis = build_kpis(
            analysis
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"KPI generation failed: {str(e)}"
            ),
        )

    try:
        products = get_products(
            analysis
        )
    except Exception:
        products = []

    try:
        regions = get_regions(
            analysis
        )
    except Exception:
        regions = []

    try:
        trends = get_trends(
            analysis
        )
    except Exception:
        trends = []

    try:

        insights = generate_business_insights(
            analysis
        )

    except Exception as e:

        insights = {
            "summary": (
                "Business insights could not be generated."
            ),
            "insights": [],
            "recommendations": [],
            "warning": str(e),
        }

    try:

        dashboard = build_dashboard(
            dataset_id=dataset_id,
            filename=filename,
            analysis=analysis,
            kpis=kpis,
            insights=insights,
            products=products,
            regions=regions,
            trends=trends,
            filters={
                "product": product,
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Dashboard response generation failed: "
                f"{str(e)}"
            ),
        )

    dashboard["dataset"]["original_rows"] = (
        original_rows
    )

    dashboard["dataset"]["filtered_rows"] = (
        filtered_rows
    )

    return dashboard


# ============================================================
# PHASE 27 — AUTOMATIC CHART ANALYSIS
# ============================================================

@router.get(
    "/datasets/{dataset_id}/chart-analysis"
)
def dataset_chart_analysis(
    dataset_id: str,
):
    """
    Automatically analyze the dataset and determine:

    - detected dataset features
    - recommended visualizations
    - generated chart data
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Analyze dataset
    # --------------------------------------------------------

    try:

        analysis = analyze_dataset(
            filepath
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Build automatic chart intelligence
    # --------------------------------------------------------

    try:

        chart_analysis = build_chart_analysis(
            analysis
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Chart analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "analysis": chart_analysis,
    }



# ============================================================
# PHASE 28 — NATURAL LANGUAGE CHART GENERATION
# ============================================================

@router.post(
    "/datasets/{dataset_id}/chart-query"
)
def dataset_chart_query(
    dataset_id: str,
    question: str,
):
    """
    Generate a chart from a natural-language request.

    Examples:
        Show revenue by product
        Show revenue by region
        Show revenue trend
        Compare revenue and profit
        Compare revenue and cost
        Show top 5 products
    """

    if not dataset_id or not dataset_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    if not question or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Chart question is required.",
        )

    question = question.strip()

    dataset = find_dataset_file(dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    try:
        analysis = analyze_dataset(filepath)

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dataset analysis failed: {str(e)}",
        )

    try:
        result = generate_chart_from_question(
            question=question,
            analysis=analysis,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chart generation failed: {str(e)}",
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "question": question,
        "result": result,
    }

# ============================================================
# PHASE 29 — UNIFIED BI QUESTION AGENT
# ============================================================

@router.post(
    "/datasets/{dataset_id}/bi-question"
)
def dataset_bi_question(
    dataset_id: str,
    question: str,
):
    """
    Unified BI endpoint.

    Handles both business questions and chart requests.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    if not question or not question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    question = question.strip()

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Analyze dataset
    # --------------------------------------------------------

    try:

        analysis = analyze_dataset(
            filepath
        )

        kpis = build_kpis(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Business analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Analyze question
    # --------------------------------------------------------

    try:

        result = analyze_bi_question(
            question=question,
            analysis=analysis,
            kpis=kpis,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"BI question analysis failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "question": question,
        "result": result,
        "kpis": kpis,
    }


# ============================================================
# PHASE 30 — CONVERSATIONAL BI
# ============================================================

@router.post(
    "/datasets/{dataset_id}/conversation"
)
def dataset_bi_conversation(
    dataset_id: str,
    question: str,
    session_id: str,
):
    """
    Conversational BI endpoint.

    Keeps short-term memory so users can ask
    follow-up questions.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    if not session_id or not session_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Session ID is required.",
        )

    session_id = session_id.strip()

    if not question or not question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    question = question.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Analyze dataset
    # --------------------------------------------------------

    try:

        analysis = analyze_dataset(
            filepath
        )

        kpis = build_kpis(
            analysis
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Business analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Process conversational question
    # --------------------------------------------------------

    try:

        result = process_bi_conversation(
            session_id=session_id,
            dataset_id=dataset_id,
            filename=filename,
            question=question,
            analysis=analysis,
            kpis=kpis,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Conversational BI failed: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "session_id": session_id,
        "question": question,
        "result": result,
        "kpis": kpis,
    }






# ============================================================
# PHASE 24 — AGENT ANALYSIS + DYNAMIC CHARTS
# ============================================================

@router.post(
    "/datasets/{dataset_id}/ask"
)
def ask_business_dataset(
    dataset_id: str,
    question: str,
):
    """
    Analyze a natural-language business question
    against the calculated dataset metrics.

    Returns:
        - answer
        - analysis type
        - selected chart
        - all available charts
        - KPIs
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question or not question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question is required.",
        )

    question = question.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Analyze dataset
    # --------------------------------------------------------

    try:

        analysis = analyze_dataset(
            filepath
        )

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Build KPIs and business data
    # --------------------------------------------------------

    try:

        kpis = build_kpis(
            analysis
        )

        products = get_products(
            analysis
        )

        regions = get_regions(
            analysis
        )

        trends = get_trends(
            analysis
        )
        detailed_products = analysis.get(
            "detailed_products",
            [],
        )
        detailed_regions = analysis.get(
            "detailed_regions",
            [],
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Business analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Build dynamic charts
    # --------------------------------------------------------

    try:

        charts = build_charts(
            products=products,
            regions=regions,
            trends=trends,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Chart generation failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Analyze question
    # --------------------------------------------------------

    try:

        agent_result = (
            analyze_dashboard_question(
                question=question,
                analysis=analysis,
                kpis=kpis,
                products=products,
                regions=regions,
                trends=trends,
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Agent analysis failed: {str(e)}"
            ),
        )

    if not isinstance(
        agent_result,
        dict,
    ):

        agent_result = {
            "answer": (
                "Unable to analyze the question."
            ),
            "type": "general_analysis",
            "chart_type": None,
        }

    # --------------------------------------------------------
    # Selected chart
    # --------------------------------------------------------

    selected_chart = None

    chart_type = agent_result.get(
        "chart_type"
    )

    if chart_type == "products":

        for chart in charts:

            if (
                isinstance(chart, dict)
                and chart.get("title")
                == "Revenue by Product"
            ):

                selected_chart = chart
                break

    elif chart_type == "regions":

        for chart in charts:

            if (
                isinstance(chart, dict)
                and chart.get("title")
                == "Revenue by Region"
            ):

                selected_chart = chart
                break

    elif chart_type == "trends":

        for chart in charts:

            if (
                isinstance(chart, dict)
                and chart.get("title")
                == "Revenue Trend"
            ):

                selected_chart = chart
                break

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "question": question,

        "answer": agent_result.get(
            "answer",
            "",
        ),

        "analysis_type": agent_result.get(
            "type",
            "general_analysis",
        ),

        "chart": selected_chart,

        "available_charts": charts,

        "kpis": kpis,
    }

# ============================================================
# PHASE 31 — DATASET EXPLORATION
# ============================================================

@router.get(
    "/datasets/{dataset_id}/explore"
)
def explore_business_dataset(
    dataset_id: str,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of sample rows to return.",
    ),
):
    """
    Explore an uploaded business dataset.

    Returns:
        - dataset metadata
        - rows and columns
        - column data types
        - missing values
        - unique values
        - sample records
        - numeric statistics
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    try:

        extension = os.path.splitext(
            filepath
        )[1].lower()

        if extension == ".csv":

            df = pd.read_csv(
                filepath
            )

        elif extension in {
            ".xlsx",
            ".xls",
        }:

            df = pd.read_excel(
                filepath
            )

        else:

            raise ValueError(
                "Unsupported dataset format."
            )

        # Clean column names

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load dataset: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Basic dataset information
    # --------------------------------------------------------

    rows = int(
        len(df)
    )

    columns = int(
        len(df.columns)
    )

    # --------------------------------------------------------
    # Column information
    # --------------------------------------------------------

    column_info = []

    for column in df.columns:

        series = df[column]

        column_info.append(
            {
                "name": str(column),

                "dtype": str(
                    series.dtype
                ),

                "missing": int(
                    series.isna().sum()
                ),

                "missing_percentage": round(
                    float(
                        series.isna().mean() * 100
                    ),
                    2,
                ),

                "unique_values": int(
                    series.nunique(
                        dropna=True
                    )
                ),
            }
        )

    # --------------------------------------------------------
    # Sample rows
    # --------------------------------------------------------

    try:

        sample_df = df.head(
            limit
        )

        # Convert NaN / NaT to None

        sample_df = sample_df.astype(
            object
        ).where(
            pd.notna(sample_df),
            None,
        )

        sample_rows = (
            sample_df.to_dict(
                orient="records"
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to generate sample data: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Numeric statistics
    # --------------------------------------------------------

    numeric_statistics = {}

    try:

        numeric_df = df.select_dtypes(
            include="number"
        )

        if not numeric_df.empty:

            statistics_df = numeric_df.describe()

            statistics_df = statistics_df.astype(
                object
            ).where(
                pd.notna(statistics_df),
                None,
            )

            numeric_statistics = (
                statistics_df.to_dict()
            )

    except Exception:

        numeric_statistics = {}

    # --------------------------------------------------------
    # Dataset response
    # --------------------------------------------------------

    return {
        "dataset": {
            "dataset_id": dataset_id,
            "filename": filename,
            "extension": extension,
            "rows": rows,
            "columns": columns,
        },

        "columns": column_info,

        "sample": {
            "limit": limit,
            "returned": len(
                sample_rows
            ),
            "rows": sample_rows,
        },

        "statistics": {
            "numeric": numeric_statistics,
        },
    }

# ============================================================
# PHASE 32 — DATASET DATA QUALITY
# ============================================================

@router.get(
    "/datasets/{dataset_id}/quality"
)
def dataset_quality(
    dataset_id: str,
):
    """
    Analyze dataset quality.

    Detects:
        - missing values
        - duplicate rows
        - empty columns
        - constant columns
        - column data types
        - quality score
        - warnings
        - recommendations
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    try:

        extension = os.path.splitext(
            filepath
        )[1].lower()

        if extension == ".csv":

            df = pd.read_csv(
                filepath
            )

        elif extension in {
            ".xlsx",
            ".xls",
        }:

            df = pd.read_excel(
                filepath
            )

        else:

            raise ValueError(
                "Unsupported dataset format."
            )

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load dataset: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Analyze quality
    # --------------------------------------------------------

    try:

        quality = analyze_data_quality(
            df
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset quality analysis failed: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "quality": quality,
    }

# ============================================================
# PHASE 33 — DATASET CLEANING & PREPROCESSING
# ============================================================

@router.post(
    "/datasets/{dataset_id}/clean"
)
def clean_business_dataset(
    dataset_id: str,

    remove_duplicates: bool = Query(
        default=True,
        description="Remove duplicate rows.",
    ),

    remove_empty_columns: bool = Query(
        default=True,
        description="Remove completely empty columns.",
    ),

    fill_missing_numeric: bool = Query(
        default=True,
        description=(
            "Fill missing numeric values using the median."
        ),
    ),

    fill_missing_text: bool = Query(
        default=True,
        description=(
            "Fill missing text values using 'Unknown'."
        ),
    ),
):
    """
    Clean and preprocess a business dataset.
    """

    # --------------------------------------------------------
    # Validate dataset ID
    # --------------------------------------------------------

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    # --------------------------------------------------------
    # Find dataset
    # --------------------------------------------------------

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    filename, filepath = dataset

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    try:

        extension = os.path.splitext(
            filepath
        )[1].lower()

        if extension == ".csv":

            df = pd.read_csv(
                filepath
            )

        elif extension in {
            ".xlsx",
            ".xls",
        }:

            df = pd.read_excel(
                filepath
            )

        else:

            raise ValueError(
                "Unsupported dataset format."
            )

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load dataset: {str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Clean dataset
    # --------------------------------------------------------

    try:

        result = clean_dataframe(
            df=df,
            remove_duplicates=(
                remove_duplicates
            ),
            remove_empty_columns=(
                remove_empty_columns
            ),
            fill_missing_numeric=(
                fill_missing_numeric
            ),
            fill_missing_text=(
                fill_missing_text
            ),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset cleaning failed: {str(e)}"
            ),
        )

    cleaned_df = result[
        "dataframe"
    ]

    stats = result[
        "stats"
    ]

    # --------------------------------------------------------
    # Save cleaned dataset
    # --------------------------------------------------------

    cleaned_filename = (
        f"{dataset_id}_cleaned.csv"
    )

    cleaned_filepath = os.path.join(
        BUSINESS_UPLOAD_DIR,
        cleaned_filename,
    )

    try:

        cleaned_df.to_csv(
            cleaned_filepath,
            index=False,
        )
        cleaned_version = register_cleaned_version(
        dataset_id=dataset_id,
        filename=cleaned_filename,
        filepath=cleaned_filepath,
        stats=stats,
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to save cleaned dataset: "
                f"{str(e)}"
            ),
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "message": (
        "Dataset cleaned successfully."
      ),
        "dataset_id": dataset_id,
        "original_filename": filename,
        "cleaned_filename": cleaned_filename,
        "cleaned_filepath": cleaned_filepath,
        "version": cleaned_version,
        "stats": stats,
    }

# ============================================================
# PHASE 34 — DATASET VERSIONS
# ============================================================

@router.get(
    "/datasets/{dataset_id}/versions"
)
def dataset_versions(
    dataset_id: str,
):
    """
    Return all available dataset versions.
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    dataset = find_dataset_file(
        dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    try:

        metadata = load_versions(
            dataset_id
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to load dataset versions: {str(e)}"
            ),
        )

    return {
        "dataset_id": dataset_id,
        "active_version": metadata.get(
            "active_version",
            "original",
        ),
        "versions": metadata.get(
            "versions",
            [],
        ),
    }

# ============================================================
# PHASE 34 — ACTIVATE DATASET VERSION
# ============================================================

@router.post(
    "/datasets/{dataset_id}/activate"
)
def activate_dataset_version(
    dataset_id: str,
    version: str,
):
    """
    Activate a specific dataset version.

    Example:
        original
        cleaned_v1
        cleaned_v2
    """

    if not dataset_id or not dataset_id.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset ID is required.",
        )

    dataset_id = dataset_id.strip()

    if not version or not version.strip():

        raise HTTPException(
            status_code=400,
            detail="Dataset version is required.",
        )

    version = version.strip()

    try:

        selected = activate_version(
            dataset_id=dataset_id,
            version=version,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to activate dataset version: {str(e)}"
            ),
        )

    return {
        "message": (
            "Dataset version activated successfully."
        ),
        "dataset_id": dataset_id,
        "active_version": version,
        "dataset": selected,
    }

