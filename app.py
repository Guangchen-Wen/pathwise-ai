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
    "start": "#10b981",
    "goal": "#f43f5e",
}

TEAM_ROLES = [
    ("Guangchen-Wen", "Project leader, integration, testing, README"),
    ("HXD3D0235", "UI layout and interactive grid editor"),
    ("Tim456-cell", "Terrain cost model and map generation"),
    ("persistkun", "A* and Dijkstra algorithm implementation"),
    ("0heh01", "BFS, Greedy search, heuristic comparison"),
    ("zixi0427feng-source", "Visualization, validation data, presentation"),
]


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
        style.configure("TCombobox", fieldbackground="#0f172a", background="#0f172a", foreground="#e5e7eb")
        style.configure("Treeview", background="#0f172a", fieldbackground="#0f172a", foreground="#e5e7eb", rowheight=25)
        style.configure("Treeview.Heading", background="#1e293b", foreground="#f8fafc", font=("Segoe UI", 9, "bold"))

    def _build_layout(self) -> None:
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
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Configure>", lambda _event: self.draw_grid())

        right_panel = ttk.Frame(body, style="Panel.TFrame")
        right_panel.pack(side="right", fill="y", padx=(12, 0))
        self._build_results(right_panel)

    def _section_label(self, parent: ttk.Frame, text: str) -> None:
        ttk.Label(parent, text=text, font=("Segoe UI", 11, "bold"), background="#111827", foreground="#f8fafc").pack(
            anchor="w", padx=12, pady=(14, 6)
        )

    def _build_controls(self, parent: ttk.Frame) -> None:
        parent.configure(width=250)
        parent.pack_propagate(False)

        self._section_label(parent, "Grid Size")
        size_frame = ttk.Frame(parent, style="Panel.TFrame")
        size_frame.pack(fill="x", padx=12)
        ttk.Label(size_frame, text="Rows").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(size_frame, from_=8, to=45, textvariable=self.rows, width=8).grid(row=0, column=1, padx=8, pady=3)
        ttk.Label(size_frame, text="Columns").grid(row=1, column=0, sticky="w")
        ttk.Spinbox(size_frame, from_=8, to=65, textvariable=self.cols, width=8).grid(row=1, column=1, padx=8, pady=3)
        ttk.Button(parent, text="Apply Grid Size", command=self.reset_grid).pack(fill="x", padx=12, pady=(8, 0))

        self._section_label(parent, "Edit Tool")
        tools = [
            ("Start", "start"),
            ("Goal", "goal"),
            ("Wall", "wall"),
            ("Normal cost 1", "normal"),
            ("Grass cost 3", "grass"),
            ("Water cost 5", "water"),
            ("Mountain cost 8", "mountain"),
        ]
        for text, value in tools:
            ttk.Radiobutton(parent, text=text, value=value, variable=self.selected_tool).pack(anchor="w", padx=14, pady=1)

        legend = ttk.Frame(parent, style="Panel.TFrame")
        legend.pack(fill="x", padx=12, pady=(8, 0))
        for index, terrain in enumerate(["normal", "grass", "water", "mountain", "wall"]):
            swatch = tk.Label(legend, width=2, height=1, bg=TERRAIN_COLORS[terrain])
            swatch.grid(row=index, column=0, sticky="w", pady=2)
            cost = TERRAIN_COSTS[terrain]
            label = "blocked" if cost is None else f"cost {cost}"
            ttk.Label(legend, text=f"{terrain.title()} - {label}").grid(row=index, column=1, sticky="w", padx=7)

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
    #Panel Layout Configuration
        parent.configure(width=330)
        parent.pack_propagate(False)
    #Current Result Section
        self._section_label(parent, "Current Result")
        self.status_label = ttk.Label(parent, text="Ready", style="Stat.TLabel")
        self.status_label.pack(anchor="w", padx=12)
        self.stats_text = tk.Text(parent, width=34, height=8, bg="#0f172a", fg="#e5e7eb", bd=0, font=("Consolas", 10))
        self.stats_text.pack(fill="x", padx=12, pady=(8, 0))
        self.stats_text.configure(state="disabled")
    # Data Table
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
        widths = {"algorithm": 112, "cost": 48, "length": 48, "visited": 58, "time": 58}
        for column in columns:
            self.compare_table.heading(column, text=headings[column])
            self.compare_table.column(column, width=widths[column], anchor="center")
        self.compare_table.pack(fill="x", padx=12, pady=(4, 0))
    #Team Roles Section
        self._section_label(parent, "Team Roles")
        roles_box = tk.Text(parent, width=34, height=12, bg="#0f172a", fg="#e5e7eb", bd=0, font=("Segoe UI", 9), wrap="word")
        roles_box.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        for name, role in TEAM_ROLES:
            roles_box.insert("end", f"{name}\n  {role}\n\n")
        roles_box.configure(state="disabled")

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
                # we distribute different kinds of lands by graudually increasing the value of "roll"
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
        self.apply_tool_at(event.x, event.y)

    def on_canvas_drag(self, event: tk.Event) -> None:
        if self.selected_tool.get() not in {"start", "goal"}:
            self.apply_tool_at(event.x, event.y)

    def apply_tool_at(self, x: int, y: int) -> None:
        position = self.position_from_xy(x, y)
        if position is None:
            return

        self.clear_search(draw=False)
        tool = self.selected_tool.get()
        row, col = position

        if tool == "start":
            if position != self.goal:
                self.start = position
                self.grid_data[row][col] = "normal"
        elif tool == "goal":
            if position != self.start:
                self.goal = position
                self.grid_data[row][col] = "normal"
        elif position not in [self.start, self.goal]:
            self.grid_data[row][col] = tool

        self.draw_grid()

    def position_from_xy(self, x: int, y: int) -> tuple[int, int] | None:
        total_cell = self.cell_size + self.cell_gap
        col = x // total_cell
        row = y // total_cell
        if 0 <= row < self.rows.get() and 0 <= col < self.cols.get():
            return int(row), int(col)
        return None

    def draw_grid(self) -> None:
        self.canvas.delete("all")           #Clear the canvas
        rows, cols = self.rows.get(), self.cols.get()
        available_w = max(1, self.canvas.winfo_width() - 16)
        available_h = max(1, self.canvas.winfo_height() - 16)
        self.cell_size = max(7, min(24, (available_w // cols) - self.cell_gap, (available_h // rows) - self.cell_gap))
        total_cell = self.cell_size + self.cell_gap
    #Double loop to draw every single cell on the grid
        for row in range(rows):
            for col in range(cols):
                x1 = col * total_cell + 4
                y1 = row * total_cell + 4
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                pos = (row, col)
                color = TERRAIN_COLORS[self.grid_data[row][col]]

                if pos in self.visited_display:
                    color = STATE_COLORS["visited"]
                if pos in self.path_display:
                    color = STATE_COLORS["path"]
                if pos == self.start:
                    color = STATE_COLORS["start"]
                if pos == self.goal:
                    color = STATE_COLORS["goal"]

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#18233a", width=1)
            #Draw the terrain movement cost number if the cell size is large enough
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
    #Run all algorithms simultaneously for benchmarking
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
    #Pick the algorithm with the lowest cost and least nodes visited
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
    #Animate the node exploration step-by-step
        def show_visited(index: int = 0) -> None:
            if index < len(result.visited_order):
                self.visited_display.add(result.visited_order[index])
                self.draw_grid()
                self.animation_job = self.after(delay, lambda: show_visited(index + 1))
                return
            show_path(0)
    #Trace out the final optimal path back to the start
        def show_path(index: int = 0) -> None:
            if index < len(result.path):
                self.path_display.add(result.path[index])
                self.draw_grid()
                self.animation_job = self.after(max(20, delay * 2), lambda: show_path(index + 1))
                return
            self.animation_job = None

        show_visited()  #Kick off animation loops

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
