"""
StudyFlow - 智能学习任务规划器

基于数据结构与算法的学习管理工具：
- 最小堆（优先队列）进行任务调度
- 有向图与拓扑排序管理任务依赖
- Trie（前缀树）实现快速搜索
"""

from .models import Course, Task
from .heap import MinHeap
from .graph import DependencyGraph
from .trie import Trie
from .storage import Storage
from .planner import StudyPlanner, DailyPlan, PlannedTask

__version__ = "1.0.0"
