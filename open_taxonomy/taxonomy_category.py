import json
from typing import List

from .taxonomy_attribute import TaxonomyAttribute

class AttributeReference:
    id: str
    name: str

class TaxonomyCategory:
    def __init__(self, id: str, name: str, description: str, level: int, full_name: str, parent_id: str, attributes: List[AttributeReference]):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.level: int = level
        self.full_name: str = full_name
        self.parent_id: str = parent_id
        self.attributes: List[AttributeReference] = attributes
        self.ancestors: List[TaxonomyCategory] = []
        self.children: List[TaxonomyCategory] = []

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "full_name": self.full_name,
            "parent_id": self.parent_id,
            "attributes": [AttributeReference(id=attr['id'], name=attr['name']) for attr in self.attributes],
            "ancestors": list(ancestor.id for ancestor in self.ancestors),
            "children": list(child.id for child in self.children)
        }

    @staticmethod
    def from_dict(data: dict):
        return TaxonomyCategory(
            data['id'],
            data['name'],
            data['description'],
            data['level'],
            data['full_name'],
            data['parent_id'],
            data['attributes']
        )
    
    def get_attributes(self):
        return self.attributes
