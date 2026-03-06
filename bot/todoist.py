"""Todoist integration for syncing notes and summaries."""

import logging
from datetime import date
from typing import TYPE_CHECKING, Any

from config import CATEGORY_EMOJIS, TODOIST_API_TOKEN, TODOIST_PROJECT_NAME

if TYPE_CHECKING:
    from todoist_api_python.api import TodoistAPI

logger = logging.getLogger(__name__)

# Cache for project and label IDs
_project_id: str | None = None
_label_ids: dict[str, str] = {}


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
        # Check if project exists
        projects = api.get_projects()
        for project in projects:
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
        # Check if label exists
        labels = api.get_labels()
        for label in labels:
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
        project_id = _get_or_create_project(api)
        if not project_id:
            return False

        # Get emoji for category
        emoji = CATEGORY_EMOJIS.get(category, "📌")

        # Create task
        api.add_task(
            content=f"{emoji} {summary}",
            description=transcript if transcript != summary else "",
            project_id=project_id,
            labels=[category],
        )

        logger.info(f"Synced note to Todoist: {category} - {summary[:30]}...")
        return True

    except Exception as e:
        logger.error(f"Failed to sync note to Todoist: {e}")
        return False


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
        project_id = _get_or_create_project(api)
        if not project_id:
            return False

        today = date.today().strftime("%B %d, %Y")

        # Create summary task
        api.add_task(
            content=f"📋 Daily Summary - {today} ({notes_count} notes)",
            description=summary_text,
            project_id=project_id,
            labels=["Daily Summary"],
        )

        logger.info(f"Synced daily summary to Todoist: {notes_count} notes")
        return True

    except Exception as e:
        logger.error(f"Failed to sync daily summary to Todoist: {e}")
        return False
