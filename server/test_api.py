from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_get_category_wrong_model():
    data_json = {"products": [{"title": "string", "concatenated_tags": "string"}]}
    response = client.post("/category/dingding", data_json)
    assert response.status_code == 404
    assert response.json()["detail"] == "Model Type Not Impllemented"


def test_get_category_wrong_fields():
    data_json = {
        "products": [
            {
                "title": "Cinto de Artes Marciais",
                "concatenated_tags": "cinto artes-marciais roupa tecido",
            },
            {"title": "Carrinho de Bebê", "km": "10000"},
            {"concatenated_tags": "Quadro de Parede", "preço": "3p"},
            {"cor": "FF2200", "preço": "3097"},
        ]
    }
    response = client.post("/category/bow", data_json)
    assert response.status_code == 404
    # assert len(response.json()["categories"]) == 2


def test_get_category_bow():
    __test_get_category("bow")


def test_get_category_tfidf():
    __test_get_category("tfidf")


def test_get_category_Word2Vec():
    __test_get_category("Word2Vec")


def test_get_category_Doc2Vec():
    __test_get_category("Doc2Vec")


def __test_get_category(model: str):
    data_json = {
        "products": [
            {
                "title": "Cinto de Artes Marciais",
                "concatenated_tags": "cinto artes-marciais roupa tecido",
            },
            {
                "title": "Quadro de plantas Tropicais",
                "concatenated_tags": "quadro parede moldura decoração",
            },
        ]
    }
    response = client.post("/category/{model}", data_json)
    assert response.status_code == 200
    categories = response.json()["categories"]
    assert len(categories) == 2
    assert categories[0] == {"Cinto de Artes Marciais": []}
    assert categories[1] == {"Quadro de plantas Tropicais": ["Decoração"]}
