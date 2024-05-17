import os
import json
import asyncio
import urllib.request

from open_taxonomy import TaxonomyNode, TaxonomyTree, is_node_relevant

taxonomy_url = "https://raw.githubusercontent.com/Intuitive-Systems/open-taxonomy/main/dist/taxonomy.json"

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
