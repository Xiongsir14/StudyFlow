"""
自定义最小堆（优先队列）实现

用于任务调度：根据紧急度分数排序，始终弹出最紧急的任务。
不依赖 Python 标准库 heapq，展示堆数据结构的完整实现。
"""

from typing import TypeVar, Generic, Optional
from functools import total_ordering

T = TypeVar("T")


@total_ordering
class HeapItem(Generic[T]):
    """堆元素：包含排序键和实际数据"""

    def __init__(self, key: float, value: T):
        self.key = key
        self.value = value

    def __lt__(self, other: "HeapItem") -> bool:
        return self.key < other.key

    def __eq__(self, other: "HeapItem") -> bool:
        return self.key == other.key

    def __repr__(self) -> str:
        return f"HeapItem(key={self.key:.2f}, value={self.value})"


class MinHeap(Generic[T]):
    """
    最小堆（二叉堆）实现

    性质：
    - 完全二叉树结构，用数组存储
    - 父节点键值 <= 子节点键值
    - 插入 O(log n)，弹出 O(log n)，查看堆顶 O(1)
    - 空间复杂度 O(n)
    """

    def __init__(self):
        self._data: list[HeapItem[T]] = []

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return len(self._data) > 0

    def __repr__(self) -> str:
        return f"MinHeap(size={len(self)})"

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i: int) -> None:
        """上浮：维持堆性质"""
        while i > 0:
            parent = self._parent(i)
            if self._data[i] < self._data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """下沉：维持堆性质"""
        n = len(self._data)
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)

            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def push(self, key: float, value: T) -> None:
        """插入元素 O(log n)"""
        item = HeapItem(key, value)
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Optional[T]:
        """弹出最小元素 O(log n)"""
        if not self._data:
            return None
        if len(self._data) == 1:
            return self._data.pop().value
        result = self._data[0].value
        self._data[0] = self._data.pop()
        self._sift_down(0)
        return result

    def peek(self) -> Optional[T]:
        """查看堆顶 O(1)"""
        if not self._data:
            return None
        return self._data[0].value

    def peek_key(self) -> Optional[float]:
        """查看堆顶键值 O(1)"""
        if not self._data:
            return None
        return self._data[0].key

    def to_sorted_list(self, ascending: bool = True) -> list[T]:
        """
        堆排序：将所有元素按序弹出，返回排序列表
        时间复杂度 O(n log n)，空间复杂度 O(n)
        会清空堆！
        """
        result = []
        while self:
            result.append(self.pop())
        if not ascending:
            result.reverse()
        return result

    @classmethod
    def heapify(cls, items: list[tuple[float, T]]) -> "MinHeap[T]":
        """
        从列表构建堆 O(n)
        从最后一个非叶子节点开始依次下沉
        """
        heap = cls()
        heap._data = [HeapItem(k, v) for k, v in items]
        n = len(heap._data)
        for i in range(n // 2 - 1, -1, -1):
            heap._sift_down(i)
        return heap
