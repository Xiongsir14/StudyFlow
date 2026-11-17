"""
学习计划生成器 —— 核心调度算法

使用最小堆（优先队列）和依赖图协同工作：
1. 从依赖图中获取所有前置已完成的任务（可执行任务）
2. 将这些任务按紧急度分数放入最小堆
3. 按每日可用时间，贪心选择最紧急的任务
4. 根据拓扑排序给出建议的执行顺序
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from .models import Task, Course
from .heap import MinHeap
from .graph import DependencyGraph
from .storage import Storage


@dataclass
class PlannedTask:
    """计划中的单个任务项"""
    task: Task
    course_name: str = ""
    start_minute: int = 0    # 在当天计划中的开始分钟数
    end_minute: int = 0      # 结束分钟数
    is_overdue: bool = False
    is_blocked: bool = False  # 被前置依赖阻塞


@dataclass
class DailyPlan:
    """一天的完整学习计划"""
    date: datetime = field(default_factory=datetime.now)
    available_minutes: int = 480
    tasks: list[PlannedTask] = field(default_factory=list)
    total_planned_minutes: int = 0
    unplanned_tasks: list[Task] = field(default_factory=list)
    blocked_tasks: list[Task] = field(default_factory=list)

    @property
    def utilization(self) -> float:
        if self.available_minutes <= 0:
            return 0.0
        return min(1.0, self.total_planned_minutes / self.available_minutes)


class StudyPlanner:
    """
    学习计划器

    核心算法：
    1. 用依赖图获取可执行任务列表
    2. 用最小堆按紧急度排序
    3. 贪心分配时间，考虑每日上限
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def plan_today(self, available_minutes: int = 480) -> DailyPlan:
        """
        生成今日学习计划

        参数:
            available_minutes: 今日可用的学习时间（分钟）

        返回:
            DailyPlan 包含计划任务列表和未计划任务
        """
        plan = DailyPlan(available_minutes=available_minutes)

        # 获取依赖图
        graph = self.storage.get_graph()

        # 获取已完成任务集合
        completed = {tid for tid, t in self.storage.tasks.items() if t.completed}

        # 获取可执行任务
        ready_ids = graph.get_ready_tasks(completed)

        # 同时考虑无依赖的任务（不在图中）
        for tid, task in self.storage.tasks.items():
            if tid not in graph.get_all_nodes() and not task.completed:
                ready_ids.append(tid)

        # 用最小堆排序（按紧急度）
        heap = MinHeap[str]()
        for tid in ready_ids:
            task = self.storage.tasks[tid]
            heap.push(task.urgency_score, tid)

        # 贪心分配时间
        remaining = available_minutes
        current_minute = 0

        while heap and remaining > 0:
            tid = heap.pop()
            task = self.storage.tasks.get(tid)
            if task is None or task.completed:
                continue

            course_name = self.storage.courses.get(task.course_id, Course()).name

            if task.estimated_minutes <= remaining:
                pt = PlannedTask(
                    task=task,
                    course_name=course_name,
                    start_minute=current_minute,
                    end_minute=current_minute + task.estimated_minutes,
                    is_overdue=task.is_overdue,
                )
                plan.tasks.append(pt)
                current_minute += task.estimated_minutes
                plan.total_planned_minutes += task.estimated_minutes
                remaining -= task.estimated_minutes
            else:
                # 放不下了，加入未计划
                plan.unplanned_tasks.append(task)

        # 弹出剩余的未计划任务
        while heap:
            tid = heap.pop()
            task = self.storage.tasks.get(tid)
            if task and not task.completed:
                plan.unplanned_tasks.append(task)

        # 找出被阻塞的任务
        all_task_ids = set(self.storage.tasks.keys())
        for tid in all_task_ids - set(ready_ids):
            task = self.storage.tasks[tid]
            if not task.completed:
                plan.blocked_tasks.append(task)

        return plan

    def get_topological_order(self) -> list[str]:
        """获取任务的拓扑排序（学习路径建议）"""
        graph = self.storage.get_graph()
        return graph.topological_sort()
