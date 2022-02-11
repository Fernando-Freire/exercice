from fastapi import FastAPI
from fastapi.testclient import TestClient
from api import read_root
from api import get_category

app = FastAPI()

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello":"World"}


#def test_get_category():


