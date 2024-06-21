import json
import asyncio
from textwrap import dedent

import instructor
from openai import OpenAI 

from open_taxonomy.utils import is_node_relevant
from .taxonomy_category import TaxonomyCategory
from .taxonomy_attribute import TaxonomyAttribute, TaxonomyValue

from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, List, Optional


# All Products have the following attributes, on top of the ones fetched from the taxonomy tree:
# - Product Name
# - Manufacturer
# - Description
# - Brand
# - Manufacturer Product Number
# The attributes fetched from the taxonomy tree are added to the model dynamically in the attributes field


class TaxonomyTree:
    def __init__(self, root_name="Root"):
        self.root = TaxonomyCategory("root", root_name, "The Root Category", 0, root_name, None, [])
        self.categories_by_id: Dict[str, TaxonomyCategory] = {"root": self.root}
        self.attributes_by_id: Dict[str, TaxonomyAttribute] = {}

    def add_category(self, node) -> TaxonomyCategory:
        # Category Checks: 
        # 1. If a different node with the same ID is in the tree, raise an error
        # 2. If the parent node is not in the tree, raise an error
        if node.id in self.categories_by_id:
            raise ValueError(f"Node with ID {node.id} already exists in the tree.")
        elif node.parent_id not in self.categories_by_id and node.level > 0:
            raise ValueError(f"Parent node with ID {node.parent_id} not found in the tree.")
       
        # Attributes Checks (for each node attribute):
        # 1. If a different attribute with the same ID is in the tree, raise an error
        # 2. If the attribute is not in the tree, add it
        # for attribute in node.attributes:
        #     if attribute["id"] in self.attributes_by_id:
        #         continue
        #         # raise ValueError(f"Attribute with ID {attribute['id']} already exists in the tree.")
        #     else:
        #         self.attributes_by_id[attribute["id"]] = attribute
    
        self.categories_by_id[node.id] = node
        
        if node.level == 0:
            self.root.children.append(node)
            node.ancestors.append(self.root)
        elif node.parent_id in self.categories_by_id:
            parent = self.categories_by_id[node.parent_id]
            parent.children.append(node)
            node.ancestors = parent.ancestors + [parent]

    def add_category_attributes(self, node_id: str, attributes: List[TaxonomyAttribute]):
        node = self.categories_by_id[node_id]
        node.attributes = attributes
        for attribute in attributes:
            if attribute.id in self.attributes_by_id and self.attributes_by_id[attribute.id] == attribute:
                continue
            elif attribute.id in self.attributes_by_id:
                raise ValueError(f"Attribute with ID {attribute.id} already exists in the tree.")
            else:
                self.attributes_by_id[attribute.id] = attribute

    def get_category(self, node_id):
        return self.categories_by_id[node_id]

    def categories_from_dict(self, data):
        version = data['version']
        verticals = data['verticals']
        all_nodes = []
        for vertical in verticals:
            for category in vertical['categories']:
                node = TaxonomyCategory.from_dict(category)
                all_nodes.append(node)
        
        for node in all_nodes:
            node_data = next((category for vertical in verticals for category in vertical['categories'] if category['id'] == node.id), None)
            if node_data:
                node.children = [self.categories_by_id.get(child_id['id']) for child_id in node_data.get('children', [])]
                node.ancestors = [self.categories_by_id.get(ancestor_id['id']) for ancestor_id in node_data.get('ancestors', [])]
                node.children = [child for child in node.children if child is not None]
                node.ancestors = [ancestor for ancestor in node.ancestors if ancestor is not None]
                self.add_category(node)
        print(f"Loaded {len(self.categories_by_id)} categories.")

    def attributes_from_dict(self, data):
        print(f"Loading {len(data['attributes'])} attributes.")
        for attribute in data['attributes']:
            attribute_obj = TaxonomyAttribute.from_dict(attribute)
            self.attributes_by_id[attribute_obj.id] = attribute_obj
        print(f"Loaded {len(self.attributes_by_id)} attributes.") 

    def get_attribute(self, attribute_id):
        return self.attributes_by_id[attribute_id]
    
    def add_attribute(self, attribute: TaxonomyAttribute):
        self.attributes_by_id[attribute.id] = attribute

    def from_dict(self, taxonomy_data: Dict[str, Any], attribute_data: Dict[str, Any]):
        self.categories_from_dict(taxonomy_data)
        self.attributes_from_dict(attribute_data)
        

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
                payload = await is_node_relevant(query, current_node.full_name, current_node.description)
                is_relevant = payload["message"] == "TRUE" and payload["confidence"] > 0.5

            if is_relevant:
                if current_node.children:
                    stack = [(child, current_path, True) for child in current_node.children] + stack
                else:
                    results.append({
                        "node": current_node.to_dict(),
                        "path": current_path,
                        "confidence": payload["confidence"]
                    })
            else:
                stack = [(child, current_path, False) for child in current_node.children] + stack
        # return results sorted
        return results
    
    async def search(self, query, node=None, path=[], depth=0, parent_relevant=True, bail_on_first_result=False, confidence_threshold=0.6):
        results = []
        if node is None:
            node = self.root

        stack = [(node, path, parent_relevant, 1)]
        while stack:
            if bail_on_first_result and len(results) > 0:
                break
            current_node, current_path, parent_relevant, confidence = stack.pop()
            current_path = current_path + [current_node.name]
            print(f"{depth * '  '}Visiting {current_node.name} (path: {current_path})")

            if not parent_relevant:
                continue

            if current_node.id == "root":
                is_relevant = True
                child_nodes = current_node.children
            else:
                payload = await is_node_relevant(query, current_node.full_name, current_node.description)
                is_relevant = payload["message"] == "TRUE" and payload["confidence"] > confidence_threshold
                child_nodes = current_node.children if is_relevant else []

            if is_relevant:
                if child_nodes:
                    # Collect relevance check tasks for child nodes
                    tasks = [
                        self._check_node_relevance(query, child, current_path, confidence_threshold)
                        for child in child_nodes
                    ]

                    # Run relevance checks concurrently in pairs
                    pairs = [tasks[i:i + 3] for i in range(0, len(tasks), 3)]
                    for pair in pairs:
                        stack.extend(await asyncio.gather(*pair))
                else:
                    results.append({
                        "node": current_node,
                        "path": current_path,
                        "confidence": confidence
                    })
        # return results sorted by confidence
        return sorted(results, key=lambda x: x["confidence"], reverse=True)
    
    async def _check_node_relevance(self, query, child, current_path, confidence_threshold):
        payload = await is_node_relevant(query, child.full_name, child.description)
        is_relevant = payload["message"] == "TRUE" and payload["confidence"] > confidence_threshold
        print(f"Visiting {child.name} (path: {current_path}) -- Is Relevant: {payload['message']}, {payload['confidence']}")
        if is_relevant:
            return child, current_path, True, payload["confidence"]
        else:
            return child, current_path, False, payload["confidence"]

    # a method to select one or more child nodes to explore based on the current node
    # 1. extract the names from each of the children and create a prompt
    # 2. Use instructor to ask the LLM to select one or more children to explore
    # 3. Recursively explore the children
    # 4. if there are no children to retrieve, return the current node
    # returns: a list of selected leaf nodes
    def explore_children(self, query, node: TaxonomyCategory = None) -> List[TaxonomyCategory]:
        if node is None:
            node = self.root 
        client = instructor.from_openai(OpenAI()) #mode=instructor.function_calls.Mode.JSON)
        children = node.children

        # base case
        if not children:
            return [node]

        class SelectedChildren(BaseModel):
            children: list[str] = []

        print(f"Currently considering {len(children)} children of {node.name} at depth {node.level}")

        instructions = dedent(f"""\
        You are classifying a single product against a hierarchical taxonomy tree. We are examining the children of a taxonomy node to determine if they improve the classification of a product description.
        Given a product description and a list of children nodes in the taxonomy, you need to decide which children explicitly *improve* the classification of the product description.
        Select the children nodes that will improve the classification of the product description if they are selected.
                              
        It is preferred to select no children than to select irrelevant children. To do so return the empty list.""")

        prompt = dedent(f"""\
        Product Description: 
        ---
        {query}
        ---
        
        Current Node: {node.name}
        Children: {", ".join(child.name for child in children)}
        Select the children nodes that are relevant to the product description.
        """)


        selected_children = client.chat.completions.create(
            model="gpt-4-turbo",
            response_model=SelectedChildren,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.1,
        )

        print(f"Selected Children: \n{selected_children}")

        # locate each of the selected children nodes and explore them
        selected_nodes = []
        for child in selected_children.children:
            selected_node = next((c for c in children if c.name == child), None)
            if selected_node:
                relevant_children = self.explore_children(query, selected_node)
                selected_nodes.extend(relevant_children)
        return selected_nodes
            

    def create_product_model(self, category_id: str, static_fields: Dict[str, Any] = {}, include_attributes=True):
        node = self.categories_by_id[category_id]
        attributes = node.attributes

        if not attributes:
            raise ValueError(f"Node {node.name} has no attributes.")
        
        if static_fields == {}:
            # Define static fields
            static_fields = {
                "ProductName": (str, Field(..., title="The official Manufacturer-assigned name, including any special characters or symbols.")),
                "SearchName": (str, Field(None, title="A Normalized version of the ProductName for search purposes.")),
                "Manufacturer": (str, Field(..., title="Manufacturer")),
                "ProductFamily": (str, Field(None, title="Product Family as defined by the manufacturer, including any special characters or symbols")),
                "SearchFamily": (str, Field(None, title="Normalized version of the ProductFamily for search purposes, without special characters or symbols")),
                "ProductLine": (str, Field(..., title="Product Sub-Family or Sub-Category as defined by the manufacturer")),
                "SearchLine": (str, Field(None, title="Normalized version of the ProductLine for search purposes, without special characters or symbols")),
                "ProductModel": (str, Field(None, title="Product Model number as defined by our own format. Ryzen 3 3200U would be R3-3200U and Ryzen 9 PRO 7940HS would be R9-PRO-7940HS")),
                "Description": (str, Field(..., title="Succinct and Brief Description of the product.")),
                # List of manufacturer part numbers
                "ManufacturerPartNumbers": (List[str], Field(None, title="Manufacturer Part Numbers")),
            }

        resolved_attributes = []
        if include_attributes:
            for attr in attributes:
                # print(f"Resolving attribute {attr['id']}")
                attribute = self.attributes_by_id[attr['id']]
                resolved_attributes.append(attribute)
                # print(json.dumps(attribute.to_dict(), indent=2))

        # Define the attributes field
        dynamic_fields = {
            attr.name: (str, Field(..., title=attr.name, examples=[value.name for value in attr.values] + ["Other"]))
            for attr in resolved_attributes
        }

        # Create a model for the attributes field
        AttributesModel = create_model('Attributes', **dynamic_fields)

        # Add the attributes field to the static fields
        static_fields["attributes"] = (AttributesModel, Field(default_factory=AttributesModel))

        # Create the main product model
        product_model = create_model('Product', **static_fields)

        # Print JSON representation of the schema
        # print(product_model.schema_json(indent=2))

        return product_model

    # a method that takes an unstructured product description and a node, and returns a Product with the appropriate attributes
    # it first creates a pydantic model with the attributes of the node
    # it then uses the product description to enrich the product with instructor
    def enrich_product(self, product_description: str, node: TaxonomyCategory, static_fields: Dict[str, Any] = {}, include_attributes=True, model_name="gpt-4o", max_retries=2):
        client = instructor.from_openai(OpenAI(max_retries=max_retries), mode=instructor.function_calls.Mode.JSON_SCHEMA)

        # resolve the node's attributes
        attributes = []
        for attr in node.attributes:
            attribute = self.attributes_by_id[attr['id']]
            attributes.append(attribute.to_dict())

        # print(f"Node Attributes: \n{json.dumps(attributes, indent=2)}")
        # Create a Pydantic model based on the node's attributes
        ProductModel = self.create_product_model(node.id, static_fields, include_attributes)
       
        print("About to call instructor to enrich the product.")
        product = client.chat.completions.create(
            model=model_name,
            response_model=List[ProductModel],
            max_retries=max_retries,
            messages=[
                # {"role": "system", "content": "You are a helpful assistant that reads relevant information from a product description and fills out a product model with the extracted information. Return exactly one product."},
                {"role": "user", "content": f"Product Information:\n\n{product_description}"}
            ],
            temperature=0.1,
            max_tokens=2048,
        )

        return product
        
        
# def enrich_product(self, product_description: str, node: TaxonomyCategory, static_fields: Dict[str, Any] = {}):
#         # client = instructor.from_openai(OpenAI(base_url="https://api.openai.com/v1"))#, mode=instructor.function_calls.Mode.JSON)
#         # client = instructor.from_openai(OpenAI(base_url="https://bigthink.dev.teachprotege.ai/v1/"), mode=instructor.function_calls.Mode.MD_JSON)
#         client = OpenAI()

#         # resolve the node's attributes
#         attributes = []
#         for attr in node.attributes:
#             attribute = self.attributes_by_id[attr['id']]
#             attributes.append(attribute.to_dict())

#         # print(f"Node Attributes: \n{json.dumps(attributes, indent=2)}")
#         # Create a Pydantic model based on the node's attributes
#         ProductModel = self.create_product_model(node.id, static_fields)
#         # print(f"Created Product Model: {ProductModel.schema_json(indent=2)}")

#         instructions = dedent(f"""\
#         As a genius expert, your task is to understand the content and provide the parsed objects in json that match the following json_schema:
#         {json.dumps(ProductModel.model_json_schema(), indent=2)}
#         Make sure to return an instance of the JSON, not the schema itself
#         """)

#         prompt = dedent(f"""\
#         Content:
#         {product_description}
#         Return the correct JSON response that matches the schema:
#         """)
#         messages = [
#             {"role": "system", "content": instructions},
#             {"role": "user", "content": prompt}
#         ]
#         response = client.chat.completions.create(
#             model="vllm",
#             messages=messages,
#             temperature=0.1 
#         )
#         print(f"Messages: {json.dumps(messages, indent=2)}")
#         print(f"Response: {response.choices[0].message.content}")
#         json_response = json.loads(response.choices[0].message.content)

#         product = ProductModel.model_validate(json_response)

#         return product

    