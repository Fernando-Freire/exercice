from typing import Optional

import mlflow.pyfunc
import nltk.stem
from gensim.utils import simple_preprocess

mlflow.set_tracking_uri("http://mlflow_server:5000")

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Product(BaseModel):
    title: str
    concatenated_tags: str


class Products(BaseModel):
    products: list[Product]


nltk.download("rslp")

app = FastAPI()

stemmer = nltk.stem.RSLPStemmer()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# Post route for product categorization
@app.post("/category/{model_type}", status_code=200)
async def get_category(model_type: str, products: Products):
    implemented_model_types = ["tfidf", "bow", "Word2Vec", "Doc2Vec"]
    if model_type not in implemented_model_types:
        raise HTTPException(status_code=404, detail="Model Type Not Impllemented")

    ## Registered model names : "model_type"+"category"
    category_list = [
        "Bebê",
        "Bijuterias e Jóias",
        "Decoração",
        "Lembrancinhas",
        "Outros",
        "Papel e Cia",
    ]

    model_name_prefix = model_type + "-DecisionTreeClass-"

    print(products.dict()["products"])
    text = []
    title = []
    for item in products.dict()["products"]:
        text.append(item["title"] + " " + item["concatenated_tags"])
        title.append(item["title"])

    print(text)

    df = pd.DataFrame(text, columns=["text"])

    df["tokenized_text"] = [simple_preprocess(line, deacc=True) for line in df["text"]]
    df["stemmed_tokens"] = [
        [stemmer.stem(word) for word in tokens] for tokens in df["tokenized_text"]
    ]

    product_category = pd.DataFrame(title, columns=["Product"])
    for category in category_list:
        model_name = model_name_prefix + category
        print("model_name is " + model_name)
        model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/Production")

        result = model.predict(df)

        product_category[category] = [x == 1 for x in result]

    return {"categories": product_category}
