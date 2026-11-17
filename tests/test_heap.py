"""
测试：自定义最小堆（MinHeap）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from studyflow.heap import MinHeap


def test_push_pop():
    """测试插入和弹出"""
    heap = MinHeap[int]()
    heap.push(5.0, 5)
    heap.push(3.0, 3)
    heap.push(7.0, 7)
    heap.push(1.0, 1)
    heap.push(4.0, 4)

    assert len(heap) == 5
    assert heap.pop() == 1
    assert heap.pop() == 3
    assert heap.pop() == 4
    assert heap.pop() == 5
    assert heap.pop() == 7
    assert len(heap) == 0
    assert heap.pop() is None
    print("  [OK] push_pop 通过")


def test_peek():
    """测试查看堆顶"""
    heap = MinHeap[str]()
    heap.push(2.0, "b")
    heap.push(1.0, "a")
    assert heap.peek() == "a"
    assert heap.peek_key() == 1.0
    # peek 不移除
    assert len(heap) == 2
    print("  [OK] peek 通过")


def test_heapify():
    """测试从列表建堆"""
    items = [(5, "e"), (3, "c"), (8, "h"), (1, "a"), (6, "f"), (2, "b")]
    heap = MinHeap.heapify(items)
    assert len(heap) == 6
    assert heap.pop() == "a"
    assert heap.pop() == "b"
    assert heap.pop() == "c"
    print("  [OK] heapify 通过")


def test_to_sorted_list():
    """测试堆排序"""
    heap = MinHeap[int]()
    values = [9, 3, 7, 1, 5, 2, 8, 4, 6]
    for v in values:
        heap.push(float(v), v)

    sorted_asc = heap.to_sorted_list(ascending=True)
    assert sorted_asc == sorted(values)
    print("  [OK] to_sorted_list (升序) 通过")

    # 重新填充
    for v in values:
        heap.push(float(v), v)
    sorted_desc = heap.to_sorted_list(ascending=False)
    assert sorted_desc == sorted(values, reverse=True)
    print("  [OK] to_sorted_list (降序) 通过")


def test_empty():
    """测试空堆"""
    heap = MinHeap[int]()
    assert not bool(heap)
    assert len(heap) == 0
    assert heap.pop() is None
    assert heap.peek() is None
    assert heap.peek_key() is None
    print("  [OK] empty 通过")


def test_large():
    """测试大量数据"""
    heap = MinHeap[int]()
    n = 1000
    for i in range(n, 0, -1):
        heap.push(float(i), i)
    for i in range(1, n + 1):
        assert heap.pop() == i
    print(f"  [OK] large ({n} 个元素) 通过")


if __name__ == "__main__":
    print("MinHeap 测试:")
    test_push_pop()
    test_peek()
    test_heapify()
    test_to_sorted_list()
    test_empty()
    test_large()
    print("全部测试通过！")
