from typing import Optional
import pickle
import json
import pandas as pd
import os


from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# Post route for product categorization
@app.post("/category")
async def get_category(request: Request):

    model = os.getenv("MODEL_PATH")

    try:
        prodct = json.loads(request.body)
    except ValueError:
        return await json.dumps({"status": 1, "info": "request failed."})

    if prodct.get("products") is None:
        return await jsonify({"error": "missing products field"})

    products_list = prodct.get("products")

    for t in products_list:
        if t.get("title") is None:
            return await jsonify({"error": "missing products title field"})

    with open(model, "rb") as f:
        text_clf = pickle.load(f)

    df = pd.DataFrame(products_list)
    df["text"] = df["concatenated_tags"] + " " + df["title"]
    df = df.fillna(" ")
    categories_list = text_clf.predict(df["text"])
    return await jsonify({"categories": categories_list.tolist()})
