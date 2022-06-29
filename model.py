# Pydantic allows auto creation of JSON Schemas from models
from itertools import product
from pydantic import BaseModel

class item(BaseModel):
    product_name: str
    price: str
    discount: str
    img_url : str
    