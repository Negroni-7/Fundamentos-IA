# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

from time import time

from tablero import generar_codigo
from ficha import Ficha


def llenar_tablero(tablero, azules, rojos):
    """Llena el tablero de las fichas que se utilizarán."""
    for i, fila in enumerate(tablero):
        if i == len(tablero) - 1:
            continue

        azules.append(Ficha(i + 1, "azul", i, 0)) # Equipo azul son las X                       <-----------------------------
        rojos.append(Ficha(i + 1, "rojo", len(tablero) - 1, i + 1)) # Equipo rojo son las O     <-----------------------------
        tablero[i][0] = "X"
        tablero[len(tablero) - 1][i + 1] = "O"


def seleccion_ficha(equipo, tablero):
    """Solicita al usuario las coordenadas de una ficha y las valida."""
    print("Seleccione la ficha que desea jugar.")

    fila = input("Ingrese la fila (horizontal) de la ficha: ")
    while not fila.isdigit() or int(fila) < 1 or int(fila) > len(tablero):
        print("ERROR: Ingrese un valor numérico válido")
        fila = input("Ingrese la fila (horizontal) de la ficha: ")

    columna = input("Ingrese la columna de la ficha: ")
    while (not columna.isdigit() or int(columna) < 1 or int(columna) >
           len(tablero)):
        print("ERROR: Ingrese un valor numérico válido")
        columna = input("Ingrese la columna de la ficha: ")

    coordenadas = [int(fila) - 1, int(columna) - 1]
    espacio = tablero[coordenadas[0]][coordenadas[1]]

    if equipo == "azul":
        if espacio == "X":
            return coordenadas
        else:
            print("Coordenada no válida.")
    elif equipo == "rojo":
        if espacio == "O":
            return coordenadas
        else:
            print("Coordenada no válida.")

    return None


def faltan_fichas_coronar(equipo_x):
    """Recorre las listas de las fichas buscando si faltan por coronar o
    no."""
    for ficha in equipo_x:
        if not ficha.corona:
            return False
    return True


def equipo_bloqueado(equipo_x, tablero):
    """Bucle que recorre la lista de fichas del equipo y revisa si alguna
    puede moverse."""
    n = len(tablero)
    for ficha in equipo_x:
        if ficha.corona:
            continue

        fila, columna = ficha.posicion
        if ficha.equipo == "azul":
            if (fila > 0
                    and tablero[fila - 1][columna]
                    == "."):
                return False
            
            if columna == n-1:
                return False
            
            elif (tablero[fila][columna + 1] == "."):
                return False
            if (fila < n - 1 and tablero[fila + 1][columna] == "."):
                return False
            
        elif ficha.equipo == "rojo":
            if fila == 0:
                return False
            elif (tablero[fila - 1][columna]
                    == "."):
                return False
            if (columna < n - 1
                    and tablero[fila][columna + 1]
                  == "."):
                return False
            if (columna > 0
                    and tablero[fila][columna - 1]
                  == "."):
                return False
    return True

def hay_repeticion(tablero, turno, historial):
    """Registra el estado actual del tablero en el historial y termina
    la partida en empate si ese estado ya se repitió 3 veces."""
    codigo_actual = generar_codigo(tablero, turno)
    historial.append(codigo_actual)
    if historial.count(codigo_actual) >= 3:
        print(
            "Debido a repetición de movimientos,"
            "el juego queda en empate."
        )
        time.sleep(5)
        exit()