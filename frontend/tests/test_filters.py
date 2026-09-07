"""Unit tests for app.filtering (Filters value object, query parsing)."""

from datetime import date

from app.filtering import Filters, filters_from_query


def test_defaults_are_inactive():
    f = Filters()
    assert f.active is False
    assert f.date_range_active is False
    assert f.to_query() == {}
    assert f.chips() == []


def test_status_makes_it_active():
    f = Filters(status="pending")
    assert f.active is True
    assert f.to_query() == {"status": "pending"}


def test_date_range_query_and_field_only_when_relevant():
    f = Filters(date_from=date(2026, 9, 1), date_to=date(2026, 9, 30))
    assert f.to_query() == {"date_from": "2026-09-01", "date_to": "2026-09-30"}

    f2 = Filters(date_field="completed", date_from=date(2026, 9, 1))
    assert f2.to_query() == {"date_from": "2026-09-01", "date_field": "completed"}

    # date_field is irrelevant without a bound -> not emitted
    assert Filters(date_field="completed").to_query() == {}


def test_chips_labels():
    f = Filters(status="done", date_field="completed", date_from=date(2026, 9, 1))
    facets = dict(f.chips())
    assert facets["status"] == "Status: Done"
    assert facets["dates"] == "Completed: 2026-09-01 → …"


def test_from_query_roundtrip():
    params = {"status": "done", "date_field": "completed", "date_from": "2026-09-01"}
    f = filters_from_query(params)
    assert f == Filters(status="done", date_field="completed",
                        date_from=date(2026, 9, 1))
    assert f.to_query() == params


def test_from_query_ignores_garbage():
    f = filters_from_query(
        {"status": "bogus", "date_field": "nope", "date_from": "not-a-date"}
    )
    assert f == Filters()


def test_from_query_empty():
    assert filters_from_query({}) == Filters()
