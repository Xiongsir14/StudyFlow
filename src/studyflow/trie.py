"""
Trie（前缀树）实现 —— 用于任务快速搜索

支持：
- 插入关键词（任务标题、课程名）
- 前缀搜索
- 模糊匹配（包含子串）

时间复杂度：
- 插入 O(m)，m 为单词长度
- 搜索 O(m)
- 前缀匹配 O(m + k)，k 为匹配结果数
"""


class TrieNode:
    """Trie 节点"""

    __slots__ = ("children", "task_ids", "is_end")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.task_ids: list[str] = []  # 经过此节点的任务 ID
        self.is_end: bool = False


class Trie:
    """
    前缀树

    用于按任务标题或课程名称快速搜索
    支持中文（Unicode 字符作为键）
    """

    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def insert(self, word: str, task_id: str) -> None:
        """插入单词并关联任务 ID"""
        if not word:
            return
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            if task_id not in node.task_ids:
                node.task_ids.append(task_id)
        node.is_end = True
        self._size += 1

    def remove(self, word: str, task_id: str) -> None:
        """移除某个任务 ID 与单词的关联"""
        if not word:
            return
        node = self.root
        for ch in word:
            if ch not in node.children:
                return
            node = node.children[ch]
            if task_id in node.task_ids:
                node.task_ids.remove(task_id)

    def search(self, prefix: str) -> list[str]:
        """
        前缀搜索：返回所有以 prefix 开头的任务 ID

        遍历到前缀末尾节点后，收集其子树中所有任务 ID
        """
        if not prefix:
            return []
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        # BFS 收集所有后代节点的 task_ids
        result: set[str] = set()
        stack = [node]
        while stack:
            cur = stack.pop()
            result.update(cur.task_ids)
            for child in cur.children.values():
                stack.append(child)
        return list(result)

    def contains_prefix(self, prefix: str) -> bool:
        """检查是否存在以 prefix 为前缀的单词"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def clear(self) -> None:
        """清空 Trie"""
        self.root = TrieNode()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"Trie(entries={self._size})"
