from typing import Optional

import gensim
import mlflow.pyfunc
import nltk.stem
from gensim import corpora
from gensim.utils import simple_preprocess
from mlflow.tracking import MlflowClient

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
        raise HTTPException(status_code=404, detail="Model Type Not Implemented")

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

    text = []
    title = []
    for item in products.dict()["products"]:
        text.append(item["title"] + " " + item["concatenated_tags"])
        title.append(item["title"])

    df = pd.DataFrame(text, columns=["text"])

    df["tokenized_text"] = [simple_preprocess(line, deacc=True) for line in df["text"]]
    df["stemmed_tokens"] = [
        [stemmer.stem(word) for word in tokens] for tokens in df["tokenized_text"]
    ]

    product_category = pd.DataFrame(title, columns=["Product"])
    product_category.set_index("Product")
    for category in category_list:
        model_name = model_name_prefix + category
        model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/Production")
        name_file = "my_dict_" + model_type + ".txt"
        dict = MlflowClient().download_artifacts(model.metadata.run_id, name_file)
        mydict = corpora.Dictionary.load_from_text(dict)
        test_features = []
        for index, row in df.iterrows():
            # Converting the tokens into the formet that the model requires
            features = gensim.matutils.corpus2csc(
                [mydict.doc2bow(row["stemmed_tokens"])], num_terms=len(mydict)
            ).toarray()[:, 0]
            test_features.append(features)

        result = model.predict(test_features)

        # product_category[category] = [x == 1 for x in result]
        product_category[category] = result

    print(product_category)
    response = []
    for index, row in product_category.iterrows():
        categories_of_product = []
        product_name = row[0]
        for i in range(1, 7):
            if row[i] == 1:
                categories_of_product.append(product_category.columns[i])
        response.append({product_name: categories_of_product})
    return {"categories": response}
