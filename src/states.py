from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.messages import BaseMessage

# Define Product Model
class Product(BaseModel):
    name: str
    quantity: int
    price: float

# Define State Model
class State(BaseModel):
    query: Optional[str]
    cart: List[Product] = []
    messages: List[BaseMessage] = []

# Initialize StateGraph
graph = StateGraph(State)
