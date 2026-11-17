"""
StudyFlow 数据模型
定义 Task（任务）和 Course（课程）数据结构，包含验证逻辑。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Course:
    """课程模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    instructor: str = ""
    credits: int = 0
    color: str = "#4A90D9"

    def validate(self) -> list[str]:
        errors = []
        if not self.name.strip():
            errors.append("课程名称不能为空")
        if self.credits < 0:
            errors.append("学分不能为负数")
        return errors

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "instructor": self.instructor,
            "credits": self.credits,
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Course":
        return cls(
            id=d.get("id", str(uuid.uuid4())[:8]),
            name=d.get("name", ""),
            instructor=d.get("instructor", ""),
            credits=d.get("credits", 0),
            color=d.get("color", "#4A90D9"),
        )


@dataclass
class Task:
    """学习任务模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    course_id: str = ""
    description: str = ""
    deadline: Optional[datetime] = None
    estimated_minutes: int = 30
    priority: int = 3       # 1-5, 5最高
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    prerequisites: list[str] = field(default_factory=list)  # 前置任务ID列表
    tags: list[str] = field(default_factory=list)

    PRIORITY_NAMES = {1: "很低", 2: "较低", 3: "中等", 4: "较高", 5: "很高"}

    def validate(self) -> list[str]:
        errors = []
        if not self.title.strip():
            errors.append("任务标题不能为空")
        if self.estimated_minutes <= 0:
            errors.append("预计时间必须大于0")
        if self.priority < 1 or self.priority > 5:
            errors.append("优先级必须在1-5之间")
        if self.deadline is not None and self.deadline < datetime.now():
            errors.append("截止日期已过，请检查")
        return errors

    @property
    def priority_name(self) -> str:
        return self.PRIORITY_NAMES.get(self.priority, "未知")

    @property
    def is_overdue(self) -> bool:
        if self.deadline is None or self.completed:
            return False
        return datetime.now() > self.deadline

    @property
    def days_until_deadline(self) -> Optional[int]:
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.now()
        return max(0, delta.days)

    @property
    def urgency_score(self) -> float:
        """计算紧急度分数（用于优先队列排序）"""
        if self.completed:
            return float("inf")  # 已完成任务排在最后
        if self.deadline is None:
            days_factor = 365  # 无截止日期，低紧迫度
        else:
            delta = self.deadline - datetime.now()
            days_factor = max(0, delta.total_seconds() / 86400.0)
        # 紧急度 = 截止日期近 + 优先级高 + 时间短（优先完成短任务）
        # 使用加权公式
        urgency = (100.0 / (days_factor + 1.0)) - (self.priority * 10.0)
        return -urgency  # 负值使min-heap弹出最紧急的

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "course_id": self.course_id,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "estimated_minutes": self.estimated_minutes,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "prerequisites": self.prerequisites,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        deadline = d.get("deadline")
        if deadline:
            deadline = datetime.fromisoformat(deadline)
        completed_at = d.get("completed_at")
        if completed_at:
            completed_at = datetime.fromisoformat(completed_at)
        return cls(
            id=d.get("id", str(uuid.uuid4())[:8]),
            title=d.get("title", ""),
            course_id=d.get("course_id", ""),
            description=d.get("description", ""),
            deadline=deadline,
            estimated_minutes=d.get("estimated_minutes", 30),
            priority=d.get("priority", 3),
            completed=d.get("completed", False),
            created_at=datetime.fromisoformat(d.get("created_at", datetime.now().isoformat())),
            completed_at=completed_at,
            prerequisites=d.get("prerequisites", []),
            tags=d.get("tags", []),
        )
