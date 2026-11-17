"""Screenshot capture script - launches GUI and auto-captures"""
import sys, os, shutil, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

src_demo = os.path.join(os.path.dirname(__file__), "..", "data", "demo_data.json")
dst_data = os.path.join(os.path.dirname(__file__), "..", "data", "studyflow.json")
shutil.copy(src_demo, dst_data)

from studyflow.gui import StudyFlowApp
import tkinter as tk
from PIL import ImageGrab

root = tk.Tk()
app = StudyFlowApp(root)
root.update()
root.deiconify()
time.sleep(2)
root.update()

screenshot_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
os.makedirs(screenshot_dir, exist_ok=True)

x = root.winfo_rootx()
y = root.winfo_rooty()
w = root.winfo_width()
h = root.winfo_height()

img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img.save(os.path.join(screenshot_dir, "dashboard.png"))
print(f"Dashboard: {w}x{h}")

app.notebook.select(1)
time.sleep(0.5)
root.update()
img2 = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img2.save(os.path.join(screenshot_dir, "tasks.png"))
print("Tasks saved")

app.notebook.select(2)
time.sleep(0.5)
root.update()
img3 = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img3.save(os.path.join(screenshot_dir, "courses.png"))
print("Courses saved")

root.destroy()
print("Done!")
