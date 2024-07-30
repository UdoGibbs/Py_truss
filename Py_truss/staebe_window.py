import csv
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def save_to_csv(entries, window):
    try:
        with open('staebe.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for row_entries in entries:
                row_values = [entry.get().strip() for entry in row_entries]
                if all(value.replace('.', '', 1).isdigit() for value in row_values):  # Prüfen, ob alle Felder Zahlen enthalten
                    writer.writerow(row_values)
                elif any(value for value in row_values):  # Prüfen, ob irgendein Wert in der Zeile vorhanden ist
                    messagebox.showerror("Fehler", "Alle Felder in einer Zeile müssen Zahlen enthalten.")
                    return
        window.destroy()
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der CSV: {e}")

def create_label(parent, text, row, column, rowspan=1, columnspan=1, sticky="nsew"):
    label = tk.Label(parent, text=text, borderwidth=1, relief="solid")
    label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=1, pady=1)

def create_entry(parent, row, column, rowspan=1, columnspan=1, sticky="nsew"):
    entry = tk.Entry(parent, borderwidth=1, relief="solid", width=5)  # Breite auf ein Drittel reduziert
    entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky, padx=1, pady=1)
    return entry

def open_new_window():
    # Erstelle ein neues Fenster
    new_window = tk.Toplevel()
    new_window.title("Tabelle")

    # Fenstergröße festlegen
    new_window.geometry("350x656")

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
    create_label(scrollable_frame, "Stab", 0, 1, columnspan=2)
    create_label(scrollable_frame, "E-Modul", 0, 3, rowspan=2)
    create_label(scrollable_frame, "Fläche", 0, 4, rowspan=2)

    # Unterspalten für Stab
    create_label(scrollable_frame, "von", 1, 1)
    create_label(scrollable_frame, "bis", 1, 2)

    # Beispiel für Datenzeilen mit Eingabefeldern
    entries = []
    for i in range(2, 22):  # Erstellen von 20 Datenzeilen
        row_entries = [
            create_entry(scrollable_frame, i, 1),  # Stab von
            create_entry(scrollable_frame, i, 2),  # Stab bis
            create_entry(scrollable_frame, i, 3),  # E-Modul
            create_entry(scrollable_frame, i, 4)   # Fläche
        ]
        entries.append(row_entries)

        # Nummerierung
        create_label(scrollable_frame, f"{i-1}", i, 0)

    # Daten aus der Datei laden und in die Textfelder eintragen
    def load_entries_from_csv(filename):
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i < len(entries):
                        row_entries = entries[i]
                        # Setze die Werte in die Textfelder
                        for j, value in enumerate(row):
                            if j < len(row_entries):
                                row_entries[j].delete(0, tk.END)
                                row_entries[j].insert(0, value)
        except FileNotFoundError:
            print(f"Datei {filename} nicht gefunden.")

    # Aufruf der Funktion zum Laden der Einträge
    load_entries_from_csv('staebe.csv')

    # Funktion zum Leeren der Eingabefelder
    def clear_entries():
        for row_entries in entries:
            for entry in row_entries:
                entry.delete(0, tk.END)

    # Buttons zum Speichern und Löschen
    save_button = tk.Button(new_window, text="Speichern", command=lambda: save_to_csv(entries, new_window))
    save_button.pack(side=tk.RIGHT, padx=10, pady=10)

    clear_button = tk.Button(new_window, text="Löschen", command=clear_entries)
    clear_button.pack(side=tk.LEFT, padx=10, pady=10)
