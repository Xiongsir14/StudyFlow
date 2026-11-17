"""
测试：计划生成器
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from studyflow.models import Task, Course
from studyflow.storage import Storage
from studyflow.planner import StudyPlanner
from datetime import datetime, timedelta
import tempfile


def test_plan_generation():
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "test_plan.json")
    storage = Storage(filepath)

    # 添加课程
    storage.add_course(Course(id="c1", name="算法"))

    # 添加几个任务：一个有依赖
    t1 = Task(id="t1", title="任务A", course_id="c1",
              deadline=datetime.now() + timedelta(days=5),
              estimated_minutes=60, priority=5)
    storage.add_task(t1)

    t2 = Task(id="t2", title="任务B", course_id="c1",
              deadline=datetime.now() + timedelta(days=2),
              estimated_minutes=30, priority=3)
    storage.add_task(t2)

    t3 = Task(id="t3", title="任务C", course_id="c1",
              deadline=datetime.now() - timedelta(days=1),  # 已过期
              estimated_minutes=45, priority=4)
    storage.add_task(t3)

    # t4 依赖 t2
    t4 = Task(id="t4", title="任务D", course_id="c1",
              deadline=datetime.now() + timedelta(days=10),
              estimated_minutes=90, priority=2,
              prerequisites=["t2"])
    storage.add_task(t4)

    # 重新加载以刷新依赖图
    storage.save()
    storage2 = Storage(filepath)
    storage2.load()

    planner = StudyPlanner(storage2)
    plan = planner.plan_today(available_minutes=200)

    # 验证计划
    assert len(plan.tasks) >= 1
    # t2 应该在前（截止日期更近）
    task_ids_in_plan = [pt.task.id for pt in plan.tasks]
    # t4 因为前置未完成，不应该在计划中
    assert "t4" not in task_ids_in_plan

    # 验证拓扑排序
    order = planner.get_topological_order()
    # t4在t2之后
    if "t2" in order and "t4" in order:
        assert order.index("t2") < order.index("t4")

    # 清理
    os.remove(filepath)
    os.rmdir(tmpdir)
    print("  [OK] plan_generation 通过")


if __name__ == "__main__":
    print("StudyPlanner 测试:")
    test_plan_generation()
    print("全部测试通过！")
