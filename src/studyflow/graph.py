"""
有向图与拓扑排序 —— 实现任务依赖关系管理

用邻接表存储图结构，支持：
- 添加依赖边
- 检测环路（DFS 三色标记法）
- 拓扑排序（Kahn 算法 / BFS 入度法）
- 获取可执行任务列表（所有前置已完成的任务）
"""

from collections import deque


class DependencyGraph:
    """
    有向图（邻接表表示）

    节点 ID 为字符串，边表示 "from -> to"（from 是前置，to 是后继）
    即：必须先完成 from 才能做 to

    空间复杂度：O(V + E)
    """

    def __init__(self):
        # 邻接表：节点 -> 后继节点列表
        self._adj: dict[str, list[str]] = {}
        # 反向邻接表：节点 -> 前置节点列表
        self._rev_adj: dict[str, list[str]] = {}

    def add_node(self, node_id: str) -> None:
        """添加节点"""
        if node_id not in self._adj:
            self._adj[node_id] = []
            self._rev_adj[node_id] = []

    def add_edge(self, from_id: str, to_id: str) -> bool:
        """
        添加依赖边：from_id 是 to_id 的前置任务
        返回 False 如果添加此边会形成环路
        """
        self.add_node(from_id)
        self.add_node(to_id)

        if to_id not in self._adj[from_id]:
            self._adj[from_id].append(to_id)
            self._rev_adj[to_id].append(from_id)

        # 检查环路
        if self.has_cycle():
            # 回滚
            self._adj[from_id].remove(to_id)
            self._rev_adj[to_id].remove(from_id)
            return False
        return True

    def remove_edge(self, from_id: str, to_id: str) -> None:
        """移除依赖边"""
        if from_id in self._adj and to_id in self._adj[from_id]:
            self._adj[from_id].remove(to_id)
        if to_id in self._rev_adj and from_id in self._rev_adj[to_id]:
            self._rev_adj[to_id].remove(from_id)

    def remove_node(self, node_id: str) -> None:
        """移除节点及其所有边"""
        if node_id in self._adj:
            for succ in self._adj[node_id]:
                if node_id in self._rev_adj.get(succ, []):
                    self._rev_adj[succ].remove(node_id)
            del self._adj[node_id]
        if node_id in self._rev_adj:
            for pred in self._rev_adj[node_id]:
                if node_id in self._adj.get(pred, []):
                    self._adj[pred].remove(node_id)
            del self._rev_adj[node_id]

    def has_cycle(self) -> bool:
        """
        检测图中是否存在环路 —— DFS 三色标记法
        白色(0): 未访问, 灰色(1): 访问中, 黑色(2): 已完成

        时间复杂度 O(V + E), 空间复杂度 O(V)
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {node: WHITE for node in self._adj}

        def dfs(node: str) -> bool:
            color[node] = GRAY
            for neighbor in self._adj.get(node, []):
                if color[neighbor] == GRAY:
                    return True  # 发现环路
                if color[neighbor] == WHITE:
                    if dfs(neighbor):
                        return True
            color[node] = BLACK
            return False

        for node in self._adj:
            if color[node] == WHITE:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> list[str]:
        """
        Kahn 算法（BFS 入度法）拓扑排序
        时间复杂度 O(V + E)，空间复杂度 O(V)

        Returns:
            拓扑排序的节点列表，如果存在环路则返回空列表
        """
        if self.has_cycle():
            return []

        in_degree: dict[str, int] = {node: 0 for node in self._adj}
        for node in self._adj:
            for neighbor in self._adj[node]:
                in_degree[neighbor] = in_degree.get(neighbor, 0) + 1

        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in self._adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result if len(result) == len(self._adj) else []

    def get_ready_tasks(self, completed: set[str]) -> list[str]:
        """
        获取当前可执行的任务列表
        即：所有前置任务都在 completed 集合中的任务

        时间复杂度 O(V + E)
        """
        ready = []
        for node in self._adj:
            if node in completed:
                continue
            prerequisites = self._rev_adj.get(node, [])
            if all(p in completed for p in prerequisites):
                ready.append(node)
        return ready

    def get_prerequisites(self, node_id: str) -> list[str]:
        """获取某个任务的所有前置任务"""
        return list(self._rev_adj.get(node_id, []))

    def get_successors(self, node_id: str) -> list[str]:
        """获取某个任务的所有后继任务"""
        return list(self._adj.get(node_id, []))

    def get_all_nodes(self) -> list[str]:
        return list(self._adj.keys())

    def __len__(self) -> int:
        return len(self._adj)

    def __repr__(self) -> str:
        edges = sum(len(v) for v in self._adj.values())
        return f"DependencyGraph(nodes={len(self)}, edges={edges})"
