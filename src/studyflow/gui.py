"""
StudyFlow GUI - Tkinter 图形界面

界面布局（标签页）：
- 仪表盘：概览统计 + 今日计划
- 任务管理：列表、增删改、搜索、标记完成
- 课程管理：课程增删改
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path

from .storage import Storage
from .models import Task, Course
from .planner import StudyPlanner
from .trie import Trie

# 主题颜色
COLORS = {
    "bg": "#F0F4F8",
    "fg": "#1A202C",
    "primary": "#4A90D9",
    "success": "#48BB78",
    "warning": "#ED8936",
    "danger": "#F56565",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
    "muted": "#A0AEC0",
    "overdue": "#FC8181",
}

FONT_TITLE = ("Microsoft YaHei", 16, "bold")
FONT_HEADING = ("Microsoft YaHei", 13, "bold")
FONT_NORMAL = ("Microsoft YaHei", 10)
FONT_SMALL = ("Microsoft YaHei", 9)
FONT_MONO = ("Consolas", 10)


class StudyFlowApp:
    """主应用窗口"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("StudyFlow - 智能学习任务规划器")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])

        # 数据层
        self.storage = Storage()
        self.storage.load()
        self.planner = StudyPlanner(self.storage)

        # 样式
        self._setup_styles()

        # 构建界面
        self._build_header()
        self._build_notebook()

        # 刷新数据
        self._refresh_all()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(20, 8), font=FONT_NORMAL,
                        background=COLORS["border"], foreground=COLORS["fg"])
        style.map("TNotebook.Tab", background=[("selected", COLORS["primary"])],
                  foreground=[("selected", "white")])

        style.configure("Card.TFrame", background=COLORS["card"], relief="solid", borderwidth=1)
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["fg"], font=FONT_NORMAL)
        style.configure("Card.TLabel", background=COLORS["card"], foreground=COLORS["fg"])
        style.configure("Title.TLabel", font=FONT_TITLE, background=COLORS["bg"])
        style.configure("Heading.TLabel", font=FONT_HEADING, background=COLORS["bg"])
        style.configure("Muted.TLabel", foreground=COLORS["muted"], font=FONT_SMALL, background=COLORS["bg"])
        style.configure("Success.TLabel", foreground=COLORS["success"], font=FONT_HEADING)
        style.configure("Danger.TLabel", foreground=COLORS["danger"], font=FONT_HEADING)
        style.configure("Warning.TLabel", foreground=COLORS["warning"], font=FONT_HEADING)

        style.configure("Primary.TButton", background=COLORS["primary"], foreground="white",
                        font=FONT_NORMAL, padding=(12, 6))
        style.map("Primary.TButton", background=[("active", "#3A7BC8")])
        style.configure("Success.TButton", background=COLORS["success"], foreground="white",
                        font=FONT_SMALL, padding=(8, 4))
        style.configure("Danger.TButton", background=COLORS["danger"], foreground="white",
                        font=FONT_SMALL, padding=(8, 4))

        style.configure("Treeview", font=FONT_NORMAL, rowheight=28)
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 10, "bold"))

    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_lbl = tk.Label(header, text="StudyFlow  智能学习任务规划器",
                             font=("Microsoft YaHei", 18, "bold"),
                             bg=COLORS["primary"], fg="white")
        title_lbl.pack(side="left", padx=20, pady=12)

        subtitle = tk.Label(header, text="DS&A Course Project  ·  用算法优化你的学习",
                            font=FONT_SMALL, bg=COLORS["primary"], fg="#BEE3F8")
        subtitle.pack(side="left", padx=5, pady=22)

        refresh_btn = tk.Button(header, text="刷新", command=self._refresh_all,
                                bg="#3A7BC8", fg="white", font=FONT_SMALL,
                                relief="flat", padx=12, pady=4, cursor="hand2")
        refresh_btn.pack(side="right", padx=15, pady=15)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- 仪表盘 ----
        self.tab_dashboard = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_dashboard, text="  仪表盘  ")

        # 统计卡片行
        self.stats_frame = tk.Frame(self.tab_dashboard, bg=COLORS["bg"])
        self.stats_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.stat_cards = {}
        stat_items = [
            ("total", "任务总数", COLORS["primary"]),
            ("completed", "已完成", COLORS["success"]),
            ("overdue", "已逾期", COLORS["danger"]),
            ("rate", "完成率", COLORS["warning"]),
        ]
        for key, label, color in stat_items:
            card = tk.Frame(self.stats_frame, bg=COLORS["card"], relief="solid",
                            bd=1, highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=5, ipady=10)
            tk.Label(card, text=label, font=FONT_SMALL, bg=COLORS["card"],
                     fg=COLORS["muted"]).pack()
            val = tk.Label(card, text="--", font=("Microsoft YaHei", 24, "bold"),
                           bg=COLORS["card"], fg=color)
            val.pack()
            self.stat_cards[key] = val

        # 今日计划区域
        plan_header = tk.Frame(self.tab_dashboard, bg=COLORS["bg"])
        plan_header.pack(fill="x", padx=15, pady=(10, 0))
        tk.Label(plan_header, text="今日学习计划", font=FONT_HEADING, bg=COLORS["bg"]).pack(side="left")
        tk.Label(plan_header, text="可用时间(分钟):", font=FONT_SMALL, bg=COLORS["bg"]).pack(side="left", padx=(30, 5))
        self.time_var = tk.StringVar(value="480")
        time_entry = tk.Entry(plan_header, textvariable=self.time_var, width=6,
                              font=FONT_NORMAL, justify="center")
        time_entry.pack(side="left")
        gen_btn = tk.Button(plan_header, text="生成计划", command=self._generate_plan,
                            bg=COLORS["primary"], fg="white", font=FONT_SMALL,
                            relief="flat", padx=12, pady=3, cursor="hand2")
        gen_btn.pack(side="left", padx=10)
        self.plan_summary = tk.Label(plan_header, text="", font=FONT_SMALL, bg=COLORS["bg"], fg=COLORS["muted"])
        self.plan_summary.pack(side="left", padx=5)

        # 计划列表
        plan_frame = tk.Frame(self.tab_dashboard, bg=COLORS["bg"])
        plan_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("title", "course", "duration", "priority", "status")
        self.plan_tree = ttk.Treeview(plan_frame, columns=columns, show="headings", height=12)
        self.plan_tree.heading("title", text="任务", anchor="w")
        self.plan_tree.heading("course", text="课程", anchor="w")
        self.plan_tree.heading("duration", text="时长(分)", anchor="center")
        self.plan_tree.heading("priority", text="优先级", anchor="center")
        self.plan_tree.heading("status", text="状态", anchor="center")
        self.plan_tree.column("title", width=300)
        self.plan_tree.column("course", width=120)
        self.plan_tree.column("duration", width=80, anchor="center")
        self.plan_tree.column("priority", width=80, anchor="center")
        self.plan_tree.column("status", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(plan_frame, orient="vertical", command=self.plan_tree.yview)
        self.plan_tree.configure(yscrollcommand=scrollbar.set)
        self.plan_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- 任务管理 ----
        self.tab_tasks = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_tasks, text="  任务管理  ")

        # 工具栏
        toolbar = tk.Frame(self.tab_tasks, bg=COLORS["bg"])
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._on_search())
        search_entry = tk.Entry(toolbar, textvariable=self.search_var, font=FONT_NORMAL,
                                width=25)
        search_entry.pack(side="left", padx=(0, 5))
        tk.Label(toolbar, text="🔍", bg=COLORS["bg"], font=FONT_NORMAL).pack(side="left")

        btn_add = tk.Button(toolbar, text="+ 添加任务", command=self._add_task_dialog,
                            bg=COLORS["primary"], fg="white", font=FONT_SMALL,
                            relief="flat", padx=12, pady=3, cursor="hand2")
        btn_add.pack(side="right", padx=3)
        btn_edit = tk.Button(toolbar, text="编辑", command=self._edit_task_dialog,
                             bg=COLORS["card"], fg=COLORS["fg"], font=FONT_SMALL,
                             relief="flat", padx=10, pady=3, cursor="hand2")
        btn_edit.pack(side="right", padx=3)
        btn_del = tk.Button(toolbar, text="删除", command=self._delete_task,
                            bg=COLORS["danger"], fg="white", font=FONT_SMALL,
                            relief="flat", padx=10, pady=3, cursor="hand2")
        btn_del.pack(side="right", padx=3)
        btn_done = tk.Button(toolbar, text="✓ 完成", command=self._mark_task_complete,
                             bg=COLORS["success"], fg="white", font=FONT_SMALL,
                             relief="flat", padx=10, pady=3, cursor="hand2")
        btn_done.pack(side="right", padx=3)

        # 任务列表
        task_frame = tk.Frame(self.tab_tasks, bg=COLORS["bg"])
        task_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("title", "course", "deadline", "est", "priority", "prereqs", "completed")
        self.task_tree = ttk.Treeview(task_frame, columns=cols, show="headings", height=18)
        self.task_tree.heading("title", text="标题", anchor="w")
        self.task_tree.heading("course", text="课程", anchor="w")
        self.task_tree.heading("deadline", text="截止日期", anchor="center")
        self.task_tree.heading("est", text="预计(分)", anchor="center")
        self.task_tree.heading("priority", text="优先级", anchor="center")
        self.task_tree.heading("prereqs", text="前置任务", anchor="w")
        self.task_tree.heading("completed", text="完成", anchor="center")
        self.task_tree.column("title", width=200)
        self.task_tree.column("course", width=100)
        self.task_tree.column("deadline", width=120, anchor="center")
        self.task_tree.column("est", width=70, anchor="center")
        self.task_tree.column("priority", width=60, anchor="center")
        self.task_tree.column("prereqs", width=180)
        self.task_tree.column("completed", width=60, anchor="center")

        sbar = ttk.Scrollbar(task_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=sbar.set)
        self.task_tree.pack(side="left", fill="both", expand=True)
        sbar.pack(side="right", fill="y")

        self.task_tree.bind("<Double-1>", lambda e: self._edit_task_dialog())

        # ---- 课程管理 ----
        self.tab_courses = tk.Frame(self.notebook, bg=COLORS["bg"])
        self.notebook.add(self.tab_courses, text="  课程管理  ")

        ctoolbar = tk.Frame(self.tab_courses, bg=COLORS["bg"])
        ctoolbar.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(ctoolbar, text="我的课程", font=FONT_HEADING, bg=COLORS["bg"]).pack(side="left")
        cbtn_add = tk.Button(ctoolbar, text="+ 添加课程", command=self._add_course_dialog,
                             bg=COLORS["primary"], fg="white", font=FONT_SMALL,
                             relief="flat", padx=12, pady=3, cursor="hand2")
        cbtn_add.pack(side="right", padx=3)
        cbtn_del = tk.Button(ctoolbar, text="删除", command=self._delete_course,
                             bg=COLORS["danger"], fg="white", font=FONT_SMALL,
                             relief="flat", padx=10, pady=3, cursor="hand2")
        cbtn_del.pack(side="right", padx=3)

        cframe = tk.Frame(self.tab_courses, bg=COLORS["bg"])
        cframe.pack(fill="both", expand=True, padx=10, pady=5)

        ccols = ("name", "instructor", "credits", "task_count")
        self.course_tree = ttk.Treeview(cframe, columns=ccols, show="headings", height=12)
        self.course_tree.heading("name", text="课程名称", anchor="w")
        self.course_tree.heading("instructor", text="教师", anchor="w")
        self.course_tree.heading("credits", text="学分", anchor="center")
        self.course_tree.heading("task_count", text="关联任务数", anchor="center")
        self.course_tree.column("name", width=200)
        self.course_tree.column("instructor", width=120)
        self.course_tree.column("credits", width=80, anchor="center")
        self.course_tree.column("task_count", width=120, anchor="center")

        csbar = ttk.Scrollbar(cframe, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=csbar.set)
        self.course_tree.pack(side="left", fill="both", expand=True)
        csbar.pack(side="right", fill="y")

    # ========== 数据刷新 ==========

    def _refresh_all(self):
        self._refresh_dashboard()
        self._refresh_task_list()
        self._refresh_course_list()
        self._generate_plan()

    def _refresh_dashboard(self):
        stats = self.storage.get_stats()
        self.stat_cards["total"].config(text=str(stats["total_tasks"]))
        self.stat_cards["completed"].config(text=str(stats["completed_tasks"]))
        self.stat_cards["overdue"].config(text=str(stats["overdue_tasks"]))
        self.stat_cards["rate"].config(text=f"{stats['completion_rate']:.0%}")

    def _refresh_task_list(self):
        for row in self.task_tree.get_children():
            self.task_tree.delete(row)

        query = self.search_var.get().strip().lower()
        tasks = list(self.storage.tasks.values())

        # 使用 Trie 搜索
        if query:
            trie = self.storage.get_trie()
            matched_ids = set(trie.search(query))
            tasks = [t for t in tasks if t.id in matched_ids]

        # 排序：未完成优先，按紧急度
        tasks.sort(key=lambda t: (t.completed, t.urgency_score))

        for task in tasks:
            course_name = self.storage.courses.get(task.course_id, Course()).name
            deadline_str = task.deadline.strftime("%m/%d %H:%M") if task.deadline else "--"
            prereq_names = []
            for pid in task.prerequisites:
                pt = self.storage.tasks.get(pid)
                if pt:
                    prereq_names.append(pt.title[:8])
            prereq_str = ", ".join(prereq_names) if prereq_names else "--"

            tags = (task.title, course_name, deadline_str,
                    str(task.estimated_minutes), str(task.priority),
                    prereq_str, "✓" if task.completed else "○")

            item = self.task_tree.insert("", "end", values=tags, iid=task.id)

            if task.completed:
                self.task_tree.tag_configure("done", foreground=COLORS["muted"])
                self.task_tree.item(item, tags=("done",))
            elif task.is_overdue:
                self.task_tree.tag_configure("overdue", foreground=COLORS["overdue"])
                self.task_tree.item(item, tags=("overdue",))

    def _refresh_course_list(self):
        for row in self.course_tree.get_children():
            self.course_tree.delete(row)
        for course in self.storage.courses.values():
            count = sum(1 for t in self.storage.tasks.values() if t.course_id == course.id)
            self.course_tree.insert("", "end", iid=course.id,
                                    values=(course.name, course.instructor,
                                            str(course.credits), str(count)))

    # ========== 计划生成 ==========

    def _generate_plan(self):
        for row in self.plan_tree.get_children():
            self.plan_tree.delete(row)

        try:
            minutes = int(self.time_var.get())
        except ValueError:
            minutes = 480

        plan = self.planner.plan_today(minutes)

        self.plan_summary.config(
            text=f"已安排 {plan.total_planned_minutes} 分钟 "
                 f"(利用率 {plan.utilization:.0%}) | "
                 f"未安排 {len(plan.unplanned_tasks)} 个 | "
                 f"被阻塞 {len(plan.blocked_tasks)} 个"
        )

        for pt in plan.tasks:
            status = "🟡 逾期" if pt.is_overdue else "🟢 正常"
            item = self.plan_tree.insert("", "end", values=(
                pt.task.title, pt.course_name,
                str(pt.task.estimated_minutes), str(pt.task.priority),
                status
            ))
            if pt.is_overdue:
                self.plan_tree.tag_configure("plan_overdue", foreground=COLORS["overdue"])
                self.plan_tree.item(item, tags=("plan_overdue",))

    # ========== 搜索 ==========

    def _on_search(self):
        self._refresh_task_list()

    # ========== 任务操作 ==========

    def _add_task_dialog(self):
        dialog = TaskDialog(self.root, self.storage, title="添加任务")
        self.root.wait_window(dialog.top)
        if dialog.result:
            if self.storage.add_task(dialog.result):
                self._refresh_all()
            else:
                messagebox.showerror("错误", "添加任务失败，请检查输入数据")

    def _edit_task_dialog(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个任务")
            return
        task_id = selection[0]
        task = self.storage.tasks.get(task_id)
        if task is None:
            return
        dialog = TaskDialog(self.root, self.storage, task=task, title="编辑任务")
        self.root.wait_window(dialog.top)
        if dialog.result:
            self.storage.update_task(dialog.result)
            self._refresh_all()

    def _delete_task(self):
        selection = self.task_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("确认", "确定删除选中的任务吗？"):
            for tid in selection:
                self.storage.delete_task(tid)
            self._refresh_all()

    def _mark_task_complete(self):
        selection = self.task_tree.selection()
        if not selection:
            return
        for tid in selection:
            task = self.storage.tasks.get(tid)
            if task and task.completed:
                self.storage.mark_incomplete(tid)
            else:
                self.storage.mark_complete(tid)
        self._refresh_all()

    # ========== 课程操作 ==========

    def _add_course_dialog(self):
        dialog = CourseDialog(self.root, title="添加课程")
        self.root.wait_window(dialog.top)
        if dialog.result:
            self.storage.add_course(dialog.result)
            self._refresh_all()

    def _delete_course(self):
        selection = self.course_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("确认", "删除课程将同时删除其所有关联任务，确定吗？"):
            for cid in selection:
                self.storage.delete_course(cid)
            self._refresh_all()


# ==================== 对话框 ====================

class TaskDialog:
    """任务添加/编辑对话框（可滚动）"""

    COURSE_COLORS = ["#4A90D9", "#48BB78", "#ED8936", "#F56565", "#9F7AEA", "#38B2AC"]

    def __init__(self, parent, storage: Storage, task: Task = None, title: str = "任务"):
        self.storage = storage
        self.editing = task
        self.result: Task | None = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("520x600")
        self.top.minsize(420, 400)
        self.top.configure(bg=COLORS["card"])
        self.top.transient(parent)
        self.top.grab_set()

        # ---- 标题栏（固定） ----
        title_bar = tk.Frame(self.top, bg=COLORS["card"])
        title_bar.pack(fill="x", padx=20, pady=(15, 5))
        tk.Label(title_bar, text=title, font=FONT_TITLE, bg=COLORS["card"],
                 fg=COLORS["primary"]).pack()

        # ---- 可滚动区域 ----
        scroll_frame = tk.Frame(self.top, bg=COLORS["card"])
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        canvas = tk.Canvas(scroll_frame, bg=COLORS["card"], highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        self._form = tk.Frame(canvas, bg=COLORS["card"])

        self._form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.top.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ---- 表单内容 ----
        f = self._form

        # 任务标题
        tk.Label(f, text="任务标题 *", bg=COLORS["card"], font=FONT_SMALL,
                 fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        self.title_var = tk.StringVar(value=task.title if task else "")
        tk.Entry(f, textvariable=self.title_var, font=FONT_NORMAL).pack(fill="x", padx=20)

        # 所属课程
        tk.Label(f, text="所属课程", bg=COLORS["card"], font=FONT_SMALL,
                 fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        course_names = [c.name for c in storage.courses.values()]
        self.course_var = tk.StringVar()
        if task and task.course_id in storage.courses:
            self.course_var.set(storage.courses[task.course_id].name)
        self.course_combo = ttk.Combobox(f, textvariable=self.course_var,
                                         values=course_names, font=FONT_NORMAL, state="readonly")
        self.course_combo.pack(fill="x", padx=20)

        # 截止日期
        tk.Label(f, text="截止日期 (YYYY-MM-DD HH:MM)", bg=COLORS["card"],
                 font=FONT_SMALL, fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        dl_frame = tk.Frame(f, bg=COLORS["card"])
        dl_frame.pack(fill="x", padx=20)
        default_dl = task.deadline.strftime("%Y-%m-%d %H:%M") if task and task.deadline else ""
        self.deadline_var = tk.StringVar(value=default_dl)
        tk.Entry(dl_frame, textvariable=self.deadline_var, font=FONT_NORMAL, width=18).pack(side="left")
        tk.Button(dl_frame, text="今天", command=self._set_today,
                  bg=COLORS["primary"], fg="white", font=FONT_SMALL, relief="flat",
                  padx=8, cursor="hand2").pack(side="left", padx=3)
        tk.Button(dl_frame, text="明天", command=self._set_tomorrow,
                  bg=COLORS["primary"], fg="white", font=FONT_SMALL, relief="flat",
                  padx=8, cursor="hand2").pack(side="left")
        tk.Button(dl_frame, text="清除", command=lambda: self.deadline_var.set(""),
                  bg=COLORS["muted"], fg="white", font=FONT_SMALL, relief="flat",
                  padx=8, cursor="hand2").pack(side="left", padx=3)

        # 预计时间
        tk.Label(f, text="预计完成时间（分钟）", bg=COLORS["card"],
                 font=FONT_SMALL, fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        est_frame = tk.Frame(f, bg=COLORS["card"])
        est_frame.pack(fill="x", padx=20)
        self.est_var = tk.StringVar(value=str(task.estimated_minutes) if task else "60")
        self.est_label = tk.Label(est_frame, text="60 分钟", bg=COLORS["card"],
                                   font=FONT_SMALL, fg=COLORS["primary"], width=8, anchor="w")
        self.est_label.pack(side="right")
        scale = tk.Scale(est_frame, from_=5, to=480, orient="horizontal",
                         variable=self.est_var, bg=COLORS["card"],
                         length=350, resolution=5,
                         command=lambda v: self.est_label.config(text=f"{v} 分钟"))
        scale.pack(side="left", fill="x", expand=True)

        # 优先级
        tk.Label(f, text="优先级", bg=COLORS["card"],
                 font=FONT_SMALL, fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        prio_frame = tk.Frame(f, bg=COLORS["card"])
        prio_frame.pack(fill="x", padx=20)
        self.prio_var = tk.IntVar(value=task.priority if task else 3)
        for i in range(1, 6):
            tk.Radiobutton(prio_frame, text=str(i), variable=self.prio_var, value=i,
                           bg=COLORS["card"], font=FONT_SMALL,
                           selectcolor=COLORS["primary"]).pack(side="left", padx=10)

        # 描述
        tk.Label(f, text="描述", bg=COLORS["card"],
                 font=FONT_SMALL, fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        self.desc_text = tk.Text(f, height=3, font=FONT_NORMAL, wrap="word")
        self.desc_text.pack(fill="x", padx=20)
        if task:
            self.desc_text.insert("1.0", task.description)

        # 前置任务
        tk.Label(f, text="前置任务（按住Ctrl多选）", bg=COLORS["card"],
                 font=FONT_SMALL, fg=COLORS["fg"]).pack(anchor="w", pady=(8, 2), padx=20)
        task_options = [f"{t.title[:20]} ({t.id})" for t in storage.tasks.values()
                        if t != task and not t.completed]
        self.prereq_listbox = tk.Listbox(f, selectmode="multiple", height=4,
                                         font=FONT_SMALL, exportselection=False)
        self.prereq_listbox.pack(fill="x", padx=20)
        for opt in task_options:
            self.prereq_listbox.insert("end", opt)
        if task:
            for i, opt in enumerate(task_options):
                for pid in task.prerequisites:
                    if f"({pid})" in opt:
                        self.prereq_listbox.selection_set(i)

        # 底部留白
        tk.Frame(f, height=10, bg=COLORS["card"]).pack()

        # ---- 按钮栏（固定） ----
        btn_bar = tk.Frame(self.top, bg=COLORS["border"])
        btn_bar.pack(fill="x", side="bottom")
        btn_inner = tk.Frame(btn_bar, bg=COLORS["border"])
        btn_inner.pack(pady=10)
        tk.Button(btn_inner, text="取消", command=self.top.destroy,
                  bg="#CBD5E0", fg=COLORS["fg"], font=FONT_NORMAL,
                  relief="flat", padx=24, pady=8, cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn_inner, text="✓ 保存任务", command=self._save,
                  bg=COLORS["primary"], fg="white", font=("Microsoft YaHei", 11, "bold"),
                  relief="flat", padx=24, pady=8, cursor="hand2").pack(side="left", padx=8)

    def _set_today(self):
        self.deadline_var.set(datetime.now().strftime("%Y-%m-%d 23:59"))

    def _set_tomorrow(self):
        from datetime import timedelta
        tmr = datetime.now() + timedelta(days=1)
        self.deadline_var.set(tmr.strftime("%Y-%m-%d 23:59"))

    def _save(self):
        try:
            self._do_save()
        except Exception as e:
            messagebox.showerror("保存失败", f"发生错误: {str(e)}")

    def _do_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("验证失败", "任务标题不能为空")
            return

        # 解析截止日期
        deadline = None
        dl_str = self.deadline_var.get().strip()
        if dl_str:
            try:
                deadline = datetime.strptime(dl_str, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    deadline = datetime.strptime(dl_str, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("验证失败", "日期格式不正确，请使用 YYYY-MM-DD HH:MM")
                    return

        # 解析前置任务
        selected_indices = self.prereq_listbox.curselection()
        try:
            all_options = self.prereq_listbox.get(0, "end")
        except tk.TclError:
            all_options = []
        prerequisites = []
        for idx in selected_indices:
            opt = all_options[idx]
            # 从 "(task_id)" 中提取ID
            import re
            match = re.search(r"\(([^)]+)\)$", opt)
            if match:
                prerequisites.append(match.group(1))

        # 课程
        course_id = ""
        course_name = self.course_var.get()
        for c in self.storage.courses.values():
            if c.name == course_name:
                course_id = c.id
                break

        try:
            est = int(self.est_var.get())
        except (ValueError, tk.TclError):
            est = 60

        if self.editing:
            task = self.editing
            task.title = title
            task.course_id = course_id
            task.deadline = deadline
            task.estimated_minutes = est
            task.priority = self.prio_var.get()
            task.description = self.desc_text.get("1.0", "end-1c")
            task.prerequisites = prerequisites
        else:
            task = Task(
                title=title,
                course_id=course_id,
                deadline=deadline,
                estimated_minutes=est,
                priority=self.prio_var.get(),
                description=self.desc_text.get("1.0", "end-1c"),
                prerequisites=prerequisites,
            )

        self.result = task
        self.top.destroy()


class CourseDialog:
    """课程添加/编辑对话框"""

    def __init__(self, parent, course: Course = None, title: str = "课程"):
        self.editing = course
        self.result: Course | None = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.configure(bg=COLORS["card"])
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        tk.Label(self.top, text=title, font=FONT_TITLE, bg=COLORS["card"],
                 fg=COLORS["primary"]).pack(pady=(15, 15))

        form = tk.Frame(self.top, bg=COLORS["card"])
        form.pack(fill="both", expand=True, padx=30)

        tk.Label(form, text="课程名称 *", bg=COLORS["card"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        self.name_var = tk.StringVar(value=course.name if course else "")
        tk.Entry(form, textvariable=self.name_var, font=FONT_NORMAL, width=35).pack(fill="x")

        tk.Label(form, text="授课教师", bg=COLORS["card"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        self.inst_var = tk.StringVar(value=course.instructor if course else "")
        tk.Entry(form, textvariable=self.inst_var, font=FONT_NORMAL, width=35).pack(fill="x")

        tk.Label(form, text="学分", bg=COLORS["card"], font=FONT_SMALL).pack(anchor="w", pady=(8, 2))
        self.credits_var = tk.StringVar(value=str(course.credits) if course else "3")
        tk.Spinbox(form, from_=0, to=10, textvariable=self.credits_var,
                   font=FONT_NORMAL, width=10).pack(anchor="w")

        btn_frame = tk.Frame(form, bg=COLORS["card"])
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="取消", command=self.top.destroy,
                  bg=COLORS["border"], fg=COLORS["fg"], font=FONT_NORMAL,
                  relief="flat", padx=20, pady=6, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="保存", command=self._save,
                  bg=COLORS["primary"], fg="white", font=FONT_NORMAL,
                  relief="flat", padx=20, pady=6, cursor="hand2").pack(side="left", padx=5)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("验证失败", "课程名称不能为空")
            return
        try:
            credits = int(self.credits_var.get())
        except ValueError:
            credits = 0

        if self.editing:
            course = self.editing
            course.name = name
            course.instructor = self.inst_var.get().strip()
            course.credits = credits
        else:
            course = Course(
                name=name,
                instructor=self.inst_var.get().strip(),
                credits=credits,
            )
        self.result = course
        self.top.destroy()
