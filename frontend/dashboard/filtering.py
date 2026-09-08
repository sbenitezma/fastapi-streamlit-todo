"""The ``Filters`` value object and query-parameter parsing.

Pure: no Streamlit, no I/O. The Streamlit filter bar lives in ``app.filters``.
"""

from dataclasses import dataclass
from datetime import date

from dashboard.config import DATE_FIELD_OPTIONS, STATUS_OPTIONS

STATUS_LABEL = {v: k for k, v in STATUS_OPTIONS.items()}
DATE_FIELD_LABEL = {v: k for k, v in DATE_FIELD_OPTIONS.items()}
_VALID_STATUS = {v for v in STATUS_OPTIONS.values() if v}
_VALID_DATE_FIELD = set(DATE_FIELD_OPTIONS.values())


@dataclass(frozen=True)
class Filters:
    """The active filter selection. Immutable value object."""

    status: str | None = None
    date_field: str = "created"
    date_from: date | None = None
    date_to: date | None = None

    @property
    def date_range_active(self) -> bool:
        return bool(self.date_from or self.date_to)

    @property
    def active(self) -> bool:
        return bool(self.status) or self.date_range_active

    def to_query(self) -> dict[str, str]:
        """Query parameters for ``GET /api/todos`` (and the browser URL)."""
        query: dict[str, str] = {}
        if self.status:
            query["status"] = self.status
        if self.date_from:
            query["date_from"] = self.date_from.isoformat()
        if self.date_to:
            query["date_to"] = self.date_to.isoformat()
        if self.date_range_active and self.date_field != "created":
            query["date_field"] = self.date_field
        return query

    def chips(self) -> list[tuple[str, str]]:
        """``(facet, label)`` pairs for each active filter."""
        out: list[tuple[str, str]] = []
        if self.status:
            out.append(("status", f"Status: {STATUS_LABEL[self.status]}"))
        if self.date_range_active:
            lo = self.date_from.isoformat() if self.date_from else "…"
            hi = self.date_to.isoformat() if self.date_to else "…"
            out.append(("dates", f"{DATE_FIELD_LABEL[self.date_field]}: {lo} → {hi}"))
        return out


def _parse_date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def filters_from_query(params) -> Filters:
    """Build ``Filters`` from a mapping of query parameters (invalid values ignored)."""
    status = params.get("status")
    date_field = params.get("date_field", "created")
    return Filters(
        status=status if status in _VALID_STATUS else None,
        date_field=date_field if date_field in _VALID_DATE_FIELD else "created",
        date_from=_parse_date(params.get("date_from")),
        date_to=_parse_date(params.get("date_to")),
    )
