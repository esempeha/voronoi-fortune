"""
Voronoi Diagram Interactive GUI Application

This file provides a graphical user interface for creating and visualizing Voronoi diagram,
users can add points manually, load points from file, generate random points,
and see the resulting Voronoi diagram (with largest empty circles being shown)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Tuple
import random
from voronoi import Voronoi

class MainApp:
    """Main application window for Voronoi diagram visualization"""

    # Constants
    CANVAS_WIDTH, CANVAS_HEIGHT = 600, 600
    POINT_RADIUS = 2
    BUTTON_WIDTH = 20
    FONT_STYLE = ("Helvetica", 12, "bold")
    BG_COLOR = "lightblue"
    
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the main window and all UI components"""
        self.master = master
        self.master.title("Voronoi Diagram")
        self.master.configure(bg=self.BG_COLOR)
        
        self.points: List[Tuple[float, float]] = []  # List of points (x, y)
        self.circles: List[Tuple[float, float, float]] = []  # List of circles (x, y, radius)
        
        self._create_layout()
        self._setup_bindings()

    def _create_layout(self) -> None:
        """Create and organize all GUI elements"""
        self._create_container()
        self._create_left_panel()
        self._create_canvas()
        self._create_bottom_panel()
        self._create_status_bar()

    def _create_container(self) -> None:
        """Create main container frame"""
        self.container = tk.Frame(self.master, bg=self.BG_COLOR)
        self.container.pack(fill=tk.BOTH, expand=True)

    def _create_left_panel(self) -> None:
        """Create left control panel with input fields and point list"""
        self.left_panel = tk.Frame(self.container, relief=tk.RAISED, borderwidth=1, bg=self.BG_COLOR)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Title
        tk.Label(self.left_panel, text="Voronoi Diagram", 
                font=("Helvetica", 16, "bold"), bg=self.BG_COLOR).pack(pady=10)

        # Manual input frame
        self._create_input_frame()
        
        # Points list
        self._create_points_list()

    def _create_input_frame(self) -> None:
        """Create frame for manual point input"""
        input_frame = tk.LabelFrame(self.left_panel, text="Add Point Manually", 
                                  padx=5, pady=5, bg=self.BG_COLOR)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # X coordinate
        tk.Label(input_frame, text="X:", bg=self.BG_COLOR).grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(input_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)

        # Y coordinate
        tk.Label(input_frame, text="Y:", bg=self.BG_COLOR).grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(input_frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)

        # Add button
        tk.Button(input_frame, text="Add Point", command=self.add_manual_point,
                 bg="cornflower blue", fg="white", font=self.FONT_STYLE).grid(row=0, column=4, padx=5)

    def _create_points_list(self) -> None:
        """Create listbox for displaying points"""
        points_frame = tk.LabelFrame(self.left_panel, text="Points List", padx=5, pady=5)
        points_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.points_listbox = tk.Listbox(points_frame, height=10)
        scrollbar = tk.Scrollbar(points_frame, orient=tk.VERTICAL)
        
        self.points_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.points_listbox.yview)
        
        self.points_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Delete specific point button
        tk.Button(self.left_panel, text="Delete Selected Point", width=30,
                 command=self.delete_selected_point,
                 bg="maroon", fg="white", font=self.FONT_STYLE).pack(pady=5)

    def _create_canvas(self) -> None:
        """Create drawing canvas"""
        canvas_frame = tk.Frame(self.container, width=self.CANVAS_WIDTH,
                              height=self.CANVAS_HEIGHT, bg=self.BG_COLOR)
        canvas_frame.pack_propagate(False)
        canvas_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, width=self.CANVAS_WIDTH,
                              height=self.CANVAS_HEIGHT, background='white',
                              relief=tk.SUNKEN, bd=2, highlightthickness=1)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

    def _create_bottom_panel(self) -> None:
        """Create bottom control panel with action buttons"""
        control_panel = tk.Frame(self.master, bg=self.BG_COLOR)
        control_panel.pack(fill=tk.X, pady=5)

        buttons_frame = tk.Frame(control_panel, bg=self.BG_COLOR)
        buttons_frame.pack(expand=True)

        # Create action buttons
        self._create_action_buttons(buttons_frame)

    def _create_action_buttons(self, parent: tk.Frame) -> None:
        """Create all action buttons"""
        buttons = [
            ("Clear All", "maroon", self.on_click_clear),
            ("Load Point(s)", "cornflower blue", self.load_points_from_file),
            ("Random Points", "sea green", self.generate_random_points),
            ("Save Point(s)", "snow4", self.save_points_to_file)
        ]

        for text, color, command in buttons:
            tk.Button(parent, text=text, width=self.BUTTON_WIDTH,
                     command=command, bg=color, fg="white",
                     font=self.FONT_STYLE).pack(side=tk.LEFT, padx=5)

    def _create_status_bar(self) -> None:
        """Create status bar for displaying messages"""
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.master, textvariable=self.status_var,
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                 bg=self.BG_COLOR)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_bindings(self) -> None:
        """Setup event bindings"""
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Motion>', self.on_mouse_move)

    def add_manual_point(self) -> None:
        """Add a point manually from input fields"""
        try:
            x = float(f"{float(self.x_entry.get()):.1f}")
            y = float(f"{float(self.y_entry.get()):.1f}")
            if 0 <= x <= self.CANVAS_WIDTH and 0 <= y <= self.CANVAS_HEIGHT:
                self.add_point((x, y))
                self.x_entry.delete(0, tk.END)
                self.y_entry.delete(0, tk.END)
                self.update_points_list()
            else:
                messagebox.showwarning("Invalid Input", f"Coordinates must be within 0-{self.CANVAS_WIDTH} for X and 0-{self.CANVAS_HEIGHT} for Y")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical coordinates")

    def delete_selected_point(self) -> None:
        """Delete the selected point from the list"""
        selection = self.points_listbox.curselection()
        if selection:
            index = selection[0]
            del self.points[index]
            self.redraw_all()
            self.update_points_list()

    def update_points_list(self) -> None:
        """Update the listbox with current points"""
        self.points_listbox.delete(0, tk.END)
        for i, point in enumerate(self.points):
            self.points_listbox.insert(tk.END, f"Point {i+1}: ({point[0]:.1f}, {point[1]:.1f})")

    def save_points_to_file(self) -> None:
        """Save current points to a file"""
        if not self.points:
            messagebox.showwarning("Warning", "No points to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Points"
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    for point in self.points:
                        file.write(f"{point[0]}, {point[1]}\n")
                self.status_var.set(f"Saved {len(self.points)} points to file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save points: {e}")

    def on_mouse_move(self, event: tk.Event) -> None:
        """Update status bar with mouse coordinates"""
        math_point = self._gui_to_math((event.x, event.y))
        x = float(f"{math_point[0]:.1f}")
        y = float(f"{math_point[1]:.1f}")
        self.status_var.set(f"Mouse position: ({x:.1f}, {y:.1f})")

    def add_point(self, point: Tuple[float, float]) -> None:
        """Add a point to the list and update the canvas"""
        x = float(f"{point[0]:.1f}")
        y = float(f"{point[1]:.1f}")
        
        if 0 <= x <= self.CANVAS_WIDTH and 0 <= y <= self.CANVAS_HEIGHT:
            self.points.append((x, y))
            self.update_points_list()
            self.redraw_all()
            self.status_var.set(f"Added point at ({x:.1f}, {y:.1f})")
        else:
            messagebox.showwarning("Invalid Point", 
                f"Point must be within canvas bounds (0-{self.CANVAS_WIDTH}, 0-{self.CANVAS_HEIGHT})")

    def redraw_all(self) -> None:
        """Redraw all elements on the canvas"""
        self.canvas.delete(tk.ALL)
        for point in self.points:
            gui_point = self._math_to_gui(point)
            self.canvas.create_oval(
                gui_point[0] - 3,
                gui_point[1] - 3,
                gui_point[0] + 3,
                gui_point[1] + 3,
                fill="black"
            )
        if len(self.points) >= 2:
            self.on_click_calculate()

    def on_click_calculate(self) -> None:
        """Calculate and draw the Voronoi diagram"""
        if len(self.points) >= 2:
            try:                
                voronoi = Voronoi(self.points, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
                voronoi.generate_voronoi_diagram()
                lines = voronoi.get_voronoi_line_segments()
                
                if len(self.points) >= 2:
                    self.draw_lines_on_canvas(lines)
                
                if len(self.points) >= 3:
                    largest_empty_circles = voronoi.get_largest_empty_circles()
                    
                    for center, radius, points in largest_empty_circles:
                        gui_center = self._math_to_gui((center.x, center.y))
                        cx, cy = gui_center
                        
                        self.canvas.create_oval(
                            cx - radius, cy - radius,
                            cx + radius, cy + radius,
                            outline='red', width=2, tags="circle"
                        )
                        self.canvas.create_oval(
                            cx - 4, cy - 4,
                            cx + 4, cy + 4,
                            fill="red", tags="circle"
                        )
                        for p in points:
                            gui_p = self._math_to_gui((p.x, p.y))
                            self.canvas.create_oval(
                                gui_p[0] - 4, gui_p[1] - 4,
                                gui_p[0] + 4, gui_p[1] + 4,
                                fill="green", tags="circle"
                            )
                
                self.status_var.set(f"Processed {len(self.points)} points, generated {len(lines)} lines")
            except Exception as e:
                print(f"Error in calculation: {str(e)}")
                self.status_var.set(f"Error: {str(e)}")

    def load_points_from_file(self) -> None:
        """Load points from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Points File",
            filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            try:
                self.points = []
                self.update_points_list()
                
                with open(file_path, 'r') as file:
                    for line in file:
                        try:
                            line = line.strip().strip('()')
                            if line:
                                x, y = map(float, line.split(','))
                                x = float(f"{x:.1f}")
                                y = float(f"{y:.1f}")
                                self.add_point((x, y))
                        except ValueError:
                            continue
                            
                self.redraw_all()
                self.status_var.set(f"Loaded {len(self.points)} points from file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load points from file: {e}")

    def on_canvas_click(self, event: tk.Event) -> None:
        """Handle canvas click to add a point"""
        gui_point = (event.x, event.y)
        math_point = self._gui_to_math(gui_point)
        self.add_point(math_point)

    def on_click_clear(self) -> None:
        """Clear all points and circles from the canvas"""
        self.points = []
        self.circles = []
        self.canvas.delete(tk.ALL)
        self.update_points_list()

    def draw_lines_on_canvas(self, lines: List[Tuple[float, float, float, float]]) -> None:
        """Draw Voronoi lines on the canvas"""
        self.canvas.delete("line")
        for l in lines:
            start = self._math_to_gui((l[0], l[1]))
            end = self._math_to_gui((l[2], l[3]))
            self.canvas.create_line(
                start[0], start[1], 
                end[0], end[1], 
                fill='blue', tags="line"
            )

    def generate_random_points(self) -> None:
        """Generate random points within the canvas bounds"""
        self.points = []
        num_points = random.randint(15, 30)
        
        for _ in range(num_points):
            x = float(f"{random.uniform(10, self.CANVAS_WIDTH-10):.1f}")
            y = float(f"{random.uniform(10, self.CANVAS_HEIGHT-10):.1f}")
            self.add_point((x, y))
            
        self.update_points_list()
        self.redraw_all()
        self.status_var.set(f"Generated {num_points} random points")

    def _gui_to_math(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Convert GUI coordinates to math coordinates"""
        x, y = point
        return (x, self.CANVAS_HEIGHT - y)

    def _math_to_gui(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Convert math coordinates to GUI coordinates"""
        x, y = point
        return (x, self.CANVAS_HEIGHT - y)

def main() -> None:
    """Run the main application"""
    root = tk.Tk()
    MainApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()