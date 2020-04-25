class Node:
    def __init__(self, item=None):
        self.item = item
        self.next_item = None


class LinkedList:
    def __init__(self):
        self.head = None

    def contains(self, cat):
        last_item = self.head
        while last_item:
            if cat == last_item.cat:
                return True
            else:
                last_item = last_item.next_item
        return False

    def add_to_end(self, new_item):
        new_item = Node(new_item)
        if self.head is None:
            self.head = new_item
            return
        last_item = self.head
        while last_item.next_item:
            last_item = last_item.next_item
        last_item.next_item = new_item

    def add_to_beginning(self, new_item):
        new_item = Node(new_item)
        if self.head is None:
            self.head = new_item
            return
        new_item.next_item = self.head
        self.head = new_item

    def get(self, index):
        last_item = self.head
        node_index = 0
        while node_index <= index:
            if node_index == index:
                return last_item.item
            node_index = node_index + 1
            last_item = last_item.next_item

    def remove(self, removable_item):
        head_item = self.head
        if head_item is not None:
            if head_item.item == removable_item:
                self.head = head_item.next_item
                head_item = None
                return
        while head_item is not None:
            if head_item.cat == removable_item:
                break
            last_item = head_item
            head_item = head_item.next_item
        if head_item is None:
            return
        last_item.next_item = head_item.next_item
        head_item = None

    def size(self):
        head = self.head
        counter = 0
        while head.next_item is not None:
            counter += 1
            head = head.next_item
        return counter
