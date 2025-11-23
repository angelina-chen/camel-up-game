class LinkedList:
    """
    Singly linked list used to represent a stack of camels on a tile.

    Each node's `data` is typically a tuple like ('blue',) representing
    a camel on the track.
    """

    class Node:
        """
        A single node in the linked list.

        Attributes:
            data (Any): Payload stored in the node (e.g., a camel tuple).
            next (Node | None): Reference to the next node in the list.
        """

        def __init__(self, data: Any, next_node: Optional["LinkedList.Node"] = None) -> None:
            """
            Initialize a new node.

            Args:
                data (Any): Data to store in this node.
                next_node (Node | None, optional): Next node in the list.
            """
            self.data = data
            self.next: Optional["LinkedList.Node"] = next_node

        def __str__(self) -> str:
            return str(self.data)

    def __init__(self) -> None:
        """
        Initialize an empty linked list.
        """
        self.head: Optional[LinkedList.Node] = None

    def append(self, data: Any) -> None:
        """
        Add a new node with the given data to the end of the list.

        Args:
            data (Any): Data to store in the new node (e.g., a camel tuple).

        Returns:
            None
        """
        new_node = LinkedList.Node(data)
        if self.head is None:
            self.head = new_node
            return

        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = new_node

    def to_list(self) -> list[Any]:
        """
        Convert the linked list to a Python list of node data, from head to tail.

        Returns:
            list[Any]: List of node data values in order.
        """
        result: list[Any] = []
        curr = self.head
        while curr:
            result.append(curr.data)
            curr = curr.next
        return result

    def remove_from(self, color: str) -> Optional["LinkedList.Node"]:
        """
        Remove and return the node whose data's first element matches `color`,
        along with all nodes above it in the stack.

        This is used to "lift" a camel and everything stacked above it.

        Args:
            color (str): Camel color to remove from the stack.

        Returns:
            Node | None:
                - The starting node of the removed stack if found.
                - None if no node with the given color exists in the list.
        """
        if self.head is None:
            return None

        # If the target is at the head, remove the entire list
        if self.head.data[0] == color:
            moving = self.head
            self.head = None
            return moving

        prev = self.head
        curr = prev.next
        while curr:
            if curr.data[0] == color:
                # Disconnect previous node from this stack
                prev.next = None
                return curr
            prev = curr
            curr = curr.next
        return None

    def add_stack_to_top(self, node: Optional["LinkedList.Node"]) -> None:
        """
        Attach the given stack (node and its successors) to the end of the list.

        Args:
            node (Node | None): Starting node of the stack to attach.

        Returns:
            None
        """
        if node is None:
            return

        if self.head is None:
            self.head = node
            return

        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = node

    def remove_stack_from_top(self, n: int) -> Optional["LinkedList.Node"]:
        """
        Remove the top `n` nodes (the last n nodes) from the list and return
        the starting node of that removed stack.

        Args:
            n (int): Number of nodes to remove from the top of the stack.

        Returns:
            Node | None:
                - Starting node of the removed stack if the list is non-empty.
                - None if the list is empty.
        """
        if self.head is None:
            return None

        # Compute total length
        length = 0
        curr = self.head
        while curr:
            length += 1
            curr = curr.next

        # If n >= length, remove the entire list
        if n >= length:
            stack = self.head
            self.head = None
            return stack

        # Walk to the node just before the split point
        prev: Optional[LinkedList.Node] = None
        curr = self.head
        for _ in range(length - n):
            prev = curr
            curr = curr.next  # type: ignore[assignment]

        if prev is not None:
            prev.next = None
        return curr

    def add_stack_to_bottom(self, node: Optional["LinkedList.Node"]) -> None:
        """
        Attach the given stack node to the beginning (bottom) of the list.

        Args:
            node (Node | None): Starting node of the stack to prepend.

        Returns:
            None
        """
        if node is None:
            return

        # Find end of provided stack
        tail = node
        while tail.next:
            tail = tail.next

        # Attach current list after this stack, then update head
        tail.next = self.head
        self.head = node

    def __str__(self) -> str:
        """
        String representation of the list.

        Returns:
            str: Stringified list of node data.
        """
        return str(self.to_list())
