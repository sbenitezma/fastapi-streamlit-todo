"""Static configuration and option maps for the dashboard."""

import os

API_URL = os.environ.get("API_URL", "http://localhost:8000/api")
API_TIMEOUT = 5

# label -> value sent to the API (None means "no filter")
STATUS_OPTIONS: dict[str, str | None] = {
    "All": None,
    "Pending": "pending",
    "Done": "done",
}
DATE_FIELD_OPTIONS: dict[str, str] = {
    "Created": "created",
    "Updated": "updated",
    "Completed": "completed",
}
THEME_CHOICES: tuple[str, ...] = ("System", "Light", "Dark")
