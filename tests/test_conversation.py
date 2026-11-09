from delnavazan_ai.conversation import (
    PublicFact,
    needs_human,
    prepare_instructions,
    reply_to_public_query,
)
from delnavazan_ai.settings import Settings


class FakeGenerator:
    def __init__(self, answer: str = "کلاس‌ها به صورت آنلاین برگزار می‌شوند.") -> None:
        self.answer = answer
        self.called = False

    def generate(self, instructions: str, user_text: str) -> str:
        self.called = True
        assert "public" in instructions.lower()
        return self.answer


def test_explicit_human_request_escalates_without_model_call() -> None:
    fake = FakeGenerator()
    response = reply_to_public_query(
        "می‌خوام با اپراتور حرف بزنم",
        [PublicFact("faq", "Public lesson info")],
        fake,
        Settings(enable_ai_responses=True, openai_api_key="test-key"),
    )
    assert response.escalate and not fake.called


def test_private_payment_question_escalates() -> None:
    assert needs_human("What happened to my payment?")
    assert needs_human("وضعیت رزرو من چیست؟")


def test_unapproved_sources_excluded() -> None:
    instructions, sources = prepare_instructions(
        [PublicFact("internal", "PRIVATE", approved=False), PublicFact("faq", "Online classes")]
    )
    assert sources == ("faq",)
    assert "PRIVATE" not in instructions


def test_no_public_sources_fails_closed() -> None:
    fake = FakeGenerator()
    result = reply_to_public_query(
        "کلاس تار دارید؟", [], fake,
        Settings(enable_ai_responses=True, openai_api_key="test-key"),
    )
    assert result.escalate and not fake.called


def test_feature_flag_disabled_fails_closed() -> None:
    fake = FakeGenerator()
    result = reply_to_public_query(
        "کلاس تار دارید؟", [PublicFact("faq", "Tar lessons")], fake,
        Settings(enable_ai_responses=False, openai_api_key="test-key"),
    )
    assert result.escalate and not fake.called


def test_public_question_uses_approved_source() -> None:
    fake = FakeGenerator()
    result = reply_to_public_query(
        "کلاس‌ها آنلاین هستند؟", [PublicFact("faq-online", "Online classes")], fake,
        Settings(enable_ai_responses=True, openai_api_key="test-key"),
    )
    assert not result.escalate
    assert result.source_ids == ("faq-online",)
    assert fake.called


def test_empty_model_output_escalates() -> None:
    result = reply_to_public_query(
        "سلام", [PublicFact("faq", "Online classes")], FakeGenerator(""),
        Settings(enable_ai_responses=True, openai_api_key="test-key"),
    )
    assert result.escalate
