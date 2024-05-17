import json
import asyncio 

from open_taxonomy.utils import is_node_relevant
from .taxonomy_node import TaxonomyNode

class TaxonomyTree:
    def __init__(self, root_name="Root"):
        self.root = TaxonomyNode("root", root_name, 0, root_name, None, [])
        self.nodes_by_id = {"root": self.root}

    def add_node(self, node):
        self.nodes_by_id[node.id] = node
        
        if node.level == 0:
            self.root.children.append(node)
            node.ancestors.append(self.root)
        elif node.parent_id in self.nodes_by_id:
            parent = self.nodes_by_id[node.parent_id]
            parent.children.append(node)
            node.ancestors = parent.ancestors + [parent]

    def get_node(self, node_id):
        return self.nodes_by_id[node_id]

    def from_dict(self, data):
        version = data['version']
        verticals = data['verticals']
        all_nodes = []
        for vertical in verticals:
            for category in vertical['categories']:
                node = TaxonomyNode.from_dict(category, self.nodes_by_id)
                all_nodes.append(node)
        
        for node in all_nodes:
            node_data = next((category for vertical in verticals for category in vertical['categories'] if category['id'] == node.id), None)
            if node_data:
                node.children = [self.nodes_by_id.get(child_id['id']) for child_id in node_data.get('children', [])]
                node.ancestors = [self.nodes_by_id.get(ancestor_id['id']) for ancestor_id in node_data.get('ancestors', [])]
                node.children = [child for child in node.children if child is not None]
                node.ancestors = [ancestor for ancestor in node.ancestors if ancestor is not None]
                self.add_node(node)
        print(f"Loaded {len(self.nodes_by_id)} nodes.")

    def load_from_file(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.from_dict(data)

    def traverse(self, node=None, depth=0):
        if node is None:
            if depth > 0: 
                return
            node = self.root
        print(f"{'  ' * depth}{node.name} (ID: {node.id}, Level: {node.level})")
        print(f"Node has {len(node.children)} children.")
        for child in node.children:
            if child:
                print(f"Traversing child {child.id}")
                self.traverse(child, depth + 1)
            else: 
                print(f"Child node {child} not found.")

    async def search_sync(self, query, node=None, path=[], depth=0, parent_relevant=True):
        results = []
        if node is None:
            node = self.root

        stack = [(node, path, parent_relevant)]
        visited_nodes = set()

        while stack:
            current_node, current_path, parent_relevant = stack.pop(0)
            current_path = current_path + [current_node.name]
            print(f"{depth * '  '}Visiting {current_node.name} (path: {current_path})")

            if not parent_relevant or current_node in visited_nodes:
                continue

            visited_nodes.add(current_node)

            if current_node.id == "root":
                is_relevant = True
            else:
                payload = await is_node_relevant(query, current_node.name)
                is_relevant = payload["message"] == "TRUE" and payload["confidence"] > 0.5

            if is_relevant:
                if current_node.children:
                    stack = [(child, current_path, True) for child in current_node.children] + stack
                else:
                    results.append({
                        "node": current_node.to_dict(),
                        "path": current_path
                    })
            else:
                stack = [(child, current_path, False) for child in current_node.children] + stack

        return results
    
    async def search(self, query, node=None, path=[], depth=0, parent_relevant=True, bail_on_first_result=True):
        results = []
        if node is None:
            node = self.root

        stack = [(node, path, parent_relevant)]
        while stack:
            if bail_on_first_result and len(results) > 0:
                break
            current_node, current_path, parent_relevant = stack.pop()
            current_path = current_path + [current_node.name]
            print(f"{depth * '  '}Visiting {current_node.name} (path: {current_path})")

            if not parent_relevant:
                continue

            if current_node.id == "root":
                is_relevant = True
                child_nodes = current_node.children
            else:
                payload = await is_node_relevant(query, current_node.name)
                is_relevant = payload["message"] == "TRUE" and payload["confidence"] > 0.7
                child_nodes = current_node.children if is_relevant else []

            if is_relevant:
                if child_nodes:
                    # Collect relevance check tasks for child nodes
                    tasks = [
                        self._check_node_relevance(query, child, current_path)
                        for child in child_nodes
                    ]

                    # Run relevance checks concurrently in pairs
                    pairs = [tasks[i:i + 3] for i in range(0, len(tasks), 3)]
                    for pair in pairs:
                        stack.extend(await asyncio.gather(*pair))
                else:
                    results.append({
                        "node": current_node.to_dict(),
                        "path": current_path
                    })

        return results

    async def _check_node_relevance(self, query, child, current_path):
        payload = await is_node_relevant(query, child.name)
        is_relevant = payload["message"] == "TRUE" and payload["confidence"] > 0.6
        print(f"Visiting {child.name} (path: {current_path}) -- Is Relevant: {payload['message']}, {payload['confidence']}")
        if is_relevant:
            return child, current_path, True
        else:
            return child, current_path, False
