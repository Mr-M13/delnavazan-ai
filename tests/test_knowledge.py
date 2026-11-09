import json
from datetime import date

import pytest

from delnavazan_ai.knowledge import load_approved, retrieve


def fixture_file(tmp_path, entries):
    path = tmp_path / "knowledge.json"
    path.write_text(json.dumps({"schema_version": 1, "entries": entries}), encoding="utf-8")
    return path


def entry(**overrides):
    item = {
        "id": "tar", "title": "آموزش تار", "text": "کلاس تار به صورت آنلاین است",
        "source_url": "https://delnavazan.com/", "version": 1,
        "status": "approved", "approved_by": "admin",
        "effective_from": "2026-01-01", "effective_until": None,
        "tags": ["تار", "tar"],
    }
    item.update(overrides)
    return item


def test_draft_never_retrieved(tmp_path):
    path = fixture_file(tmp_path, [entry(status="draft")])
    assert load_approved(path, date(2026, 11, 9)) == []


def test_approval_identity_required(tmp_path):
    path = fixture_file(tmp_path, [entry(approved_by=None)])
    assert load_approved(path, date(2026, 11, 9)) == []


def test_expired_and_future_not_loaded(tmp_path):
    path = fixture_file(tmp_path, [
        entry(id="old", effective_until="2026-11-08"),
        entry(id="future", effective_from="2026-11-10"),
    ])
    assert load_approved(path, date(2026, 11, 9)) == []


def test_only_https_sources(tmp_path):
    path = fixture_file(tmp_path, [entry(source_url="http://internal/")])
    assert load_approved(path, date(2026, 11, 9)) == []


def test_persian_keyword_retrieval(tmp_path):
    items = load_approved(fixture_file(tmp_path, [entry()]), date(2026, 11, 9))
    assert [item.id for item in retrieve("آموزش تار", items)] == ["tar"]
    assert retrieve("پیانو", items) == []


def test_duplicate_id_rejected(tmp_path):
    with pytest.raises(ValueError, match="Duplicate"):
        load_approved(fixture_file(tmp_path, [entry(), entry()]), date(2026, 11, 9))


def test_repository_content_is_draft():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "knowledge/public-v1.json"
    assert load_approved(path, date(2026, 11, 9)) == []
