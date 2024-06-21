from pydantic import BaseModel, Field
from typing import List, Optional
from .Node import Node

# A Value is a generic base object that represents a discrete value of an Attribute.
# Values are the "value" part of a key-value pair that is associated with a Node.

class Value(Node):   
    # The unique identifier for the value.
    id: str = Field(..., description="The unique identifier for the value.") 
    # The name of the value.
    name: str = Field(..., description="The name of the value.")
    # The value of the value.
    value: str = Field(..., description="The value of the value.")
    