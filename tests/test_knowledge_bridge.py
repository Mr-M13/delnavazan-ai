import json
from datetime import date

from delnavazan_ai.knowledge_bridge import answer_with_approved_knowledge
from delnavazan_ai.settings import Settings


class FakeGenerator:
    def __init__(self):
        self.calls = 0

    def generate(self, instructions, user_text):
        self.calls += 1
        assert "آموزش تار" in instructions
        return "کلاس تار آنلاین است."


def test_only_relevant_approved_fact_reaches_model(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "entries": [
                    {
                        "id": "tar",
                        "title": "آموزش تار",
                        "text": "کلاس تار آنلاین است",
                        "source_url": "https://delnavazan.com/tar",
                        "version": 2,
                        "status": "approved",
                        "approved_by": "editor",
                        "effective_from": "2026-01-01",
                    },
                    {
                        "id": "private",
                        "title": "آموزش تار",
                        "text": "PRIVATE DO NOT SEND",
                        "source_url": "https://delnavazan.com/private",
                        "version": 1,
                        "status": "draft",
                        "effective_from": "2026-01-01",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    generator = FakeGenerator()
    result = answer_with_approved_knowledge(
        "آموزش تار", catalog, generator,
        Settings(enable_ai_responses=True, openai_api_key="fake"),
        today=date(2026, 11, 9),
    )
    assert not result.escalate
    assert result.source_ids == ("tar@v2:https://delnavazan.com/tar",)
    assert generator.calls == 1


def test_unknown_question_escalates_without_model(tmp_path):
    catalog = tmp_path / "catalog.json"
    catalog.write_text('{"schema_version": 1, "entries": []}', encoding="utf-8")
    generator = FakeGenerator()
    result = answer_with_approved_knowledge(
        "شهریه چقدر است؟", catalog, generator,
        Settings(enable_ai_responses=True, openai_api_key="fake"),
        today=date(2026, 11, 9),
    )
    assert result.escalate
    assert generator.calls == 0
