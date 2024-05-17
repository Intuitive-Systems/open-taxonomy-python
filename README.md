# Open Taxonomy Project

## Overview
The Open Taxonomy Project is designed to provide a structured and hierarchical classification of entities, such as products or services, using a taxonomy tree. This project includes tools for creating, managing, and querying taxonomy trees, making it easier to classify and retrieve information in a structured manner. It is particularly designed to be integrated with Large Language Models (LLMs), allowing them to interact with and create their own taxonomies.

## Features
- **Taxonomy Node Management**: Create and manage nodes within the taxonomy tree, each representing a category or classification.
- **Tree Operations**: Perform operations like adding nodes, searching within the tree, and traversing the tree to understand its structure.
- **Asynchronous Data Loading**: Load taxonomy data asynchronously from a remote JSON source.
- **Search and Classification**: Utilize natural language processing to classify entries and search within the taxonomy based on a query.
- **LLM Integration**: Enable Large Language Models to interact with and create taxonomies, making it easier for AI agents to understand and use the classification structure.

## Modules
- `TaxonomyNode`: Represents a node in the taxonomy tree.
- `TaxonomyTree`: Manages the overall structure and operations within the taxonomy tree.
- `utils`: Contains utility functions including asynchronous checks for node relevance using AI models.

## Installation
To install the Open Taxonomy Project, clone the repository and install the necessary dependencies using pip:

```sh
git clone https://github.com/intuitive-Systems/open-taxonomy.git
cd open-taxonomy
pip install -r requirements.txt
```

## Usage
To use this project, ensure you have Python installed. You can interact with the taxonomy tree by importing the classes and functions from the `open_taxonomy` package.

### Example
Here's a quick example of how to create a taxonomy node and add it to the tree:

```python
from open_taxonomy import TaxonomyNode, TaxonomyTree

# Create a new taxonomy node
node = TaxonomyNode("1", "Electronics", 1, "Electronics", None, {})

# Initialize the taxonomy tree
tree = TaxonomyTree()

# Add the node to the tree
tree.add_node(node)

# Example of adding a child node
child_node = TaxonomyNode("1-1", "Laptops", 2, "Electronics > Laptops", "1", {})
tree.add_node(child_node, parent_id="1")

# Display the tree structure
print("Current Taxonomy Tree Structure:")
tree.traverse()

# Example of searching within the tree
search_results = tree.search("Find all nodes under 'Electronics'")
print("Search Results:")
print(search_results)
```

### Advanced Example with Asynchronous Data Loading and LLM Integration

```python
import os
import json
import asyncio
import urllib.request

from open_taxonomy import TaxonomyNode, TaxonomyTree, is_node_relevant

taxonomy_url = "https://raw.githubusercontent.com/intuitive-Systems/open-taxonomy/main/dist/taxonomy.json"

# Create an asynchronous function to load and test the taxonomy tree
async def load_and_test_taxonomy():
    # Initialize the taxonomy tree
    taxonomy_tree = TaxonomyTree()

    # Fetch the taxonomy data from the URL
    with urllib.request.urlopen(taxonomy_url) as response:
        taxonomy_data = json.loads(response.read().decode())

    # Load the taxonomy tree from the fetched data
    taxonomy_tree.from_dict(taxonomy_data)

    # Traverse the tree and print its structure
    print("Traversing the taxonomy tree:")
    taxonomy_tree.traverse()

    # Perform a search query on the taxonomy tree
    search_query = 'IBM Thinkpad T480 with 14" Full HD Display, 10th Gen Intel Core i7, 16GB RAM, 512GB SSD, Windows 10, 1 Year Warranty'
    results = await taxonomy_tree.search(search_query)

    # Print the search results
    print(f"\nSearch results for query '{search_query}':")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    # Call the asynchronous function to load and test the taxonomy using asyncio.run
    asyncio.run(load_and_test_taxonomy())
```

## Testing
To run the unit tests for the project, use the following command:

```sh
export OPENAI_API_KEY="your_openai_api_key"
python -m unittest discover tests
```

## Contributing
We welcome contributions! Please fork the repository and submit pull requests for any enhancements or bug fixes. Make sure to follow the contribution guidelines.

## License
Open Taxonomy Project is released under the MIT License. Feel free to explore, play, and build something awesome!

For more information, visit the [GitHub repository](https://github.com/intuitive-Systems/open-taxonomy).