import json

class TaxonomyNode:
    def __init__(self, id, name, level, full_name, parent_id, attributes):
        self.id = id
        self.name = name
        self.level = level
        self.full_name = full_name
        self.parent_id = parent_id
        self.attributes = attributes
        self.ancestors = []
        self.children = []

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "full_name": self.full_name,
            "parent_id": self.parent_id,
            "attributes": self.attributes,
            "ancestors": [ancestor.id for ancestor in self.ancestors],
            "children": [child.id for child in self.children]
        }

    @staticmethod
    def from_dict(data, nodes_by_id):
        return TaxonomyNode(
            data['id'],
            data['name'],
            data['level'],
            data['full_name'],
            data['parent_id'],
            data['attributes']
        )
