from pydantic import BaseModel, Field, validator
from typing import List, Optional
from .Node import Node
from .Value import Value

# An Attribute is a generic base object that represents an attribute of a Node.
# Attributes are key-value pairs that are associated with a Node.
# A Node can have any number of Attributes, and each Attribute can have any number of Values.
class Attribute(Node):
    # The unique identifier for the attribute.
    id: str = Field(..., description="The unique identifier for the attribute.")
    # The name of the attribute.
    name: str = Field(..., description="The name of the attribute.")
    # The description of the attribute.
    description: Optional[str] = Field(None, description="The description of the attribute.")
    # The possible values for the attribute.
    values: Optional[List[Value]] = Field([], description="The values of the attribute.")
    # The value of the attribute.
    value: Optional[str] = Field(None, description="The value of the attribute.")

    # TODO: A Validator for the value field -- the value must be one of the values in the values field.