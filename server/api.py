from typing import Optional
import pickle
import pandas as pd
import os
from pydantic import BaseModel
from fastapi import FastAPI

class Product(BaseModel):
    title: str
    concatenated_tags: str

class Products(BaseModel):
    products: list[Product]

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# Post route for product categorization
@app.post("/category")
async def get_category(products: Products):
    model = os.getenv("MODEL_PATH")
    print(products)

    with open(model, "rb") as f:
        text_clf = pickle.load(f)

    df = pd.DataFrame(products_list)
    df["text"] = df["concatenated_tags"] + " " + df["title"]
    df = df.fillna(" ")
    categories_list = text_clf.predict(df["text"])
    return  {"categories": categories_list.tolist()}
