import unittest
from open_taxonomy import TaxonomyNode, TaxonomyTree

class TestTaxonomy(unittest.TestCase):
    def test_node_creation(self):
        node = TaxonomyNode("1", "Test Node", 1, "Test Node", "root", [])
        self.assertEqual(node.name, "Test Node")

    def test_tree_creation(self):
        tree = TaxonomyTree()
        node = TaxonomyNode("1", "Test Node", 1, "Test Node", "root", [])
        tree.add_node(node)
        self.assertEqual(tree.get_node("1").name, "Test Node")

if __name__ == "__main__":
    unittest.main()
