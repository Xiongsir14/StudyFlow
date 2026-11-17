"""
数据持久化模块 —— JSON 文件存储

负责课程和任务的读取、保存，以及索引的构建与维护。
使用 JSON 格式存储，便于人工查看和版本管理。
"""

import json
import os
from pathlib import Path
from typing import Optional

from .models import Course, Task
from .trie import Trie
from .graph import DependencyGraph


class Storage:
    """JSON 文件持久化管理器"""

    def __init__(self, filepath: str = "data/studyflow.json"):
        self.filepath = Path(filepath)
        self.courses: dict[str, Course] = {}
        self.tasks: dict[str, Task] = {}
        self._trie: Optional[Trie] = None
        self._graph: Optional[DependencyGraph] = None

    def load(self) -> bool:
        """从 JSON 文件加载数据，返回是否成功"""
        if not self.filepath.exists():
            return False
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.courses = {}
            for c in data.get("courses", []):
                course = Course.from_dict(c)
                self.courses[course.id] = course

            self.tasks = {}
            for t in data.get("tasks", []):
                task = Task.from_dict(t)
                self.tasks[task.id] = task

            self._trie = None
            self._graph = None
            return True
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"加载数据失败: {e}")
            return False

    def save(self) -> bool:
        """保存数据到 JSON 文件"""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "courses": [c.to_dict() for c in self.courses.values()],
                "tasks": [t.to_dict() for t in self.tasks.values()],
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            print(f"保存数据失败: {e}")
            return False

    def build_trie(self) -> Trie:
        """构建搜索 Trie 索引"""
        trie = Trie()
        for task in self.tasks.values():
            trie.insert(task.title, task.id)
            trie.insert(task.description, task.id)
            if task.course_id in self.courses:
                trie.insert(self.courses[task.course_id].name, task.id)
            for tag in task.tags:
                trie.insert(tag, task.id)
        self._trie = trie
        return trie

    def get_trie(self) -> Trie:
        """获取当前 Trie（惰性构建）"""
        if self._trie is None:
            self.build_trie()
        return self._trie

    def build_graph(self) -> DependencyGraph:
        """构建任务依赖图"""
        graph = DependencyGraph()
        for task in self.tasks.values():
            graph.add_node(task.id)
        for task in self.tasks.values():
            for prereq_id in task.prerequisites:
                if prereq_id in self.tasks:
                    graph.add_edge(prereq_id, task.id)
        self._graph = graph
        return graph

    def get_graph(self) -> DependencyGraph:
        """获取当前依赖图（惰性构建）"""
        if self._graph is None:
            self.build_graph()
        return self._graph

    def invalidate_cache(self) -> None:
        """数据变更后使索引缓存失效"""
        self._trie = None
        self._graph = None

    # ---- 课程操作 ----

    def add_course(self, course: Course) -> bool:
        if not course.name.strip():
            return False
        self.courses[course.id] = course
        self.invalidate_cache()
        self.save()
        return True

    def update_course(self, course: Course) -> bool:
        if course.id not in self.courses:
            return False
        self.courses[course.id] = course
        self.invalidate_cache()
        self.save()
        return True

    def delete_course(self, course_id: str) -> bool:
        if course_id not in self.courses:
            return False
        # 删除关联任务
        to_delete = [tid for tid, t in self.tasks.items() if t.course_id == course_id]
        for tid in to_delete:
            del self.tasks[tid]
        del self.courses[course_id]
        self.invalidate_cache()
        self.save()
        return True

    # ---- 任务操作 ----

    def add_task(self, task: Task) -> bool:
        errors = task.validate()
        if errors:
            return False
        self.tasks[task.id] = task
        self.invalidate_cache()
        self.save()
        return True

    def update_task(self, task: Task) -> bool:
        if task.id not in self.tasks:
            return False
        self.tasks[task.id] = task
        self.invalidate_cache()
        self.save()
        return True

    def delete_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        # 清理其他任务中对它的引用
        for task in self.tasks.values():
            if task_id in task.prerequisites:
                task.prerequisites.remove(task_id)
        self.invalidate_cache()
        self.save()
        return True

    def mark_complete(self, task_id: str) -> bool:
        from datetime import datetime
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.completed = True
        task.completed_at = datetime.now()
        self.invalidate_cache()
        self.save()
        return True

    def mark_incomplete(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.completed = False
        task.completed_at = None
        self.invalidate_cache()
        self.save()
        return True

    # ---- 统计 ----

    def get_stats(self) -> dict:
        """获取学习统计"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.completed)
        overdue = sum(1 for t in self.tasks.values() if t.is_overdue and not t.completed)
        total_minutes = sum(t.estimated_minutes for t in self.tasks.values())
        completed_minutes = sum(t.estimated_minutes for t in self.tasks.values() if t.completed)

        # 按课程统计
        course_stats = {}
        for task in self.tasks.values():
            cid = task.course_id
            if cid not in course_stats:
                course_stats[cid] = {"total": 0, "completed": 0, "minutes": 0}
            course_stats[cid]["total"] += 1
            course_stats[cid]["minutes"] += task.estimated_minutes
            if task.completed:
                course_stats[cid]["completed"] += 1

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "completion_rate": completed / total if total > 0 else 0,
            "total_minutes": total_minutes,
            "completed_minutes": completed_minutes,
            "course_stats": course_stats,
        }
