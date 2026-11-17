"""
StudyFlow - 智能学习任务规划器
入口文件

运行方式：
    python src/main.py

或在 PyCharm 中直接运行此文件。
"""

import sys
import os

# 确保 src 目录在 sys.path 中，以便导入 studyflow 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from studyflow.gui import StudyFlowApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = StudyFlowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
