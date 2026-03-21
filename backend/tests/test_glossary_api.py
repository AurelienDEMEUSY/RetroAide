from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.routers.glossary.explain_term")
def test_post_glossary_returns_explanation(mock_explain) -> None:
    mock_explain.return_value = (
        "Un trimestre est une période de cotisation retraite, environ trois mois."
    )
    response = client.post("/api/v1/glossary", json={"term": "trimestre"})
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert len(data["explanation"]) > 0
    assert "trimestre" in data["explanation"].lower() or "cotisation" in data["explanation"].lower()
    mock_explain.assert_called_once_with("trimestre")


def test_post_glossary_validation_empty_term() -> None:
    response = client.post("/api/v1/glossary", json={"term": ""})
    assert response.status_code == 422
