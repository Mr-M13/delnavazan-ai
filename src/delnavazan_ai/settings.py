from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DZN_AI_", extra="ignore")

    environment: str = "development"
    database_url: str = ""
    enable_outbound_messages: bool = False
    enable_ai_responses: bool = False
    openai_api_key: str = ""
    chatwoot_api_token: str = ""
    meta_access_token: str = ""
    timezone: str = "Australia/Brisbane"
    acknowledgement_reminder_minutes: int = 5
    backup_escalation_minutes: int = 15


settings = Settings()
