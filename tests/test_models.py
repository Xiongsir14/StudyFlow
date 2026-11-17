"""
测试：任务模型与存储
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from studyflow.models import Task, Course
from studyflow.storage import Storage
from datetime import datetime, timedelta
import tempfile, os


def test_task_validation():
    t = Task(title="", estimated_minutes=-1, priority=0)
    errors = t.validate()
    assert len(errors) >= 3  # 标题空、时间负数、优先级超范围
    print("  [OK] task_validation 通过")


def test_task_urgency():
    # 过期任务更紧急（urgency_score 更小即更紧急，堆中排在前面）
    t1 = Task(title="过期任务", deadline=datetime.now() - timedelta(days=1), priority=3)
    t2 = Task(title="未来任务", deadline=datetime.now() + timedelta(days=10), priority=3)
    # urgency_score 是负值排序，值越小越优先
    assert t1.urgency_score < t2.urgency_score  # 过期更紧急
    print(f"  [OK] task_urgency 通过 (过期={t1.urgency_score:.2f}, 未来={t2.urgency_score:.2f})")


def test_task_overdue():
    t = Task(title="过期", deadline=datetime.now() - timedelta(hours=1))
    assert t.is_overdue is True
    t.completed = True
    assert t.is_overdue is False  # 已完成不算逾期
    print("  [OK] task_overdue 通过")


def test_course_validation():
    c = Course(name="")
    assert len(c.validate()) == 1
    c.name = "算法"
    assert len(c.validate()) == 0
    print("  [OK] course_validation 通过")


def test_storage_crud():
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "test.json")
    storage = Storage(filepath)

    # 添加课程
    course = Course(name="测试课程", instructor="张老师", credits=3)
    assert storage.add_course(course)

    # 添加任务
    task = Task(title="测试任务", course_id=course.id, estimated_minutes=60, priority=4)
    assert storage.add_task(task)

    # 标记完成
    assert storage.mark_complete(task.id)
    assert storage.tasks[task.id].completed is True

    # 统计
    stats = storage.get_stats()
    assert stats["completed_tasks"] == 1
    assert stats["total_tasks"] == 1

    # 删除任务
    assert storage.delete_task(task.id)
    assert task.id not in storage.tasks

    # 删除课程
    assert storage.delete_course(course.id)
    assert course.id not in storage.courses

    # 清理
    os.remove(filepath)
    os.rmdir(tmpdir)
    print("  [OK] storage_crud 通过")


if __name__ == "__main__":
    print("Models & Storage 测试:")
    test_task_validation()
    test_task_urgency()
    test_task_overdue()
    test_course_validation()
    test_storage_crud()
    print("全部测试通过！")
