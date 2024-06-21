from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from ..base.Node import Node
from ..base.Relationship import Relationship, RelationshipCardinality, RelationshipDirection
from ..base.Attribute import Attribute








# A Tree is a generic base object that represents a tree structure that contains TreeNodes. 
# Trees are the top-level object that contains all of the nodes and relationships in a downstream use-case like a Taxonomy.
# Trees can be searched, traversed, and manipulated to find specific nodes and relationships.
# Trees can be serialized and deserialized to and from JSON.
# TreeNodes are special nodes that contain internal references to the tree structure to facilitate traversal and manipulation.

class Tree(BaseModel):
    # The unique identifier for the tree.
    id: str = Field(..., description="The unique identifier for the tree.")
    # The name of the tree.
    name: str = Field(..., description="The name of the tree.")
    # The description of the tree.
    description: Optional[str] = Field(None, description="The description of the tree.")
    # The root node of the tree.
    root: TreeNode = Field(..., description="The root node of the tree.")
    # The nodes of the tree.
    nodes: Optional[List[TreeNode]] = Field([], description="The nodes of the tree.")
    # The relationships of the tree.
    relationships: Optional[List[TreeRelationship]] = Field([], description="The relationships of the tree.")


# A TreeNode inherits from a Node and is a generic base object that represents a node in a Tree.
# TreeNodes are the base objects that are connected to each other through TreeRelationships.

class TreeNode(Node):
    # A private reference to the tree that the node belongs to.
    _tree: Tree = Field(..., description="The tree that the node belongs to.")

    # The unique identifier for the tree node.
    id: str = Field(..., description="The unique identifier for the tree node.")
    # The name of the Node Type.
    type: str = Field(..., description="The name of the node type.")
    # The parent node of the tree node.
    parent: Optional[TreeNode] = Field(None, description="The parent node of the tree node.")
    # The children nodes of the tree node.
    children: Optional[List[TreeNode]] = Field([], description="The children nodes of the tree node.")
    