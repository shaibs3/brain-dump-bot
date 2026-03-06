"""Todoist integration for syncing notes and summaries."""

import logging
import time
from collections.abc import Callable
from datetime import date
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from config import CATEGORY_EMOJIS, TODOIST_API_TOKEN, TODOIST_PROJECT_NAME

if TYPE_CHECKING:
    from todoist_api_python.api import TodoistAPI

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # seconds
BACKOFF_MULTIPLIER = 2.0

# Cache for project and label IDs
_project_id: str | None = None
_label_ids: dict[str, str] = {}

T = TypeVar("T")


def _retry_with_backoff(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to retry a function with exponential backoff."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        delay = INITIAL_DELAY
        last_exception: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Todoist API call failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= BACKOFF_MULTIPLIER

        logger.error(f"Todoist API call failed after {MAX_RETRIES} attempts: {last_exception}")
        raise last_exception  # type: ignore[misc]

    return wrapper


def is_todoist_enabled() -> bool:
    """Check if Todoist integration is configured."""
    return bool(TODOIST_API_TOKEN)


def _get_client() -> "TodoistAPI | None":
    """Get Todoist API client (lazy loaded)."""
    if not TODOIST_API_TOKEN:
        return None
    from todoist_api_python.api import TodoistAPI

    return TodoistAPI(TODOIST_API_TOKEN)


def _get_or_create_project(api: Any) -> str | None:
    """Get or create the Brain Dump project."""
    global _project_id

    if _project_id:
        return _project_id

    try:
        # Check if project exists (paginated results)
        for page in api.get_projects():
            for project in page:
                if project.name == TODOIST_PROJECT_NAME:
                    _project_id = str(project.id)
                    logger.info(f"Found existing Todoist project: {TODOIST_PROJECT_NAME}")
                    return _project_id

        # Create project if not exists
        project = api.add_project(name=TODOIST_PROJECT_NAME)
        _project_id = str(project.id)
        logger.info(f"Created Todoist project: {TODOIST_PROJECT_NAME}")
        return _project_id

    except Exception as e:
        logger.error(f"Failed to get/create Todoist project: {e}")
        return None


def _get_or_create_label(api: Any, category: str) -> str | None:
    """Get or create a label for a category."""
    global _label_ids

    if category in _label_ids:
        return _label_ids[category]

    try:
        # Check if label exists (paginated results)
        for page in api.get_labels():
            for label in page:
                if label.name == category:
                    _label_ids[category] = str(label.id)
                    return str(label.id)

        # Create label if not exists
        label = api.add_label(name=category)
        _label_ids[category] = str(label.id)
        logger.info(f"Created Todoist label: {category}")
        return str(label.id)

    except Exception as e:
        logger.error(f"Failed to get/create Todoist label: {e}")
        return None


def sync_note_to_todoist(category: str, summary: str, transcript: str) -> bool:
    """
    Sync a single note to Todoist as a task.

    Args:
        category: Note category (e.g., "Career", "Health")
        summary: Short summary of the note
        transcript: Full transcript as task description

    Returns:
        True if sync successful, False otherwise
    """
    if not is_todoist_enabled():
        return False

    api = _get_client()
    if not api:
        return False

    try:
        _sync_note_with_retry(api, category, summary, transcript)
        logger.info(f"Synced note to Todoist: {category} - {summary[:30]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to sync note to Todoist after retries: {e}")
        return False


@_retry_with_backoff
def _sync_note_with_retry(api: Any, category: str, summary: str, transcript: str) -> None:
    """Internal function to sync note with retry logic."""
    project_id = _get_or_create_project(api)
    if not project_id:
        raise RuntimeError("Failed to get/create project")

    emoji = CATEGORY_EMOJIS.get(category, "📌")
    api.add_task(
        content=f"{emoji} {summary}",
        description=transcript if transcript != summary else "",
        project_id=project_id,
        labels=[category],
    )


def sync_daily_summary_to_todoist(summary_text: str, notes_count: int) -> bool:
    """
    Sync daily summary to Todoist as a task.

    Args:
        summary_text: The full summary text
        notes_count: Number of notes in the summary

    Returns:
        True if sync successful, False otherwise
    """
    if not is_todoist_enabled():
        return False

    api = _get_client()
    if not api:
        return False

    try:
        _sync_summary_with_retry(api, summary_text, notes_count)
        logger.info(f"Synced daily summary to Todoist: {notes_count} notes")
        return True
    except Exception as e:
        logger.error(f"Failed to sync daily summary to Todoist after retries: {e}")
        return False


@_retry_with_backoff
def _sync_summary_with_retry(api: Any, summary_text: str, notes_count: int) -> None:
    """Internal function to sync summary with retry logic."""
    project_id = _get_or_create_project(api)
    if not project_id:
        raise RuntimeError("Failed to get/create project")

    today = date.today().strftime("%B %d, %Y")
    api.add_task(
        content=f"📋 Daily Summary - {today} ({notes_count} notes)",
        description=summary_text,
        project_id=project_id,
        labels=["Daily Summary"],
    )
