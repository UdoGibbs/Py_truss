from math import *

import numpy as np
from numpy.linalg import inv

from main import *


def remove_n_j_from_lists(list_of_lists):
    # Iteriere durch jede innere Liste
    for inner_list in list_of_lists:
        # Erstelle eine neue Liste, die nur die gewünschten Objekte enthält
        inner_list[:] = [item for item in inner_list if item not in ("N", "J")]


def calculation():
    try:

        ## Koordinaten-CSV einlesen
        with open('koord.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            koords = []  # Liste, um die Daten zu speichern
            for row in reader:  # Iteriere über die Zeilen der CSV-Datei
                koords.append(row)
        remove_n_j_from_lists(koords)

        ## Material-CSV einlesen
        with open('material.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            materials = []  # Liste, um die Daten zu speichern
            for row in reader:  # Iteriere über die Zeilen der CSV-Datei
                materials.append(row)

        ## Staebe-CSV einlesen
        with open('staebe.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            staebe = []  # Liste, um die Daten zu speichern
            for row in reader:  # Iteriere über die Zeilen der CSV-Datei
                staebe.append(row)

        # Randbedingungen einlesen
        filename = 'bcond.csv'
        # Einlesen der CSV-Datei in ein NumPy-Array
        data_array = np.genfromtxt(filename, delimiter=',')
        # Umwandeln des Arrays in eine NumPy-Matrix
        bcond = np.matrix(data_array)

        # Kräfte einlesen
        filename = 'fk.csv'
        # Einlesen der CSV-Datei in ein NumPy-Array
        data_array = np.genfromtxt(filename, delimiter=',')
        # Umwandeln des Arrays in eine NumPy-Matrix
        fk = np.matrix(data_array)

        # Systemvariablen
        DOF = 2  # Anzahl Freiheitsgrade pro Knoten
        # NEL = int(system[0]['NEL'])  # Anzahl der Elemente
        NEL = len(staebe)
        ENODE = 2  # Anzahl Knoten je Element
        EDOF = ENODE * DOF  # Anzahl Freiheitsgrade pro Element
        # NNODE = int(system[0]['NNODE'])  # Anzahl der globalen Knoten
        NNODE = len(koords)
        NDOF = DOF * NNODE  # Anzahl der globalen Freiheitsgrade

        # Materialparameter der Elemente E*A
        mat = np.matrix(materials)
        mat = mat.astype(np.float)

        eModuln = []
        for i in range(len(staebe)):
            eModuln.append(materials[i][0])
        # print(eModuln)
        surfaces = []
        for i in range(len(staebe)):
            surfaces.append(materials[i][1])
        # print(surfaces)
        # Knotennummern der Elemente
        nodes = np.matrix([[1, 2],
                           [2, 3]], )

        # Globale Knotenkoordinaten
        koord = np.matrix(koords)
        koord = koord.astype(float)

        def calc_length(x1, x2, y1, y2):
            l = ((x2 - x1) ** 2 + (y1 - y2) ** 2) ** 0.5
            return l

        def calculate_lengths(koord, staebe):
            lengths = []
            for stab in staebe:
                start_node = int(stab[0]) - 1
                end_node = int(stab[1]) - 1
                x1, y1 = koord.item(start_node, 0), koord.item(start_node, 1)
                x2, y2 = koord.item(end_node, 0), koord.item(end_node, 1)
                length = calc_length(x1, x2, y1, y2)
                lengths.append(length)
            return lengths

        lengths = calculate_lengths(koord, staebe)
        # print("Längen der Stäbe:", lengths)

        # Elementsteifigkeitsmatrizen
        ker = []
        # print("E-Modul:",float(eModuln[i]))
        # print("Surface:", float(surfaces[i]))
        for i in range(len(staebe)):
            ker.append((float(eModuln[i]) * float(surfaces[i]) / lengths[i]) * np.matrix([[1, -1],
                                                                                          [-1, 1], ]))
            # print("Ker:",ker[i])

        def calculate_angles(koord, staebe):
            angles = []
            for stab in staebe:
                start_node = int(stab[0]) - 1
                end_node = int(stab[1]) - 1
                x1, y1 = koord.item(start_node, 0), koord.item(start_node, 1)
                x2, y2 = koord.item(end_node, 0), koord.item(end_node, 1)
                if x2 - x1 == 0:
                    if y2 - y1 >= 0:
                        alpha = pi / 2
                    else:
                        alpha = (pi + pi / 2)
                else:
                    alpha = atan((y2 - y1) / (x2 - x1))
                    if alpha <= 0:
                        alpha = 2 * pi + alpha
                angles.append(alpha)
            return angles

        angles = calculate_angles(koord, staebe)

        # Transformationsmatrix
        tei = []

        for i in range(len(staebe)):
            c = np.round(np.cos(angles[i]), 3)
            s = np.round(np.sin(angles[i]), 3)
            tei.append(np.matrix([[c, s, 0.0, 0.0],
                                  [0.0, 0.0, c, s], ]))
            # print("tei:", tei[i])

        # Lokale Elementsteifigkeitsmatrizen
        kei = []
        for i in range(len(staebe)):
            kei.append(np.transpose(tei[i]) * ker[i] * tei[i])
            # print("kei:",kei[i])

        # Berechnen der Größe der globalen Steifigkeitsmatrix
        #global_matrix_size = (kei[0].shape[1] + (NEL - 1) * kei[0].shape[1] // 2)
        global_matrix_size = NDOF
        # Initialisieren der globalen Steifigkeitsmatrix mit Nullen
        K = np.zeros((global_matrix_size, global_matrix_size))

        def assemble_global_stiffness_matrix(K, kei, staebe):
            # Loop through each element and place its stiffness matrix in the global stiffness matrix
            for i, (start_node, end_node, _, _) in enumerate(staebe):
                # Convert to integer and subtract 1 for zero-based indexing
                start_node = int(start_node) - 1
                end_node = int(end_node) - 1

                # Create an array of indices in the global stiffness matrix corresponding to the element's nodes
                indices = [2 * start_node, 2 * start_node + 1, 2 * end_node, 2 * end_node + 1]

                # Size of the element stiffness matrix
                size = kei[i].shape[0]

                # Add the element stiffness matrix to the global stiffness matrix at the correct positions
                for r in range(size):
                    for c in range(size):
                        K[indices[r], indices[c]] += kei[i][r, c]

        # Aufrufen der Funktion zum Überlagern der Steifigkeitsmatrizen
        assemble_global_stiffness_matrix(K, kei, staebe)

        # Bestimmen der Länge des Vektors U
        # Da jede Knotennummer zwei Richtungen (1 und 2) hat, ist die Länge des Vektors 2 * max_knoten
        U_length = int(2 * NNODE)

        # Initialisieren des Vektors U mit None
        U = [None] * U_length

        # Aktualisieren des Vektors U basierend auf bcond
        for row in bcond:
            knoten = int(row[0, 0])
            richtung = int(row[0, 1])
            index = 2 * (knoten - 1) + (richtung - 1)
            U[index] = 0

        # Ermitteln der Indizes, bei denen U None ist
        none_indices = [i for i, x in enumerate(U) if x is None]

        # Extrahieren der Submatrix Kaa, indem nur die Zeilen und Spalten verwendet werden, deren Indizes in none_indices sind
        Kaa = K[np.ix_(none_indices, none_indices)]

        # Submatrix Kbb extrahieren
        Kbb = np.delete(K, none_indices, axis=0)
        Kbb = np.delete(Kbb, none_indices, axis=1)

        # Alle Indizes außer den unbekannten
        known_indices = [i for i in range(K.shape[0]) if i not in none_indices]

        # Submatrix Kab extrahieren
        Kab = K[np.ix_(none_indices, known_indices)]

        # Erzeugen des Vektors F
        F = np.zeros((NDOF, 1), dtype=float)

        # Aktualisieren des Vektors F basierend auf fk
        for row in fk:
            knoten = int(row[0, 0])
            richtung = int(row[0, 1])
            kraft = row[0, 2]
            index = 2 * (knoten - 1) + (richtung - 1)
            F[index, 0] = float(kraft)

        # Bestimmen der Indizes für unbekannte Verschiebungen
        unknown_displacement_indices = [i for i, value in enumerate(U) if value is None]

        # Extrahieren des Subvektors Faa
        Faa = F[unknown_displacement_indices]
        Uaa = inv(Kaa) @ Faa

        # Einfügen des Vektors U_aa in U
        for i, index in enumerate(unknown_displacement_indices):
            U[index] = Uaa[i, 0]

        # Berechnung der Lagerreaktionen
        Fb = np.transpose(Kab) @ Uaa

        # Einfügen des Vektors Fb in F
        for i, index in enumerate(known_indices):
            print("i:",i)
            print("indes:",index)
            print("known:", known_indices)
            print("Fb[i]",Fb[i, 0])
            print(Fb)
            F[index] = Fb[i, 0]

        # Berechnunge der Schnittkräte
        ## Todo

        # Runden der Ergebnisse
        U = np.round(U, 3)
        F = np.round(F, 3)

        # Schreibe den U-Vektor in eine CSV-Datei
        with open('u_vektor.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(U)

        # Schreibe den F-Vektor in eine CSV-Datei
        with open('f_vektor.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in zip(*F.tolist()):
                writer.writerow(row)


    except Exception as e:
        # Behandlung aller anderen Ausnahmen
        messagebox.showinfo("Fehler", "Ungültiges System.")
