from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import tkinter as tk
import csv
from matplotlib.patches import Rectangle
from system_window import *
from tkinter import messagebox

import Input_File


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith(('koord.csv', 'staebe.csv', 'f_vektor.csv', 'fk.csv')):
            self.callback()


def read_forces(filename='f_vektor.csv'):
    forces = {}
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            forces_list = []
            for row in reader:
                forces_list.extend(row)

            for i in range(0, len(forces_list), 2):
                try:
                    fx = float(forces_list[i])
                    fy = float(forces_list[i + 1])
                    forces[(i // 2) + 1] = (fx, fy)
                except (ValueError, IndexError):
                    pass  # Skip rows that can't be converted to float or are incomplete
    except FileNotFoundError:
        pass  # Ignore if the file does not exist yet
    return forces


def read_arrows(filename='fk.csv'):
    arrows = []
    max_magnitude = 0
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    node = int(row[0])
                    direction = int(row[1])
                    magnitude = float(row[2])
                    max_magnitude = max(max_magnitude, abs(magnitude))
                    arrows.append((node, direction, magnitude))
                except ValueError:
                    pass  # Skip rows that can't be converted to the appropriate types
    except FileNotFoundError:
        pass  # Ignore if the file does not exist yet
    return arrows, max_magnitude


def read_bcond(filename='bcond.csv'):
    bcond = {}
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    node = int(row[0])
                    direction = int(row[1])  # Direction of the boundary condition
                    if node not in bcond:
                        bcond[node] = [0, 0]  # Initialize both x and y directions as not blocked
                    if direction == 1:  # x direction
                        bcond[node][0] = 1
                    elif direction == 2:  # y direction
                        bcond[node][1] = 1
                except ValueError:
                    pass  # Skip rows that can't be converted to the appropriate types
    except FileNotFoundError:
        pass  # Ignore if the file does not exist yet
    return bcond


def plot():
    # Read the coordinates from 'koord.csv'
    coords = {}
    with open('koord.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            try:
                x = float(row[0])
                y = float(row[1])
                coords[i + 1] = (x, y)  # Knoten werden mit 1 beginnend nummeriert
            except ValueError:
                pass  # Skip rows that can't be converted to float

    # Read the beams from 'staebe.csv'
    beams = []
    with open('staebe.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                start_node = int(row[0])
                end_node = int(row[1])
                beams.append((start_node, end_node))
            except ValueError:
                pass  # Skip rows that can't be converted to int

    # Read the forces from 'f_vektor.csv'
    forces = read_forces()

    # Read the arrows from 'fk.csv'
    arrows, max_magnitude = read_arrows()

    # Read the boundary conditions from 'bcond.csv'
    bcond = read_bcond()

    # Create the plot
    fig = Figure(figsize=(6, 6), dpi=100)  # Increased figure size for better clarity
    plot1 = fig.add_subplot(111)

    # Plot the beams
    for beam in beams:
        start_node, end_node = beam
        if start_node in coords and end_node in coords:
            x_values = [coords[start_node][0], coords[end_node][0]]
            y_values = [coords[start_node][1], coords[end_node][1]]
            plot1.plot(x_values, y_values, marker='o', color='blue')

    # Plot the forces
    for node, (fx, fy) in forces.items():
        if node in coords:
            x, y = coords[node]
            if node in bcond:  # Only display forces if boundary conditions exist
                x_sperre, y_sperre = bcond[node]
                if x_sperre and y_sperre:  # Both directions are blocked
                    plot1.add_patch(Rectangle((x - 0.1, y - 0.1), 0.2, 0.2, color='red', fill=True))
                    plot1.text(x, y - 0.15, f'{fy}', color='black', ha='center', va='top')  # Below in x direction
                    plot1.text(x - 0.15, y, f'{fx}', color='black', ha='right', va='center')  # Left in y direction
                elif y_sperre:  # Only y direction is blocked
                    plot1.plot([x - 0.1, x + 0.1], [y, y], color='red', linewidth=4)
                    plot1.text(x - 0.35, y, f'{fy}', color='black', ha='left', va='center')
                    plot1.text(x, y - 0.25, f'{fx}', color='black', ha='center', va='bottom')
                elif x_sperre:  # Only x direction is blocked
                    plot1.plot([x, x], [y - 0.1, y + 0.1], color='red', linewidth=4)
                    plot1.text(x, y + 0.25, f'{fy}', color='black', ha='center', va='bottom')
                    plot1.text(x + 0.25, y, f'{fx}', color='black', ha='left', va='center')
            else:
                # Do not show forces if there's no boundary condition
                pass

    # Plot the arrows
    min_arrow_length = 2.0
    for node, direction, magnitude in arrows:
        if node in coords:
            x, y = coords[node]
            if max_magnitude > 0:  # Avoid division by zero
                # Scale the arrow length
                arrow_length = (magnitude / max_magnitude) * min_arrow_length
                if direction == 1:  # x direction
                    plot1.arrow(x - arrow_length + 0.1, y, arrow_length if magnitude >= 0 else arrow_length, 0,
                                head_width=0.1, head_length=0.1, fc='green', ec='green')
                elif direction == 2:  # y direction
                    plot1.arrow(x, y - arrow_length + 0.1, 0, arrow_length if magnitude >= 0 else arrow_length,
                                head_width=0.1, head_length=0.1, fc='green', ec='green')

    plot1.set_aspect('equal', adjustable='datalim')
    plot1.set_title("Stäbe Plot")
    plot1.set_xlabel("X-Achse")
    plot1.set_ylabel("Y-Achse")

    # Adjust plot limits to provide extra space
    x_coords = [x for x, y in coords.values()]
    y_coords = [y for x, y in coords.values()]
    x_margin = 0.1 * (max(x_coords) - min(x_coords))
    y_margin = 0.1 * (max(y_coords) - min(y_coords))
    plot1.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
    plot1.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)

    return fig


def update_plot(canvas):
    fig = plot()
    canvas.figure = fig
    canvas.draw()

    # Reduce the window size by 1 pixel
    window = canvas.get_tk_widget().master.master
    width = window.winfo_width()
    height = window.winfo_height()
    window.geometry(f"{width-1}x{height-1}")

    # Restore the window size to its original dimensions
    window.after(100, lambda: window.geometry(f"{width}x{height}"))

def main():
    main = tk.Tk()
    main.tk.call('tk', 'scaling', 2.0)
    main.title("Py Truss 0.0.1")
    screen_width = main.winfo_screenwidth()
    screen_height = main.winfo_screenheight()
    main.geometry(f"{screen_width}x{screen_height}+0+0")

    # Configure grid layout
    main.grid_rowconfigure(0, weight=1)
    main.grid_rowconfigure(1, weight=0)
    main.grid_columnconfigure(0, weight=1)

    # Frame for the plot and toolbar
    plot_frame = tk.Frame(main)
    plot_frame.grid(row=0, column=0, sticky='nsew')

    fig = plot()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)

    toolbar_frame = tk.Frame(plot_frame)
    toolbar_frame.pack(side=tk.TOP, fill=tk.X)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    for button in toolbar.winfo_children():
        button.pack_configure(padx=5, pady=2)

    # Frame for the buttons
    button_frame = tk.Frame(main)
    button_frame.grid(row=1, column=0, sticky='ew')

    cmdEnd = tk.Button(button_frame, text="Beenden", command=main.destroy)
    cmdEnd.pack(side=tk.RIGHT, padx=20, pady=20)

    cmdCalc = tk.Button(button_frame, text="Berechnen", command=lambda: [update_plot(canvas), Input_File.calculation()])

    cmdCalc.pack(side=tk.RIGHT, padx=20, pady=20)

    button = tk.Button(button_frame, text="System", command=lambda: input_window())  # Hier die tatsächliche Funktion für 'input_window' einfügen
    button.pack(side=tk.LEFT, padx=20, pady=20)

    def on_files_changed():
        update_plot(canvas)

    event_handler = FileChangeHandler(on_files_changed)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    main.mainloop()
    observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
