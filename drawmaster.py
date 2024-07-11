import tkinter as tk
from tkinter import filedialog
import pandas as pd
import math

class DrawingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DrawMaster")
        self.geometry("800x600")
        
        self.canvas = tk.Canvas(self, bg="darkgray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.mode = None
        self.start_x = None
        self.start_y = None
        self.points = []
        self.lines = []
        self.snap_distance = 20
        self.snap_rect = None
        self.selected_item = None
        self.history = []
        self.redo_stack = []
        
        self.create_toolbar()
        self.bind_events()
        
    def create_toolbar(self):
        toolbar = tk.Frame(self, bg="lightgray")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        point_button = tk.Button(toolbar, text="Draw Point", command=self.set_point_mode)
        point_button.pack(side=tk.LEFT)
        
        line_button = tk.Button(toolbar, text="Draw Line", command=self.set_line_mode)
        line_button.pack(side=tk.LEFT)
        
        upload_button = tk.Button(toolbar, text="Upload Excel", command=self.upload_excel)
        upload_button.pack(side=tk.LEFT)
        
        modify_toolbar = tk.Frame(self, bg="lightgray")
        modify_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        undo_button = tk.Button(modify_toolbar, text="Undo", command=self.undo)
        undo_button.pack(side=tk.LEFT)
        
        redo_button = tk.Button(modify_toolbar, text="Redo", command=self.redo)
        redo_button.pack(side=tk.LEFT)
        
        select_button = tk.Button(modify_toolbar, text="Select", command=self.set_select_mode)
        select_button.pack(side=tk.LEFT)
        
        delete_button = tk.Button(modify_toolbar, text="Delete", command=self.delete_selected)
        delete_button.pack(side=tk.LEFT)
        
        move_button = tk.Button(modify_toolbar, text="Move", command=self.set_move_mode)
        move_button.pack(side=tk.LEFT)
        
        copy_button = tk.Button(modify_toolbar, text="Copy", command=self.copy_selected)
        copy_button.pack(side=tk.LEFT)
        
    def set_point_mode(self):
        self.mode = "point"
        
    def set_line_mode(self):
        self.mode = "line"
        
    def set_select_mode(self):
        self.mode = "select"
        
    def set_move_mode(self):
        self.mode = "move"
        
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)
        
    def on_click(self, event):
        snap_x, snap_y = self.get_snapped_coordinates(event.x, event.y)
        if self.mode == "point":
            self.draw_point(snap_x, snap_y)
        elif self.mode == "line":
            self.start_x, self.start_y = snap_x, snap_y
        elif self.mode == "select":
            self.select_item(event.x, event.y)
        elif self.mode == "move" and self.selected_item:
            self.start_x, self.start_y = event.x, event.y
            
    def on_drag(self, event):
        snap_x, snap_y = self.get_snapped_coordinates(event.x, event.y)
        if self.mode == "line" and self.start_x is not None and self.start_y is not None:
            self.canvas.delete("preview_line")
            self.canvas.create_line(self.start_x, self.start_y, snap_x, snap_y, fill="white", tags="preview_line")
        elif self.mode == "move" and self.selected_item and self.start_x is not None and self.start_y is not None:
            self.move_selected(event.x, event.y)
            
    def on_release(self, event):
        snap_x, snap_y = self.get_snapped_coordinates(event.x, event.y)
        if self.mode == "line" and self.start_x is not None and self.start_y is not None:
            self.canvas.delete("preview_line")
            self.draw_line(self.start_x, self.start_y, snap_x, snap_y)
            self.start_x, self.start_y = None, None
        elif self.mode == "move" and self.selected_item:
            self.history.append(("move", self.selected_item))
            self.redo_stack.clear()
            self.start_x, self.start_y = None, None
            
    def on_motion(self, event):
        self.update_snap_indicator(event.x, event.y)
        
    def draw_point(self, x, y):
        r = 2  # radius of the point
        item = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", tags="point")
        self.canvas.create_text(x + 10, y - 10, text=f"({x}, {y})", anchor="nw", font=("Arial", 10), fill="white", tags="point")
        self.points.append((item, x, y))
        self.history.append(("point", item))
        self.redo_stack.clear()
        
    def draw_line(self, x1, y1, x2, y2):
        item = self.canvas.create_line(x1, y1, x2, y2, fill="white", tags="line")
        self.canvas.create_text(x1 + 10, y1 - 10, text=f"({x1}, {y1})", anchor="nw", font=("Arial", 10), fill="white", tags="line")
        self.canvas.create_text(x2 + 10, y2 - 10, text=f"({x2}, {y2})", anchor="nw", font=("Arial", 10), fill="white", tags="line")
        self.lines.append((item, x1, y1, x2, y2))
        self.history.append(("line", item))
        self.redo_stack.clear()
        
    def update_snap_indicator(self, x, y):
        nearest_point = self.find_nearest_point(x, y)
        if nearest_point:
            snap_x, snap_y = nearest_point
            if self.snap_rect:
                self.canvas.delete(self.snap_rect)
            self.snap_rect = self.canvas.create_rectangle(
                snap_x-5, snap_y-5, snap_x+5, snap_y+5, outline="red", tags="snap_indicator"
            )
        else:
            if self.snap_rect:
                self.canvas.delete(self.snap_rect)
                self.snap_rect = None
            
    def get_snapped_coordinates(self, x, y):
        nearest_point = self.find_nearest_point(x, y)
        if nearest_point:
            return nearest_point
        return x, y
        
    def find_nearest_point(self, x, y):
        min_dist = float('inf')
        nearest_point = None
        for item, px, py in self.points:
            dist = math.hypot(px - x, py - y)
            if dist < min_dist:
                min_dist = dist
                nearest_point = (px, py)
        for item, x1, y1, x2, y2 in self.lines:
            for px, py in [(x1, y1), (x2, y2)]:
                dist = math.hypot(px - x, py - y)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = (px, py)
        if min_dist <= self.snap_distance:  # snap threshold distance
            return nearest_point
        return None
    
    def select_item(self, x, y):
        self.deselect_item()
        item = self.canvas.find_closest(x, y)[0]
        if item:
            self.selected_item = item
            self.canvas.itemconfig(item, fill="blue")
            
    def deselect_item(self):
        if self.selected_item:
            item_type = self.canvas.type(self.selected_item)
            if item_type == "oval":
                self.canvas.itemconfig(self.selected_item, fill="white")
            elif item_type == "line":
                self.canvas.itemconfig(self.selected_item, fill="white")
            self.selected_item = None
            
    def delete_selected(self):
        if self.selected_item:
            self.canvas.delete(self.selected_item)
            self.history.append(("delete", self.selected_item))
            self.redo_stack.clear()
            self.deselect_item()
            
    def move_selected(self, x, y):
        if self.selected_item:
            dx = x - self.start_x
            dy = y - self.start_y
            self.canvas.move(self.selected_item, dx, dy)
            self.start_x, self.start_y = x, y
            
    def copy_selected(self):
        if self.selected_item:
            item_type = self.canvas.type(self.selected_item)
            if item_type == "oval":
                x0, y0, x1, y1 = self.canvas.coords(self.selected_item)
                new_item = self.canvas.create_oval(x0, y0, x1, y1, fill="white", tags="point")
                self.points.append((new_item, (x0 + x1) // 2, (y0 + y1) // 2))
            elif item_type == "line":
                x0, y0, x1, y1 = self.canvas.coords(self.selected_item)
                new_item = self.canvas.create_line(x0, y0, x1, y1, fill="white", tags="line")
                self.lines.append((new_item, x0, y0, x1, y1))
            self.history.append(("copy", new_item))
            self.redo_stack.clear()
            
    def undo(self):
        if not self.history:
            return
        action, item = self.history.pop()
        if action in ("point", "line", "delete", "copy"):
            self.redo_stack.append((action, item))
            self.canvas.delete(item)
        elif action == "move":
            self.redo_stack.append((action, item))
            # Movement undo logic should be implemented
        self.deselect_item()
        
    def redo(self):
        if not self.redo_stack:
            return
        action, item = self.redo_stack.pop()
        if action in ("point", "line", "delete", "copy"):
            self.history.append((action, item))
            # Redo logic should be implemented
        elif action == "move":
            self.history.append((action, item))
            # Movement redo logic should be implemented
        self.deselect_item()
        
    def upload_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.load_coordinates_from_excel(file_path)
    
    def load_coordinates_from_excel(self, file_path):
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            x, y = row['x'], row['y']
            self.draw_point(x, y)
        
if __name__ == "__main__":
    app = DrawingApp()
    app.mainloop()
