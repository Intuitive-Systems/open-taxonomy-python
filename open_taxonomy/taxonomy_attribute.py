import json
from typing import Dict, List

class TaxonomyAttribute:
    def __init__(self, id: str, name: str, handle: str, description: str, extended_attributes: List[str], values: List[Dict[str, str]]):
        self.id: str = id
        self.name: str = name
        self.handle: str = handle
        self.description: str = description
        self.extended_attributes: List[str] = extended_attributes
        self.values: List[TaxonomyValue] = [TaxonomyValue.from_dict(value) for value in values] if values else []

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "handle": self.handle,
            "description": self.description,
            "extended_attributes": self.extended_attributes,
            "values": [value.to_dict() for value in self.values]
        }

    @staticmethod
    def from_dict(data):
        return TaxonomyAttribute(
            data['id'],
            data['name'],
            data['handle'],
            data.get('description', ''),
            data.get('extended_attributes', []),
            data.get('values', [])
        )


class TaxonomyValue:
    def __init__(self, id, name, handle):
        self.id = id
        self.name = name
        self.handle = handle

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "handle": self.handle
        }

    @staticmethod
    def from_dict(data):
        return TaxonomyValue(
            data['id'],
            data['name'],
            data['handle']
        )
