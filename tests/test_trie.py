"""
测试：前缀树 Trie
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from studyflow.trie import Trie


def test_insert_and_search():
    trie = Trie()
    trie.insert("数据结构", "t1")
    trie.insert("数组", "t2")
    trie.insert("数据科学", "t3")
    trie.insert("数字逻辑", "t4")

    # 前缀搜索
    result = trie.search("数据")
    assert set(result) == {"t1", "t3"}
    print("  [OK] insert_and_search 通过")


def test_single_char():
    trie = Trie()
    trie.insert("排序算法", "t1")
    result = trie.search("排")
    assert "t1" in result
    print("  [OK] single_char 通过")


def test_exact_match():
    trie = Trie()
    trie.insert("堆排序", "t1")
    trie.insert("堆", "t2")
    result = trie.search("堆排序")
    assert result == ["t1"]  # 精确匹配
    print("  [OK] exact_match 通过")


def test_no_match():
    trie = Trie()
    trie.insert("二叉树", "t1")
    result = trie.search("图")
    assert result == []
    print("  [OK] no_match 通过")


def test_remove():
    trie = Trie()
    trie.insert("算法", "t1")
    trie.insert("算法", "t2")
    trie.remove("算法", "t1")
    result = trie.search("算法")
    assert result == ["t2"]
    print("  [OK] remove 通过")


def test_empty():
    trie = Trie()
    assert trie.search("") == []
    assert trie.search("任意") == []
    assert len(trie) == 0
    print("  [OK] empty 通过")


def test_contains_prefix():
    trie = Trie()
    trie.insert("数据结构", "t1")
    assert trie.contains_prefix("数据") is True
    assert trie.contains_prefix("算法") is False
    print("  [OK] contains_prefix 通过")


if __name__ == "__main__":
    print("Trie 测试:")
    test_insert_and_search()
    test_single_char()
    test_exact_match()
    test_no_match()
    test_remove()
    test_empty()
    test_contains_prefix()
    print("全部测试通过！")
