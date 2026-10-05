"""Rubric Management and Versioning System.

Parses YAML rubric files, maintains active version state, validates category tags,
and supports instant rollback for QA governance.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentassure.config import settings
from agentassure.db.models.rubric import RubricVersion


class RubricsManager:
    """Manages versioned QA evaluation rubrics and taxonomy definitions."""

    _cached_rubrics: Dict[str, Dict[str, Any]] = {}
    _active_version_tag: str = "v1.0"

    @classmethod
    def load_yaml_rubric(cls, file_path: Path) -> Dict[str, Any]:
        """Parse and validate YAML rubric file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Rubric file not found at: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        version = data.get("version", "v1.0")
        cls._cached_rubrics[version] = data
        return data

    @classmethod
    def get_rubric(cls, version: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve rubric definition by version tag, or active version if None."""
        target_version = version or cls._active_version_tag

        if target_version in cls._cached_rubrics:
            return cls._cached_rubrics[target_version]

        # Attempt to load from default config directory
        config_dir = settings.RUBRICS_DIR
        candidate_file = config_dir / f"rubrics_{target_version}.yaml"
        if candidate_file.exists():
            return cls.load_yaml_rubric(candidate_file)

        # Fallback to first available in directory
        for f in config_dir.glob("rubrics_*.yaml"):
            rubric = cls.load_yaml_rubric(f)
            if rubric.get("version") == target_version:
                return rubric

        # If cache has any, return latest cached
        if cls._cached_rubrics:
            return next(iter(cls._cached_rubrics.values()))

        raise ValueError(f"Rubric version '{target_version}' not found.")

    @classmethod
    def set_active_version(cls, version_tag: str) -> None:
        """Activate specific rubric version tag."""
        # Ensure it exists
        _ = cls.get_rubric(version_tag)
        cls._active_version_tag = version_tag

    @classmethod
    def get_active_version(cls) -> str:
        """Get the current active rubric version string."""
        return cls._active_version_tag

    @classmethod
    def validate_category(cls, category_l1: str, category_l2: str) -> bool:
        """Check if an L1 category and L2 subcategory exist in the active rubric."""
        rubric = cls.get_rubric()
        for cat in rubric.get("categories", []):
            if cat["name"].lower() == category_l1.lower():
                subcats = [s["name"].lower() for s in cat.get("subcategories", [])]
                if category_l2.lower() in subcats:
                    return True
        return False

    @classmethod
    def sync_to_db(cls, db: Session) -> None:
        """Synchronize disk YAML rubrics into database table."""
        config_dir = settings.RUBRICS_DIR
        if not config_dir.exists():
            return

        for f in config_dir.glob("rubrics_*.yaml"):
            rubric_dict = cls.load_yaml_rubric(f)
            v_tag = rubric_dict.get("version", "v1.0")
            existing = db.scalar(select(RubricVersion).where(RubricVersion.version_tag == v_tag))
            raw_yaml = yaml.dump(rubric_dict)

            if not existing:
                rv = RubricVersion(
                    version_tag=v_tag,
                    description=rubric_dict.get("description", "Quality Rubric"),
                    content_yaml=raw_yaml,
                    is_active=(v_tag == cls._active_version_tag),
                )
                db.add(rv)
            else:
                existing.content_yaml = raw_yaml
                existing.description = rubric_dict.get("description", existing.description)
                existing.is_active = v_tag == cls._active_version_tag

        db.commit()
