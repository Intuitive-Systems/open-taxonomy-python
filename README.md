# Goal 

To achieve an API like this: 

```python
# Desired API for the TaxonomyTree model (which sub-classes the Tree model): 

# First situation -- we want to classify the type of a product based on the open taxonomy product classification.
taxonomy_url = "https://raw.githubusercontent.com/Intuitive-Systems/open-taxonomy/main/dist/product-classification.json"

# Initialize the taxonomy
taxonomy = Taxonomy(url=taxonomy_url)

product_description = "Thinkpad X1 Carbon (AMD) - 14\" FHD - AMD Ryzen 5 Pro 4650U - 8GB RAM - 256GB SSD - Windows 10 Pro - Black - 20U9001PUS"
# classification is a TaxonomyNode representing the classification of the product description.
classification = taxonomy.classify(product_description)
# you can query its parent
parents = classification.parent
# you can query its children
children = classification.children
# Product is a Product() representing the product description, extracted with an LLM. 
product = taxonomy.enrich(product_description, classification)

# Second situation -- we want to manipulate the taxonomy tree to add/mutate categories, attributes, and values
# Initialize the taxonomy
taxonomy = Taxonomy(url=taxonomy_url)

# fetch a node from the taxonomy tree
node = taxonomy.get(id="gid://open-taxonomy/TaxonomyCategory/el-6-3")

# add a new attribute to the node
attribute = Attribute(id="gid://open-taxonomy/Attribute/el-6-3-1", name="CPU Family")
# this should throw an error if the attribute already exists in the tree (node contains an internal reference to the tree for state management)
node.add_attribute(attribute)

# add a new value to the attribute
value = Value(id="gid://open-taxonomy/Value/el-6-3-1-1", name="AMD Ryzen 5 Pro Processors")
attribute.add_value(value)

# add a new child node to the node
child = TaxonomyCategory(id="gid://open-taxonomy/TaxonomyCategory/el-6-3-1", name="AMD Ryzen 5 Pro Processors")
node.add_child(child)

```