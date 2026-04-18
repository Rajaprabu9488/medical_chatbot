import pytest
import image_to_text


# =========================
# TEST 1: Dependency Detection
# =========================
def test_dependency_detection(monkeypatch):

    def mock_detect_intent(text):
        return "symptom_description"

    class MockDoc:
        ents = []

    def mock_nlp(text):
        return MockDoc()

    monkeypatch.setattr("image_to_text.detect_intent", mock_detect_intent)
    monkeypatch.setattr("image_to_text.nlp", mock_nlp)

    result = image_to_text.detect_entity_and_intent("It is getting worse")

    assert "dependent convo" in result["conversation"]
    assert result["intent"] == ["symptom_description"]


# =========================
# TEST 2: Entity Detection
# =========================
def test_entity_detection(monkeypatch):

    def mock_detect_intent(text):
        return "disease_info"

    class MockEntity:
        def __init__(self, label):
            self.label_ = label

    class MockDoc:
        ents = [MockEntity("DISEASE")]

    def mock_nlp(text):
        return MockDoc()

    monkeypatch.setattr("image_to_text.detect_intent", mock_detect_intent)
    monkeypatch.setattr("image_to_text.nlp", mock_nlp)

    result = image_to_text.detect_entity_and_intent("I have fever")

    assert "DISEASE" in result["conversation"]
    assert result["intent"] == ["disease_info"]


# =========================
# TEST 3: Intent Detection
# =========================
def test_detect_intent(monkeypatch):

    class MockModel:
        def encode(self, text):
            return text

    def mock_cos_sim(a, b):
        return 1.0 if a == b else 0.1

    monkeypatch.setattr("image_to_text.intent_model", MockModel())
    monkeypatch.setattr(
        "image_to_text.util",
        type("MockUtil", (), {"cos_sim": mock_cos_sim})
    )

    image_to_text.intent_vectors = {
        "symptom_description": ["I have fever"],
        "non_medical": ["how to cook rice"]
    }

    result = image_to_text.detect_intent("I have fever")

    assert result == "symptom_description"


# =========================
# TEST 4: Non-Medical Intent
# =========================
def test_non_medical(monkeypatch):

    class MockModel:
        def encode(self, text):
            return text

    def mock_cos_sim(a, b):
        return 1.0 if "cook" in a else 0.1

    monkeypatch.setattr("image_to_text.intent_model", MockModel())
    monkeypatch.setattr(
        "image_to_text.util",
        type("MockUtil", (), {"cos_sim": mock_cos_sim})
    )

    image_to_text.intent_vectors = {
        "non_medical": ["how to cook rice"],
        "symptom_description": ["I have fever"]
    }

    result = image_to_text.detect_intent("how to cook food")

    assert result == "non_medical"


# =========================
# TEST 5: Full Pipeline
# =========================
def test_full_pipeline(monkeypatch):

    def mock_detect_intent(text):
        return "symptom_description"

    class MockEntity:
        def __init__(self, label):
            self.label_ = label

    class MockDoc:
        ents = [MockEntity("SYMPTOM")]

    def mock_nlp(text):
        return MockDoc()

    monkeypatch.setattr("image_to_text.detect_intent", mock_detect_intent)
    monkeypatch.setattr("image_to_text.nlp", mock_nlp)

    result = image_to_text.detect_entity_and_intent("I have fever and it is bad")

    assert "dependent convo" in result["conversation"]
    assert "SYMPTOM" in result["conversation"]
    assert result["intent"] == ["symptom_description"]