import csv
import tkinter as tk
from tkinter import ttk

from staebe_window import *

def save_entries_to_csv(entries, filename):
    # Speichert die Einträge in der CSV-Datei
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for entry_row in entries:
            # Extrahiere die Werte aus den Entry-Widgets und Label-Widgets
            x_value = entry_row[0].get().strip()
            z_value = entry_row[1].get().strip()

            # Prüfen, ob beide Werte vorhanden sind
            if x_value and z_value:
                row_values = [x_value, z_value]

                # Füge die Werte aus den Label-Widgets hinzu
                for widget in entry_row[2:]:
                    if isinstance(widget, tk.Label):
                        row_values.append(widget.cget("text").strip())

                # Schreibe nur Zeilen mit mindestens zwei Werten (2 Koordinaten + 0 oder mehr Auflagerwerte)
                if len(row_values) > 2:
                    writer.writerow(row_values)


def on_save(entries, new_window):
    # Speichert die Einträge und schließt das Fenster
    filename = "koord.csv"  # Dateiname der CSV-Datei
    save_entries_to_csv(entries, filename)
    print(f"Einträge gespeichert in Datei: {filename}")
    new_window.destroy()  # Schließt das Fenster


def on_clear(entries):
    # Leert alle Textfelder und setzt alle Toggle-Labels auf "N"
    for entry_row in entries:
        for widget in entry_row:
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Label):
                widget.config(text="N")


def center_window(window, width, height):
    # Bildschirmgröße ermitteln
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Position des Fensters berechnen, um es zu zentrieren
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Geometrie des Fensters festlegen
    window.geometry(f'{width}x{height}+{x}+{y}')


def input_window():
    # Erstelle ein neues Fenster
    new_window = tk.Toplevel()
    new_window.title("Knoten-Eingabe")  # Setze den Titel des neuen Fensters

    # Fenstergröße festlegen
    window_width = 350
    window_height = 656

    # Fenster zentrieren
    center_window(new_window, window_width, window_height)

    ###
    def create_label(parent, text, row, column, rowspan=1, columnspan=1, sticky="nsew"):
        label = tk.Label(parent, text=text, borderwidth=1, relief="solid")
        label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=1, pady=1)
        return label

    def create_entry(parent, row, column, rowspan=1, columnspan=1, sticky="nsew"):
        entry = tk.Entry(parent, borderwidth=1, relief="solid", width=10)  # Breite halbiert
        entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=1, pady=1)
        return entry

    def toggle_text(label):
        current_text = label.cget("text")
        new_text = "N" if current_text == "J" else "J"
        label.config(text=new_text)

    def create_toggle_label(parent, row, column, rowspan=1, columnspan=1, sticky="nsew"):
        label = tk.Label(parent, text="N", borderwidth=1, relief="solid", width=5)
        label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=1, pady=1)
        label.bind("<Button-1>", lambda e: toggle_text(label))
        return label

    # Erstellen des Frames für die Scrollbar und das Canvas
    frame = tk.Frame(new_window)
    frame.pack(fill=tk.BOTH, expand=True)

    # Erstellen des Canvas
    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Erstellen der Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Scrollbar mit dem Canvas verbinden
    canvas.configure(yscrollcommand=scrollbar.set)

    # Erstellen eines Frames innerhalb des Canvas
    scrollable_frame = tk.Frame(canvas)

    # Hinzufügen des Frames zum Canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Funktion zum Anpassen der Scrollregion
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", configure_scroll_region)

    # Hauptspalten
    create_label(scrollable_frame, "Nr.", 0, 0, rowspan=2)
    create_label(scrollable_frame, "Koordinaten", 0, 1, columnspan=2)
    create_label(scrollable_frame, "Auflager", 0, 3, columnspan=2)

    # Unterspalten für Koordinaten
    create_label(scrollable_frame, "x", 1, 1)
    create_label(scrollable_frame, "z", 1, 2)

    # Unterspalten für Auflager
    create_label(scrollable_frame, "x", 1, 3)
    create_label(scrollable_frame, "z", 1, 4)

    # Datenzeilen mit Eingabefeldern
    entries = []
    for i in range(2, 22):  # Erstellen von 20 Datenzeilen
        row_entries = [
            create_entry(scrollable_frame, i, 1),  # Koordinaten x
            create_entry(scrollable_frame, i, 2),  # Koordinaten z
            create_toggle_label(scrollable_frame, i, 3),  # Auflager x
            create_toggle_label(scrollable_frame, i, 4)  # Auflager z
        ]
        create_label(scrollable_frame, f"{i - 1}", i, 0)  # Nr.
        entries.append(row_entries)

    # Daten aus der Datei laden und in die Textfelder eintragen
    def load_entries_from_csv(filename):
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i < len(entries):
                        entry_row = entries[i]
                        # Setze die Koordinaten
                        if len(row) >= 2:
                            entry_row[0].delete(0, tk.END)
                            entry_row[0].insert(0, row[0])
                            entry_row[1].delete(0, tk.END)
                            entry_row[1].insert(0, row[1])
                        # Setze die Auflagerwerte
                        for j, value in enumerate(row[2:], start=2):
                            if j < len(entry_row):
                                entry_row[j].config(text=value)
        except FileNotFoundError:
            print(f"Datei {filename} nicht gefunden.")

    # Aufruf der Funktion zum Laden der Einträge
    load_entries_from_csv("koord.csv")

    # Erstellen der Buttons
    button_frame = tk.Frame(new_window)
    button_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

    # Button-Layout
    clear_button = tk.Button(button_frame, text="Löschen", command=lambda: on_clear(entries))
    clear_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(button_frame, text="Speichern", command=lambda: on_save(entries, new_window))
    save_button.pack(side=tk.RIGHT, padx=5)

    staebe_button = tk.Button(button_frame, text="Stäbe", command=open_new_window)
    staebe_button.pack(side=tk.RIGHT, padx=5)

    return new_window
