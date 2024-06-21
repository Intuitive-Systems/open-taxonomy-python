from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from .Node import Node
from .Attribute import Attribute

# A Relationship is a generic base object that represents an edge between two Nodes in a Object Graph Model (OGM).
# Relationships have a cardinality of either one-to-one or one-to-many.
# Relationships have a direction of either incoming or outgoing.
# Relationships have a source Node and a target Node.

class RelationshipCardinality(Enum): 
    ONE_TO_ONE = "ZERO_OR_ONE"
    ONE_TO_MANY = "ONE_OR_MORE"

class RelationshipDirection(Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"

class Relationship(BaseModel):
    # The unique identifier for the relationship.
    id: str = Field(..., description="The unique identifier for the relationship.")
    # The name of the Relationship Type.
    type: str = Field(..., description="The name of the relationship type.")
    # The cardinality of the relationship.
    cardinality: RelationshipCardinality = Field(..., description="The cardinality of the relationship.")
    # The direction of the relationship.
    direction: RelationshipDirection = Field(..., description="The direction of the relationship.")
    # The source Node of the relationship.
    source: Node = Field(Node, description="The source node of the relationship.")
    # The target Node of the relationship.
    target: Node = Field(Node, description="The target node of the relationship.")