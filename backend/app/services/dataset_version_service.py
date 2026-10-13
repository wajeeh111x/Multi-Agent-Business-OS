import json
import os
from datetime import datetime


VERSION_DIR = "uploads/business/versions"


def ensure_version_directory():
    os.makedirs(
        VERSION_DIR,
        exist_ok=True,
    )


def get_metadata_path(
    dataset_id: str,
):
    ensure_version_directory()

    return os.path.join(
        VERSION_DIR,
        f"{dataset_id}.json",
    )


def load_versions(
    dataset_id: str,
):
    path = get_metadata_path(
        dataset_id
    )

    if not os.path.exists(path):
        return {
            "dataset_id": dataset_id,
            "active_version": "original",
            "versions": [],
        }

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except Exception:

        return {
            "dataset_id": dataset_id,
            "active_version": "original",
            "versions": [],
        }


def save_versions(
    dataset_id: str,
    metadata: dict,
):
    path = get_metadata_path(
        dataset_id
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            default=str,
        )


def register_original_version(
    dataset_id: str,
    filename: str,
    filepath: str,
):
    metadata = load_versions(
        dataset_id
    )

    versions = metadata.get(
        "versions",
        [],
    )

    existing = [
        version
        for version in versions
        if version.get("version") == "original"
    ]

    if not existing:

        versions.append(
            {
                "version": "original",
                "type": "original",
                "filename": filename,
                "filepath": filepath,
                "created_at": (
                    datetime.utcnow()
                    .isoformat()
                ),
            }
        )

    metadata[
        "active_version"
    ] = metadata.get(
        "active_version",
        "original",
    )

    metadata[
        "versions"
    ] = versions

    save_versions(
        dataset_id,
        metadata,
    )

    return metadata


def register_cleaned_version(
    dataset_id: str,
    filename: str,
    filepath: str,
    stats: dict,
):
    metadata = load_versions(
        dataset_id
    )

    versions = metadata.get(
        "versions",
        [],
    )

    cleaned_versions = [
        version
        for version in versions
        if version.get("type") == "cleaned"
    ]

    version_number = (
        len(cleaned_versions) + 1
    )

    version_name = (
        f"cleaned_v{version_number}"
    )

    version_data = {
        "version": version_name,
        "type": "cleaned",
        "filename": filename,
        "filepath": filepath,
        "created_at": (
            datetime.utcnow()
            .isoformat()
        ),
        "stats": stats,
    }

    versions.append(
        version_data
    )

    metadata[
        "versions"
    ] = versions

    save_versions(
        dataset_id,
        metadata,
    )

    return version_data


def activate_version(
    dataset_id: str,
    version: str,
):
    metadata = load_versions(
        dataset_id
    )

    versions = metadata.get(
        "versions",
        [],
    )

    selected = None

    for item in versions:

        if item.get(
            "version"
        ) == version:

            selected = item
            break

    if selected is None:

        raise ValueError(
            f"Dataset version '{version}' not found."
        )

    filepath = selected.get(
        "filepath"
    )

    if not filepath or not os.path.exists(
        filepath
    ):

        raise ValueError(
            "Dataset version file does not exist."
        )

    metadata[
        "active_version"
    ] = version

    save_versions(
        dataset_id,
        metadata,
    )

    return selected


def get_active_version(
    dataset_id: str,
):
    metadata = load_versions(
        dataset_id
    )

    active_version = metadata.get(
        "active_version",
        "original",
    )

    versions = metadata.get(
        "versions",
        [],
    )

    for version in versions:

        if version.get(
            "version"
        ) == active_version:

            return version

    return None

def get_active_dataset_file(
    dataset_id: str,
):
    """
    Return the currently active dataset version.

    Falls back to the original uploaded dataset
    if version metadata does not exist yet.
    """

    active_version = get_active_version(
        dataset_id
    )

    if active_version is None:
        return None

    filepath = active_version.get(
        "filepath"
    )

    if not filepath:
        return None

    if not os.path.isfile(filepath):
        return None

    return (
        active_version.get(
            "filename"
        ),
        filepath,
        active_version.get(
            "version",
            "original",
        ),
    )