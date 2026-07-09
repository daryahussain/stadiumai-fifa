from pydantic import BaseModel


LANGUAGES = ["english", "spanish", "french", "arabic", "hindi"]


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class TranslateResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
