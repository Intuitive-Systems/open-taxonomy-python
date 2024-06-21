from pydantic import BaseModel, Field
from typing import List, Optional
from .Attribute import Attribute
from .Relationship import Relationship

# A Node is a generic base object that represents a node in a Object Graph Model (OGM).
# Nodes are the base objects that are connected to each other through Relationships.
# Nodes can be of any NodeType and can have any number of Attributes.
class Node(BaseModel):
    # The unique identifier for the node.
    id: str = Field(..., description="The unique identifier for the node.")
    # The name of the Node Type.
    type: str = Field(..., description="The name of the node type.")
    # The attributes of the node.
    attributes: Optional[List[Attribute]] = Field([], description="The attributes of the node.")
    # The relationships of the node.
    relationships: Optional[List[Relationship]] = Field([], description="The relationships of the node.")
