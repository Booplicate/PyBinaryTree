# pylint: disable=wrong-import-position
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
"""
Various tests for PyBinaryTree
"""


import sys
import pathlib
sys.path.insert(0, str(pathlib.Path.cwd() / "src"))
import json
import unittest

# from src import PyBinaryTree
from src.PyBinaryTree import (
    _Node,
    BinaryTree
)


class NodeTest(unittest.TestCase):
    TEST_VALUES = (
        "test value",
        895,
        (-95, ("hello world", 0.5))
    )
    NUM_NODES_TOTAL = 10
    NONEXISTING_VALUE = "null"

    def setUp(self):
        self.value_nodes_map = {v: _Node(v) for v in self.TEST_VALUES}
        self.num_nodes_map = {v: _Node(v) for v in range(self.NUM_NODES_TOTAL)}

        self.big_node = _Node(10**10)
        self.mid_node = _Node(1)
        self.small_node = _Node(-10**10)

    def tearDown(self):
        del self.value_nodes_map
        del self.num_nodes_map
        del self.big_node
        del self.mid_node
        del self.small_node

    def test_ordering_methods(self):
        with self.subTest("Testing == and !="):
            for v, n in self.value_nodes_map.items():
                self.assertEqual(n, _Node(v))
                self.assertNotEqual(n, _Node(self.NONEXISTING_VALUE))

        with self.subTest("Testing > and <"):
            self.assertGreater(self.big_node, self.mid_node)
            self.assertLess(self.small_node, self.mid_node)
            self.assertGreater(self.big_node, self.small_node)

        with self.subTest("Testing >= and <="):
            self.assertGreaterEqual(self.big_node, self.mid_node)
            self.assertLessEqual(self.small_node, self.mid_node)
            self.assertGreaterEqual(self.big_node, self.small_node)
            self.assertGreaterEqual(self.mid_node, self.mid_node)

    def test_hash(self):
        for v, n in self.value_nodes_map.items():
            self.assertEqual(hash(v), hash(n))

    def test_remove_child(self):
        lc = _Node(9001)
        rc = _Node("bruh")
        node = _Node("node value", left_child=lc, right_child=rc)

        self.assertIs(node.left_child, lc)
        self.assertIs(node.right_child, rc)

        self.assertFalse(
            node.remove_child(_Node(lc.value))
        )
        self.assertIsNotNone(node.left_child)
        self.assertIsNotNone(node.right_child)

        self.assertTrue(
            node.remove_child(lc)
        )
        self.assertIsNone(node.left_child)
        self.assertIsNotNone(node.right_child)

        self.assertTrue(
            node.remove_child(rc)
        )
        self.assertIsNone(node.right_child)
        self.assertIsNone(node.right_child)


class BinaryTreeTest(unittest.TestCase):
    TREE1_DATA = (3, 2, 0, 1, 4, 6, 5, 7, 8)
    TREE1_INORDER_DATA = tuple(sorted(TREE1_DATA))
    TREE1_INORDER_DATA_REVERSED = tuple(reversed(TREE1_INORDER_DATA))
    TREE1_PREORDER_DATA = (3, 2, 0, 1, 4, 6, 5, 7, 8)
    TREE1_PREORDER_DATA_REVERSED = (3, 4, 6, 7, 8, 5, 2, 0, 1)
    TREE1_POSTORDER_DATA = (1, 0, 2, 5, 8, 7, 6, 4, 3)
    TREE1_POSTORDER_DATA_REVERSED = (8, 7, 5, 6, 4, 1, 0, 2, 3)
    TREE1_BREADTHFIRST_DATA = (3, 2, 4, 0, 6, 1, 5, 7, 8)

    TREE2_DATA = (7, 8, 5, 11, 9, 10, 12, 3, 4, 0, 1, 2)

    TREE3_DATA_PATH = pathlib.Path.cwd() / "tests" / "fixtures" / "binary_tree_data_10k_values.json"

    def setUp(self):
        # pylint: disable-next=pointless-string-statement
        """
        tree1:
                        3
                    2       4
                0               6
                   1         5     7
                                     8
        """
        self.tree1 = BinaryTree()
        for i in self.TREE1_DATA:
            self.tree1.add(i)
        # pylint: disable-next=pointless-string-statement
        """
        tree2:
                            7
                        5       8
                     3             11
                   0   4          9  12
                    1           10
                     2
        """
        self.tree2 = BinaryTree(allow_dupes=False)
        for i in self.TREE2_DATA:
            self.tree2.add(i)

    def tearDown(self):
        del self.tree1
        del self.tree2

    def test_has_value(self):
        tree1 = self.tree1

        for i in self.TREE1_DATA:
            with self.subTest(f"Test 'has_value' for {i}"):
                self.assertTrue(tree1.has_value(i))

        for i in ("a", 10**10, ("test", "tuple")):
            with self.subTest(f"Test 'has_value' for {i}"):
                self.assertFalse(tree1.has_value(i))

        for i in self.TREE2_DATA:
            with self.subTest(f"Test 'has_value' for {i}"):
                if i in self.TREE1_DATA:
                    self.assertTrue(tree1.has_value(i))
                else:
                    self.assertFalse(tree1.has_value(i))

    def test_add_dupe(self):
        tree1 = self.tree1
        tree2 = self.tree2
        dupe_val = 3
        known_values = []

        def callback(node):
            known_values.append(node.value)

        self.assertTrue(tree1.has_value(dupe_val))
        self.assertTrue(tree2.has_value(dupe_val))

        with self.subTest("Can add dupe"):
            self.assertTrue(tree1.add(dupe_val))
            tree1.traverse_breadthfirst(callback)
            self.assertEqual(known_values.count(dupe_val), 2)

        known_values.clear()

        with self.subTest("Cannot add dupe"):
            self.assertFalse(tree2.add(dupe_val))
            tree2.traverse_breadthfirst(callback)
            self.assertEqual(known_values.count(dupe_val), 1)

    def test_add_root(self):
        # pylint: disable=protected-access
        tree = BinaryTree()

        self.assertIsNone(tree._root)

        tree.add("I'm a good coder"*99)

        self.assertIsNotNone(tree._root)
        self.assertIsNone(tree._root.left_child)
        self.assertIsNone(tree._root.right_child)
        self.assertIsNone(tree._root.parent)
        # pylint: enable=protected-access

    def test_add_to_root(self):
        # pylint: disable=protected-access
        tree = BinaryTree()

        root_value = 10
        tree.add(root_value)
        with self.subTest("Add as root"):
            self.assertEqual(tree._root.value, root_value)

        rc_value = 11
        tree.add(rc_value)
        with self.subTest("Add as the right child of the root"):
            self.assertIsNotNone(tree._root.right_child)
            self.assertEqual(tree._root.right_child.value, rc_value)

        tree.add(rc_value)# add dupe
        with self.subTest("Add as the right child of the right child of the root"):
            self.assertIsNotNone(tree._root.right_child.right_child)
            self.assertEqual(tree._root.right_child.right_child.value, rc_value)

        lc_value = 9
        tree.add(lc_value)
        with self.subTest("Add as the left child of the root"):
            self.assertIsNotNone(tree._root.left_child)
            self.assertEqual(tree._root.left_child.value, lc_value)

        # pylint: enable=protected-access

    def test_delete_root_no_children(self):
        tree = BinaryTree()
        root_value = 8305

        tree.add(root_value)
        self.assertTrue(tree.delete(root_value))
        self.assertFalse(tree.has_value(root_value))
        # pylint: disable-next=protected-access
        self.assertIsNone(tree._root)

    def test_delete_root_with_children(self):
        # pylint: disable=protected-access
        tree = BinaryTree()
        tree.add(-5)
        tree.add(-10)
        tree.add(0)

        self.assertEqual(tree._root.value, -5)

        tree.delete(-5)
        self.assertEqual(tree._root.value, 0)
        self.assertIsNone(tree._root.right_child)
        self.assertIsNotNone(tree._root.left_child)
        self.assertGreater(hash(tree._root), hash(tree._root.left_child))

        tree.delete(0)
        self.assertEqual(tree._root.value, -10)
        self.assertIsNone(tree._root.right_child)
        self.assertIsNone(tree._root.left_child)
        # pylint: enable=protected-access

    def test_traverse_callback(self):
        tree1 = self.tree1

        counter: int
        def callback(node):
            nonlocal counter

            counter += 1
            self.assertIsInstance(node, _Node)

        with self.subTest("Test inorder callback"):
            counter = 0
            tree1.traverse_inorder(callback)
            self.assertEqual(counter, len(self.TREE1_DATA))

        with self.subTest("Test preorder callback"):
            counter = 0
            tree1.traverse_preorder(callback)
            self.assertEqual(counter, len(self.TREE1_DATA))

        with self.subTest("Test postorder callback"):
            counter = 0
            tree1.traverse_postorder(callback)
            self.assertEqual(counter, len(self.TREE1_DATA))

    def test_traverse_inorder(self):
        tree1 = self.tree1
        traversed_node_values = []
        sorted_data = list(self.TREE1_INORDER_DATA)
        sorted_data_reversed = list(self.TREE1_INORDER_DATA_REVERSED)
        unsorted_data = list(self.TREE1_DATA)

        def callback(node):
            nonlocal traversed_node_values
            traversed_node_values.append(node.value)

        with self.subTest("Test inorder non-reversed"):
            tree1.traverse_inorder(callback)
            # the order should be the same
            self.assertEqual(traversed_node_values, sorted_data)
            self.assertNotEqual(traversed_node_values, unsorted_data)

        traversed_node_values.clear()

        with self.subTest("Test inorder reversed"):
            tree1.traverse_inorder(callback, reverse=True)
            # the order should be reversed
            self.assertEqual(traversed_node_values, sorted_data_reversed)
            self.assertNotEqual(traversed_node_values, sorted_data)
            self.assertNotEqual(traversed_node_values, unsorted_data)

    def test_traverse_preorder(self):
        tree1 = self.tree1
        traversed_node_values = []
        preorder_data = list(self.TREE1_PREORDER_DATA)
        preorder_data_reversed = list(self.TREE1_PREORDER_DATA_REVERSED)

        def callback(node):
            nonlocal traversed_node_values
            traversed_node_values.append(node.value)

        with self.subTest("Test preorder non-reversed"):
            tree1.traverse_preorder(callback)
            self.assertEqual(traversed_node_values, preorder_data)
            self.assertNotEqual(traversed_node_values, preorder_data_reversed)

        traversed_node_values.clear()

        with self.subTest("Test preorder reversed"):
            tree1.traverse_preorder(callback, reverse=True)
            self.assertEqual(traversed_node_values, preorder_data_reversed)
            self.assertNotEqual(traversed_node_values, preorder_data)

    def test_traverse_postorder(self):
        tree1 = self.tree1
        traversed_node_values = []
        postorder_data = list(self.TREE1_POSTORDER_DATA)
        postorder_data_reversed = list(self.TREE1_POSTORDER_DATA_REVERSED)

        def callback(node):
            nonlocal traversed_node_values
            traversed_node_values.append(node.value)

        with self.subTest("Test postorder non-reversed"):
            tree1.traverse_postorder(callback)
            self.assertEqual(traversed_node_values, postorder_data)
            self.assertNotEqual(traversed_node_values, postorder_data_reversed)

        traversed_node_values.clear()

        with self.subTest("Test postorder reversed"):
            tree1.traverse_postorder(callback, reverse=True)
            self.assertEqual(traversed_node_values, postorder_data_reversed)
            self.assertNotEqual(traversed_node_values, postorder_data)

    def test_traverse_breadthfirst(self):
        tree1 = self.tree1
        traversed_node_values = []
        breadthfirst_data = list(self.TREE1_BREADTHFIRST_DATA)

        def callback(node):
            nonlocal traversed_node_values
            traversed_node_values.append(node.value)

        tree1.traverse_breadthfirst(callback)
        self.assertEqual(traversed_node_values, breadthfirst_data)

    def test_cmp_hash(self):
        cmp = BinaryTree.cmp_hash

        for i in range(5):
            with self.subTest(f"Test cmp == 0 for '{i}'"):
                self.assertEqual(cmp(i, i), 0)

        a = "a"
        z = "z"
        if hash(a) > hash(z):
            a, z = z, a

        for i, j in ((-5, 5), (0, 10**10), (a, z)):
            with self.subTest(f"Test cmp < 0 for '{i}' and '{j}'"):
                self.assertLess(cmp(i, j), 0)

            with self.subTest(f"Test cmp > 0 for '{j}' and '{i}'"):
                self.assertGreater(cmp(j, i), 0)

    def test_10k_nodes_tree(self):
        tree = BinaryTree(allow_dupes=False)
        traversed_node_values = []

        def callback(node):
            nonlocal traversed_node_values
            traversed_node_values.append(node.value)

        with open(self.TREE3_DATA_PATH, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            values = json_data["values"]

        sorted_values = sorted(values)

        for v in values:
            tree.add(v)

        tree.traverse_inorder(callback)
        self.assertEqual(traversed_node_values, sorted_values)
        traversed_node_values.clear()

        new_value = -1
        self.assertFalse(tree.has_value(new_value))
        self.assertTrue(tree.add(new_value))
        self.assertTrue(tree.has_value(new_value))

        old_value = 999
        self.assertTrue(tree.has_value(old_value))
        self.assertFalse(tree.add(old_value))

        root = tree._root# pylint: disable=protected-access
        root_value = root.value
        left_child = root.left_child
        right_child = root.right_child

        self.assertTrue(tree.has_value(root_value))
        self.assertTrue(tree.delete(root_value))
        self.assertFalse(tree.has_value(root_value))

        new_root = tree._root# pylint: disable=protected-access
        new_root_value = new_root.value
        self.assertNotEqual(root_value, new_root_value)

        self.assertLess(hash(left_child), hash(new_root))
        self.assertGreaterEqual(hash(right_child), hash(new_root))

        for value in (5555, 9999, 6, 100):
            with self.subTest(f"Test delete value '{value}'"):
                self.assertTrue(tree.has_value(value))
                self.assertTrue(tree.delete(value))
                self.assertFalse(tree.has_value(value))
