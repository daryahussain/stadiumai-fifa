from app.schemas.translation import LANGUAGES


class TestTranslationEndpoint:
    def test_translate_spanish(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "hello",
            "target_language": "spanish",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"].lower() == "hola"
        assert data["target_language"] == "spanish"
        assert data["source_language"] == "english"

    def test_translate_french(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "restroom",
            "target_language": "french",
        })
        assert response.status_code == 200
        assert response.json()["translated_text"].lower() == "toilettes"

    def test_translate_arabic(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "welcome",
            "target_language": "arabic",
        })
        assert response.status_code == 200
        assert response.json()["translated_text"] == "أهلا وسهلا"

    def test_translate_hindi(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "emergency",
            "target_language": "hindi",
        })
        assert response.status_code == 200
        assert "आपातकाल" in response.json()["translated_text"]

    def test_translate_unknown_phrase(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "something unknown here",
            "target_language": "spanish",
        })
        assert response.status_code == 200
        assert response.json()["translated_text"] == "something unknown here"

    def test_translate_invalid_language(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "hello",
            "target_language": "german",
        })
        assert response.status_code == 400

    def test_translate_phrase_substitution(self, client):
        response = client.post("/api/v1/translation/translate", json={
            "text": "where is my seat near gate?",
            "target_language": "spanish",
        })
        assert response.status_code == 200
        result = response.json()["translated_text"].lower()
        assert "dónde está mi asiento" in result

    def test_all_languages_supported(self):
        assert "english" in LANGUAGES
        assert "spanish" in LANGUAGES
        assert "french" in LANGUAGES
        assert "arabic" in LANGUAGES
        assert "hindi" in LANGUAGES
        assert len(LANGUAGES) == 5
