"""
测试：依赖图与拓扑排序
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from studyflow.graph import DependencyGraph


def test_add_edge():
    g = DependencyGraph()
    assert g.add_edge("A", "B") is True
    assert "A" in g.get_all_nodes()
    assert "B" in g.get_all_nodes()
    assert g.get_prerequisites("B") == ["A"]
    assert g.get_successors("A") == ["B"]
    print("  [OK] add_edge 通过")


def test_cycle_detection():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    result = g.add_edge("C", "A")  # 形成环
    assert result is False
    assert g.has_cycle() is False
    print("  [OK] cycle_detection 通过")


def test_topological_sort():
    g = DependencyGraph()
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    g.add_edge("C", "E")

    order = g.topological_sort()
    assert len(order) == 5
    # A、B 在 C 之前
    assert order.index("A") < order.index("C")
    assert order.index("B") < order.index("C")
    # C 在 D、E 之前
    assert order.index("C") < order.index("D")
    assert order.index("C") < order.index("E")
    print(f"  [OK] topological_sort 通过 (顺序: {order})")


def test_ready_tasks():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")

    ready = g.get_ready_tasks(set())
    assert set(ready) == {"A"}  # 只有A无前置

    ready2 = g.get_ready_tasks({"A"})
    assert set(ready2) == {"B", "C"}  # A完成后B、C可用

    ready3 = g.get_ready_tasks({"A", "B"})
    assert set(ready3) == {"C", "D"}
    print("  [OK] ready_tasks 通过")


def test_remove():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.remove_edge("A", "B")
    assert g.get_prerequisites("B") == []
    assert g.get_successors("A") == []

    g.remove_node("C")
    assert "C" not in g.get_all_nodes()
    assert g.get_prerequisites("A") == []
    print("  [OK] remove 通过")


def test_empty():
    g = DependencyGraph()
    assert len(g) == 0
    assert g.topological_sort() == []
    assert g.has_cycle() is False
    print("  [OK] empty 通过")


if __name__ == "__main__":
    print("DependencyGraph 测试:")
    test_add_edge()
    test_cycle_detection()
    test_topological_sort()
    test_ready_tasks()
    test_remove()
    test_empty()
    print("全部测试通过！")
