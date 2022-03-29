# pylint: disable=invalid-name
# pylint: enable=invalid-name
"""
Python implementation of binary tree
"""


from __future__ import annotations


__all__ = ["BinaryTree"]
__version__ = "0.0.1"
__author__ = "Booplicate"


from collections import deque
from functools import total_ordering
from typing import (
    TypeVar,
    TypeAlias,
    Callable,
    Any,
    Literal,
    Protocol,
    Generic,
    cast as cast_type,
    TYPE_CHECKING
)


class CompHashProto(Protocol):
    """
    Protocol for hashable and comparable objects
    """
    def __hash__(self) -> int:
        return 0
    def __eq__(self, other) -> bool:
        ...
    def __ne__(self, other) -> bool:
        ...
    def __lt__(self, other) -> bool:
        ...
    def __gt__(self, other) -> bool:
        ...
    def __le__(self, other) -> bool:
        ...
    def __ge__(self, other) -> bool:
        ...

_T = TypeVar("_T", bound=CompHashProto)# pylint: disable=invalid-name
# Big sad I can't do this...
# _TraverseCallback: TypeAlias = Callable[[_Node[_T]], Any]


@total_ordering
class _Node(Generic[_T]):
    """
    Represents a binary tree node
    """
    __slots__ = ("value", "parent", "left_child", "right_child")

    def __init__(
        self,
        value: _T,
        parent: _Node[_T] | None = None,
        left_child: _Node[_T] | None = None,
        right_child: _Node[_T] | None = None
    ) -> None:
        """
        Constructor for binary tree node

        IN:
            value - node value (must be hashable)
            parent - the parent node for this node
                (Default: None)
            left_child - the left child node for this node
                (Default: None)
            right_child - the right child node for this node
                (Default: None)
        """
        self.value = value
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child

    def __repr__(self) -> str:
        return self.repr(1)

    def repr(self, depth: int) -> str:
        """
        Returns repr for this object

        IN:
            depth - int - recursion depth,
                0 means don't print parent/children

        OUT:
            str
        """
        return (
            f"<{type(self).__name__}"
            f"(value={self.value}, "
            f"parent={self._get_repr(self.parent, depth)}, "
            f"left_child={self._get_repr(self.left_child, depth)}, "
            f"right_child={self._get_repr(self.right_child, depth)})>"
        )

    @staticmethod
    def _get_repr(node: _Node | None, depth: int) -> str:
        """
        Return repr of a node
        if the node is None, return None
        Otherwise if the node exists, return repr for depth-1
        Otherwise return ellipsis

        IN:
            node - node whom repr to fetch
            depth - current recursion depth

        OUT:
            str
        """
        if node is None:
            return str(None)

        if depth > 0:
            return node.repr(depth-1)

        return "<...>"

    def remove_child(self, node: _Node[_T]) -> bool:
        """
        Removes a child from this node

        IN:
            node - the node to remove

        OUT:
            bool - whether or not a child was removed
        """
        return self.replace_child(node, None)

    def replace_child(self, old_node: _Node[_T], new_node: _Node[_T] | None) -> bool:
        """
        Replaced a child of this node with a new child node (which can be None)

        IN:
            old_node - the node to remove
            new_node - the node to attach

        OUT:
            bool - whether or not a child was removed
        """
        if old_node is self.left_child:
            self.left_child = new_node
            return True

        if old_node is self.right_child:
            self.right_child = new_node
            return True

        return False

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, _Node):
            return NotImplemented

        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, _Node):
            return NotImplemented

        return self.value < other.value


class BinaryTree(Generic[_T]):
    """
    Represents a binary tree
    """
    def __init__(self, allow_dupes: bool = True) -> None:
        self.allow_dupes = allow_dupes
        self._root: _Node[_T] | None = None

    def _add(self, parent_node: _Node[_T], value: _T) -> bool:
        """
        Private methods that handles adding new nodes using recursion

        IN:
            parent_node - the mode we're trying to add new node to
            value - the value of the new node

        OUT:
            bool
        """
        cmp = self.cmp_hash(value, parent_node.value)

        if cmp < 0:
            if parent_node.left_child is None:
                parent_node.left_child = _Node(value, parent=parent_node)
                return True

            return self._add(parent_node.left_child, value)

        if (cmp > 0) or self.allow_dupes:
            if parent_node.right_child is None:
                parent_node.right_child = _Node(value, parent=parent_node)
                return True

            return self._add(parent_node.right_child, value)

        # The node is a dupe and we don't like dupes here
        return False

    def add(self, value: _T) -> bool:
        """
        Adds a new node with the given value to this tree

        IN:
            value - the value for the new node

        OUT:
            bool - whether or not the new node was added
        """
        if self._root is None:
            self._root = _Node(value)
            return True

        return self._add(self._root, value)

    def _find_min(self, current_node: _Node[_T]) -> _Node[_T]:
        """
        Finds minimal node starting from the given node

        IN:
            current_node - the current node

        OUT:
            node
        """
        # Found?
        if current_node.left_child is None:
            return current_node
        # Continue
        return self._find_min(current_node.left_child)

    def _handle_node_deletion(self, node: _Node[_T]) -> bool:
        """
        Handles node deletion

        IN:
            node - the node to delete

        OUT:
            bool
        """
        has_left_child = node.left_child is not None
        has_right_child = node.right_child is not None

        # Has both children
        if (has_left_child and has_right_child):
            if TYPE_CHECKING:
                node.right_child = cast_type(_Node[_T], node.right_child)

            # Find min node from the right child
            min_node = self._find_min(node.right_child)
            min_node_value = min_node.value
            # Changed the value of the current node (basically moving the min node)
            node.value = min_node_value
            # Delete the min node
            return self._delete(min_node, min_node_value)

        # No children
        if (not has_left_child and not has_right_child):
            # Special case if we need to delete the root node
            if self._root is node:
                self._root = None
                return True

            if TYPE_CHECKING:
                node.parent = cast_type(_Node[_T], node.parent)

            return node.parent.remove_child(node)

        # One child
        if has_left_child:
            child = node.left_child

        if has_right_child:
            child = node.right_child

        if TYPE_CHECKING:
            child = cast_type(_Node[_T], child)

        node.value = child.value
        node.left_child = child.left_child
        node.right_child = child.right_child
        return True

    def _delete(self, current_node: _Node[_T] | None, value: _T) -> bool:
        """
        Recursively deletes node with the given value

        IN:
            current_node - current node
            value - the node's value to delete

        OUT:
            bool
        """
        if current_node is None:
            return False

        # Search for the node
        cmp = self.cmp_hash(value, current_node.value)
        if cmp < 0:
            return self._delete(current_node.left_child, value)

        if cmp > 0:
            return self._delete(current_node.right_child, value)

        # Found, delete
        return self._handle_node_deletion(current_node)

    def delete(self, value: _T) -> bool:
        """
        Deletes a node from the tree

        IN:
            value - the node's value

        OUT:
            bool - whether or not the node was deleted
        """
        return self._delete(self._root, value)

    def _has_value(self, current_node: _Node[_T] | None, value: _T) -> bool:
        """
        Private methods that uses recursion to find a node

        IN:
            current_node - the node we're currently checking
            value - the value to check

        OUT:
            bool
        """
        if current_node is None:
            return False

        cmp = self.cmp_hash(value, current_node.value)

        if cmp < 0:
            return self._has_value(current_node.left_child, value)

        if cmp > 0:
            return self._has_value(current_node.right_child, value)

        return True

    def has_value(self, value: _T) -> bool:
        """
        Checks if a node with the given value exists

        IN:
            value - the value to check

        OUT:
            bool
        """
        return self._has_value(self._root, value)

    def traverse_inorder(
        self,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        """
        Traverse the tree using deepth first inorder algorithm

        IN:
            callback - a callable that's being used for processing the tree,
                must accept a single argument - the node being processed
        """
        self._traverse_inorder(self._root, callback=callback, reverse=reverse)

    def _traverse_inorder(
        self,
        node: _Node[_T] | None,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        if node is None:
            return

        left_child = node.left_child
        right_child = node.right_child
        children = (left_child, right_child) if not reverse else (right_child, left_child)

        self._traverse_inorder(children[0], callback=callback, reverse=reverse)
        callback(node)
        self._traverse_inorder(children[1], callback=callback, reverse=reverse)

    def traverse_preorder(
        self,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        """
        Traverse the tree using deepth first preorder algorithm

        IN:
            callback - a callable that's being used for processing the tree,
                must accept a single argument - the node being processed
        """
        self._traverse_preorder(self._root, callback=callback, reverse=reverse)

    def _traverse_preorder(
        self,
        node: _Node[_T] | None,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        if node is None:
            return

        left_child = node.left_child
        right_child = node.right_child
        children = (left_child, right_child) if not reverse else (right_child, left_child)

        callback(node)

        for child in children:
            self._traverse_preorder(child, callback=callback, reverse=reverse)

    def traverse_postorder(
        self,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        """
        Traverse the tree using deepth first postorder algorithm

        IN:
            callback - a callable that's being used for processing the tree,
                must accept a single argument - the node being processed
        """
        self._traverse_postorder(self._root, callback=callback, reverse=reverse)

    def _traverse_postorder(
        self,
        node: _Node[_T] | None,
        callback: Callable[[_Node[_T]], Any],
        reverse: bool = False
    ) -> None:
        if node is None:
            return

        left_child = node.left_child
        right_child = node.right_child
        children = (left_child, right_child) if not reverse else (right_child, left_child)

        for child in children:
            self._traverse_postorder(child, callback=callback, reverse=reverse)
        callback(node)

    def traverse_breadthfirst(
        self,
        callback: Callable[[_Node[_T]], Any]
    ) -> None:
        """
        Traverse the tree using breadth first algorithm

        IN:
            callback - a callable that's being used for processing the tree,
                must accept a single argument - the node being processed
        """
        if self._root is None:
            return

        queue: deque[_Node[_T]] = deque()
        queue.append(self._root)

        while queue:
            node = queue.pop()

            for child in (node.left_child, node.right_child):
                if child is not None:
                    queue.appendleft(child)

            callback(node)

    @staticmethod
    def cmp_hash(obj1: _Node[_T] | _T, obj2: _Node[_T] | _T) -> Literal[-1, 0, 1]:
        """
        Compares hash of 2 objects, returns an int in range [-1, 1]

        IN:
            obj1 - the first object to compare
            obj2 - the second object to compare

        OUT:
            int
        """
        # pylint: disable=invalid-name
        h1 = hash(obj1)
        h2 = hash(obj2)
        rv = (h1 > h2) - (h1 < h2)
        # mypy I swear to got...
        if TYPE_CHECKING:
            rv = cast_type(Literal[-1, 0, 1], rv)
        return rv
        # pylint: enable=invalid-name
