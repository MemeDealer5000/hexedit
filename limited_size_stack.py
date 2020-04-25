from linked_list import LinkedList


class LimitedSizeStack:
    def __init__(self, _limit):
        self._limit = _limit
        self.lss = LinkedList()

    def push(self, item):
        if self._limit == 0:
            raise IndexError("Limit cant be equal zero")
        if self.lss.size() == self._limit:
            self.lss.remove()
