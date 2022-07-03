# Pydantic allows auto creation of JSON Schemas from models
from itertools import product
from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    product_name: str
    price: str
    unit: str
    discount: str
    img_url : str

class Subscription(BaseModel):
    email: str
    product_name: str
    price: Optional[str] = None
    unit: Optional[str] = None
    discount: Optional[str] = None
    img_url : Optional[str] = None