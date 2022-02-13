from fastapi import FastAPI
from fastapi.testclient import TestClient
from api import app



client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello":"World"}


def test_get_category():
    data_json = {
            "products": [
                {
                    "title": "Cinto de Artes Marciais",
                    "concatenated_tags": "cinto artes-marciais roupa tecido",
                },
                {"title": "Carrinho de Bebê"},
            ]
        }
    response = client.post("/category", data_json)
    assert response.status_code == 200
    #assert len(response.json()["categories"]) == 2
