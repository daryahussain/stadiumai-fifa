import os

from fastapi import APIRouter, HTTPException

from app.schemas.translation import TranslateRequest, TranslateResponse, LANGUAGES

router = APIRouter()


TRANSLATIONS = {
    "spanish": {
        "hello": "hola",
        "welcome": "bienvenido",
        "where is my seat": "¿dónde está mi asiento?",
        "restroom": "baño",
        "food court": "plaza de comidas",
        "gate": "puerta",
        "parking": "estacionamiento",
        "emergency": "emergencia",
    },
    "french": {
        "hello": "bonjour",
        "welcome": "bienvenue",
        "where is my seat": "où est ma place?",
        "restroom": "toilettes",
        "food court": "aire de restauration",
        "gate": "porte",
        "parking": "stationnement",
        "emergency": "urgence",
    },
    "arabic": {
        "hello": "مرحبا",
        "welcome": "أهلا وسهلا",
        "where is my seat": "أين مقعدي؟",
        "restroom": "حمام",
        "food court": "ساحة الطعام",
        "gate": "بوابة",
        "parking": "موقف سيارات",
        "emergency": "طوارئ",
    },
    "hindi": {
        "hello": "नमस्ते",
        "welcome": "स्वागत है",
        "where is my seat": "मेरी सीट कहाँ है?",
        "restroom": "शौचालय",
        "food court": "फूड कोर्ट",
        "gate": "गेट",
        "parking": "पार्किंग",
        "emergency": "आपातकाल",
    },
}


async def translate_with_llm(text: str, target_language: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}. Respond with only the translation."},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def translate_with_dict(text: str, target_language: str) -> str:
    lang_dict = TRANSLATIONS.get(target_language, {})
    lower_text = text.lower().strip()
    if lower_text in lang_dict:
        return lang_dict[lower_text]

    result = text
    for phrase, translation in lang_dict.items():
        if phrase in lower_text:
            idx = lower_text.find(phrase)
            original = text[idx:idx + len(phrase)]
            result = result.replace(original, translation, 1)

    return result


@router.post("/translate", response_model=TranslateResponse)
async def translate(body: TranslateRequest):
    target = body.target_language.lower()
    if target not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language. Supported: {', '.join(LANGUAGES)}")

    translated = await translate_with_llm(body.text, target)
    if translated is None:
        translated = translate_with_dict(body.text, target)

    return TranslateResponse(
        translated_text=translated,
        source_language="english",
        target_language=target,
    )
