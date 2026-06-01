"""PathWise AI desktop application.

Run with:
    python app.py
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk, messagebox

from pathfinding import Grid, SearchResult, TERRAIN_COSTS, run_all_algorithms, run_search


TERRAIN_COLORS = {
    "normal": "#1b2440",
    "grass": "#55d07a",
    "water": "#38bdf8",
    "mountain": "#a78bfa",
    "wall": "#050816",
}

STATE_COLORS = {
    "visited": "#7c3aed",
    "path": "#ffd60a",
    "start": "#ffffff",
    "goal": "#f43f5e",
}


class PathWiseApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PathWise AI - Weighted Pathfinding Visualizer")
        self.geometry("1220x760")
        self.minsize(1050, 680)
        self.configure(bg="#090d18")

        self.rows = tk.IntVar(value=22)
        self.cols = tk.IntVar(value=36)
        self.algorithm = tk.StringVar(value="A*")
        self.heuristic = tk.StringVar(value="Manhattan")
        self.selected_tool = tk.StringVar(value="wall")
        self.speed = tk.IntVar(value=12)

        self.grid_data: Grid = []
        self.start = (10, 4)
        self.goal = (10, 31)
        self.cell_size = 20
        self.cell_gap = 2
        self.animation_job: str | None = None
        self.last_result: SearchResult | None = None
        self.visited_display: set[tuple[int, int]] = set()
        self.path_display: set[tuple[int, int]] = set()

        self._build_styles()
        self._build_layout()
        self.reset_grid()
        self.option_add('*TCombobox*Listbox.background', '#0f172a')
        self.option_add('*TCombobox*Listbox.foreground', '#ffffff')

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#090d18")
        style.configure("Panel.TFrame", background="#111827", relief="flat")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#090d18", foreground="#f8fafc", font=("Segoe UI", 18, "bold"))
        style.configure("Muted.TLabel", background="#111827", foreground="#94a3b8", font=("Segoe UI", 9))
        style.configure("Stat.TLabel", background="#111827", foreground="#facc15", font=("Segoe UI", 13, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("TRadiobutton", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 9))
        style.configure("TCheckbutton", background="#111827", foreground="#e5e7eb")
        style.configure("TCombobox", fieldbackground="#050816", background="#1e293b", foreground="#ffffff",padding=5)
        style.map("TCombobox",fieldbackground=[("readonly", "#0f172a")],selectbackground=[("readonly", "#1e293b")],
                  selectforeground=[("readonly", "#ffffff")])
        style.configure("Treeview", background="#0f172a", fieldbackground="#0f172a", foreground="#e5e7eb", rowheight=25)
        style.configure("Treeview.Heading", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 9, "bold"))

    def _build_layout(self) -> None:
         #Set up the top header area to hold the title and subtitle
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=18, pady=(14, 8))
        ttk.Label(header, text="PathWise AI", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="Weighted grid pathfinding with A*, Dijkstra, BFS and Greedy Best-First Search",
            background="#090d18",
            foreground="#94a3b8",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=18)
        self.toggle_btn = ttk.Button(header, text="Hide Results ➔", command=self.toggle_right_panel)
        self.toggle_btn.pack(side="right")

        #Make the main body container for our 3-column setup
        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        left_panel = ttk.Frame(body, style="Panel.TFrame")
        left_panel.pack(side="left", fill="y", padx=(0, 12))
        self._build_controls(left_panel)

        center = ttk.Frame(body, style="TFrame")
        center.pack(side="left", fill="both", expand=True)

        canvas_shell = tk.Frame(center, bg="#0b1020", bd=0, highlightthickness=1, highlightbackground="#1f2a44")
        canvas_shell.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_shell, bg="#0b1020", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)

        #Listen for mouse clicks, drags, and window resizing so the grid updates automatically
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Configure>", lambda _event: self.draw_grid())

        self.right_panel = ttk.Frame(body, style="Panel.TFrame")
        self.right_panel.pack(side="right", fill="y", padx=(12, 0))
        self._build_results(self.right_panel)

        self.right_panel_visible = True



    def _section_label(self, parent: ttk.Frame, text: str) -> None:
        #A quick helper function so all our side panel headers look the same
        ttk.Label(parent, text=text, font=("Segoe UI", 11, "bold"), background="#111827", foreground="#f8fafc").pack(
            anchor="w", padx=12, pady=(14, 6)
        )

    def _build_controls(self, parent: ttk.Frame) -> None:
        parent.configure(width=250)
        parent.pack_propagate(False) #Stop the stuff inside from stretching or squishing the panel
        
        #Grid Size settings
        self._section_label(parent, "Grid Size")
        size_frame = ttk.Frame(parent, style="Panel.TFrame")
        size_frame.pack(fill="x", padx=12)
        ttk.Label(size_frame, text="Rows").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(size_frame, from_=8, to=45, textvariable=self.rows, width=8).grid(row=0, column=1, padx=8, pady=3)
        ttk.Label(size_frame, text="Columns").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(size_frame, from_=8, to=65, textvariable=self.cols, width=8).grid(row=1, column=1, padx=8, pady=3)
        ttk.Button(parent, text="Apply Grid Size", command=self.reset_grid).pack(fill="x", padx=12, pady=(8, 0))

        #Grid Editing Tools
        self._section_label(parent, "Edit Tools & Legend")
        tool_frame = ttk.Frame(parent, style="Panel.TFrame")
        tool_frame.pack(fill="x", padx=12, pady=(0, 8))

        tools_info = [
            ("start", "Start Point", STATE_COLORS["start"]),
            ("goal", "Goal Point", STATE_COLORS["goal"]),
            ("normal", "Normal - cost 1", TERRAIN_COLORS["normal"]),
            ("grass", "Grass - cost 3", TERRAIN_COLORS["grass"]),
            ("water", "Water - cost 5", TERRAIN_COLORS["water"]),
            ("mountain", "Mountain - cost 8", TERRAIN_COLORS["mountain"]),
            ("wall", "Wall - blocked", TERRAIN_COLORS["wall"]),
        ]

        for i, (val, text, color) in enumerate(tools_info):
            swatch = tk.Label(tool_frame, width=2, height=1, bg=color, bd=0)
            swatch.grid(row=i, column=0, pady=4, padx=(0, 10), sticky="w")
            ttk.Radiobutton(
                tool_frame,
                text=text,
                value=val,
                variable=self.selected_tool
            ).grid(row=i, column=1, sticky="w")

        self._section_label(parent, "Algorithm")
        ttk.Combobox(
            parent,
            textvariable=self.algorithm,
            state="readonly",
            values=["A*", "Dijkstra", "BFS", "Greedy Best-First"],
        ).pack(fill="x", padx=12)
        ttk.Combobox(
            parent,
            textvariable=self.heuristic,
            state="readonly",
            values=["Manhattan", "Euclidean", "Chebyshev"],
        ).pack(fill="x", padx=12, pady=(8, 0))

        ttk.Label(parent, text="Animation Speed", style="Muted.TLabel").pack(anchor="w", padx=12, pady=(10, 0))
        ttk.Scale(parent, from_=1, to=30, variable=self.speed, orient="horizontal").pack(fill="x", padx=12)

        buttons = ttk.Frame(parent, style="Panel.TFrame")
        buttons.pack(fill="x", padx=12, pady=(12, 0))
        ttk.Button(buttons, text="Run Search", command=self.run_selected).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Compare All", command=self.compare_all).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Random Map", command=self.random_map).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Clear Search", command=self.clear_search).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Clear All", command=self.reset_grid).pack(fill="x", pady=3)
    def _build_results(self, parent: ttk.Frame) -> None:
        parent.configure(width=330)
        parent.pack_propagate(False)

        self._section_label(parent, "Current Result")
        self.status_label = ttk.Label(parent, text="Ready", style="Stat.TLabel")
        self.status_label.pack(anchor="w", padx=12)
        self.stats_text = tk.Text(parent, width=34, height=8, bg="#0f172a", fg="#e5e7eb", bd=0, font=("Consolas", 10))
        self.stats_text.pack(fill="x", padx=12, pady=(8, 0))
        self.stats_text.configure(state="disabled")

        self._section_label(parent, "Algorithm Comparison")
        columns = ("algorithm", "cost", "length", "visited", "time")
        self.compare_table = ttk.Treeview(parent, columns=columns, show="headings", height=6)
        headings = {
            "algorithm": "Algorithm",
            "cost": "Cost",
            "length": "Steps",
            "visited": "Visited",
            "time": "ms",
        }
        widths = {"algorithm": 98, "cost": 44, "length": 48, "visited": 56, "time": 54}
        for column in columns:
            self.compare_table.heading(column, text=headings[column])
            self.compare_table.column(column, width=widths[column], anchor="center")
        self.compare_table.pack(fill="x", padx=12, pady=(4, 0))

    def toggle_right_panel(self) -> None:
        if self.right_panel_visible:
            self.right_panel.pack_forget()
            self.toggle_btn.configure(text="⬅ Show Results")
            self.right_panel_visible = False
        else:
            self.right_panel.pack(side="right", fill="y", padx=(12, 0))
            self.toggle_btn.configure(text="Hide Results ➔")
            self.right_panel_visible = True
        self.after(20, self.draw_grid)


    def reset_grid(self) -> None:
        self.stop_animation()
        rows = max(8, min(45, self.rows.get()))
        cols = max(8, min(65, self.cols.get()))
        self.rows.set(rows)
        self.cols.set(cols)
        self.grid_data = [["normal" for _ in range(cols)] for _ in range(rows)]
        self.start = (rows // 2, max(1, cols // 8))
        self.goal = (rows // 2, min(cols - 2, cols - cols // 8 - 1))
        self.clear_search(draw=False)
        self.draw_grid()

    def clear_search(self, draw: bool = True) -> None:
        self.stop_animation()
        self.visited_display.clear()
        self.path_display.clear()
        self.last_result = None
        self.status_label.configure(text="Ready")
        self._write_stats("Choose tools on the left, edit the grid, then run a search.")
        if draw:
            self.draw_grid()

# generate the map randomly
    def random_map(self) -> None:
        self.stop_animation()
        for row in range(self.rows.get()):
            for col in range(self.cols.get()):
                pos = (row, col)

                # in order to prevent that the beginning point and ending point covered by scanning, we should remove it 
                if pos in [self.start, self.goal]:
                    continue
                # introduce uniform distribution to randomly generate new map
                roll = random.random()
                if roll < 0.18:
                    self.grid_data[row][col] = "wall"
                elif roll < 0.28:
                    self.grid_data[row][col] = "grass"
                elif roll < 0.36:
                    self.grid_data[row][col] = "water"
                elif roll < 0.42:
                    self.grid_data[row][col] = "mountain"
                else:
                    self.grid_data[row][col] = "normal"
        self.clear_search(draw=False)
        self.draw_grid()

    def on_canvas_click(self, event: tk.Event) -> None:
        #This runs whenever you left-click on the canvas
        self.apply_tool_at(event.x, event.y)

    def on_canvas_drag(self, event: tk.Event) -> None:
        #This runs when  click and drag. 
        #Skipping 'start' and 'goal' so you don't accidentally draw a whole line of them
        if self.selected_tool.get() not in {"start", "goal"}:
            self.apply_tool_at(event.x, event.y)

    def apply_tool_at(self, x: int, y: int) -> None:
        #Figure out which grid cell is clicked based on the mouse's position
        position = self.position_from_xy(x, y)
        if position is None:
            return #If clicking is outside the grid, just bail out
            
        #Wipe out any old path lines if we edit the map
        self.clear_search(draw=False)
        tool = self.selected_tool.get()
        row, col = position

        #Special rules for placing the Start and Goal points
        if tool == "start":
            if position != self.goal:
                self.start = position
                self.grid_data[row][col] = "normal"
        elif tool == "goal":
            if position != self.start:
                self.goal = position
                self.grid_data[row][col] = "normal"
        #For everything else, like walls and grass        
        elif position not in [self.start, self.goal]:
            self.grid_data[row][col] = tool
        #Redraw the grid to show the new changes
        self.draw_grid()

    def position_from_xy(self, x: int, y: int) -> tuple[int, int] | None:
        #Calculate the cell size and gaps to find the right row and column
        total_cell = self.cell_size + self.cell_gap
        col = x // total_cell
        row = y // total_cell
        #Make sure the row and column actually exist on the grid
        if 0 <= row < self.rows.get() and 0 <= col < self.cols.get():
            return int(row), int(col)
        return None

    def draw_grid(self) -> None:
        #Wipe the canvas clean before redrawing
        self.canvas.delete("all")
        rows, cols = self.rows.get(), self.cols.get()
        #Find out how much space we have, minus a little padding
        available_w = max(1, self.canvas.winfo_width() - 16)
        available_h = max(1, self.canvas.winfo_height() - 16)
        self.cell_size = max(7, min(24, (available_w // cols) - self.cell_gap, (available_h // rows) - self.cell_gap))
        total_cell = self.cell_size + self.cell_gap

        #Go through every single cell in our data and draw it
        for row in range(rows):
            for col in range(cols):
                #Find the top-left and bottom-right corners for the rectangle
                x1 = col * total_cell + 4
                y1 = row * total_cell + 4
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                pos = (row, col)
                color = TERRAIN_COLORS[self.grid_data[row][col]]

                #Change the color if it's the start, goal, or part of the found path
                if pos in self.visited_display:
                    color = STATE_COLORS["visited"]
                if pos in self.path_display:
                    color = STATE_COLORS["path"]
                if pos == self.start:
                    color = STATE_COLORS["start"]
                if pos == self.goal:
                    color = STATE_COLORS["goal"]

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#18233a", width=1)
                #Draw the cost number on top of rough terrain, unless a path is already covering it
                if self.grid_data[row][col] in {"grass", "water", "mountain"} and pos not in self.path_display:
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(TERRAIN_COSTS[self.grid_data[row][col]]),
                        fill="#0f172a",
                        font=("Segoe UI", max(6, self.cell_size // 2), "bold"),
                    )

    def run_selected(self) -> None:
        self.stop_animation()
        result = run_search(self.grid_data, self.start, self.goal, self.algorithm.get(), self.heuristic.get())
        self.last_result = result
        self.status_label.configure(text="Path Found" if result.found else "No Path")
        self._write_result(result)
        self.animate_result(result)

    def compare_all(self) -> None:
        self.stop_animation()
        for item in self.compare_table.get_children():
            self.compare_table.delete(item)

        results = run_all_algorithms(self.grid_data, self.start, self.goal, self.heuristic.get())
        for result in results:
            self.compare_table.insert(
                "",
                "end",
                values=(
                    result.algorithm,
                    result.total_cost if result.found else "-",
                    result.path_length if result.found else "-",
                    result.explored_nodes,
                    f"{result.runtime_ms:.2f}",
                ),
            )

        best = min((result for result in results if result.found), key=lambda item: (item.total_cost, item.explored_nodes), default=None)
        if best:
            self.last_result = best
            self.status_label.configure(text=f"Best: {best.algorithm}")
            self._write_result(best)
            self.animate_result(best)
        else:
            self.status_label.configure(text="No Path")
            self._write_stats("No algorithm found a valid path.")

    def animate_result(self, result: SearchResult) -> None:
        self.visited_display.clear()
        self.path_display.clear()
        delay = max(5, int(220 / self.speed.get()))

        def show_visited(index: int = 0) -> None:
            if index < len(result.visited_order):
                self.visited_display.add(result.visited_order[index])
                self.draw_grid()
                self.animation_job = self.after(delay, lambda: show_visited(index + 1))
                return
            show_path(0)

        def show_path(index: int = 0) -> None:
            if index < len(result.path):
                self.path_display.add(result.path[index])
                self.draw_grid()
                self.animation_job = self.after(max(20, delay * 2), lambda: show_path(index + 1))
                return
            self.animation_job = None

        show_visited()

    def stop_animation(self) -> None:
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None

    def _write_stats(self, text: str) -> None:
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("end", text)
        self.stats_text.configure(state="disabled")

    def _write_result(self, result: SearchResult) -> None:
        lines = [
            f"Algorithm : {result.algorithm}",
            f"Heuristic : {result.heuristic}",
            f"Found     : {result.found}",
            f"Cost      : {result.total_cost}",
            f"Steps     : {result.path_length}",
            f"Visited   : {result.explored_nodes}",
            f"Frontier  : {result.frontier_max}",
            f"Time      : {result.runtime_ms:.2f} ms",
        ]
        if result.note:
            lines.append(f"Note      : {result.note}")
        self._write_stats("\n".join(lines))


if __name__ == "__main__":
    try:
        app = PathWiseApp()
        app.mainloop()
    except tk.TclError as exc:
        messagebox.showerror("PathWise AI", f"Unable to start Tkinter: {exc}")
