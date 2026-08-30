# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

import os


def imprimir_tablero(tablero):
    """Imprime el tablero en pantalla."""
    print()
    print("    ", end=" ")
    for i, fila in enumerate(tablero):
        print(f"{i + 1:>4}", end=" ")
    print()

    for j, fila in enumerate(tablero):
        print(f"{j + 1:>4}", end=" ")
        for elem in fila:
            print(f"{elem:>4}", end=" ")
        print()
    print()


def generar_tablero(n):
    """Crea el tablero del tamaño que se necesite."""
    tablero = []
    for i in range(n):
        fila = []
        for j in range(n):
            fila.append('.')
        tablero.append(fila)
    return tablero


def limpiar_consola():
    """Limpia la consola imprimiendo saltos de línea y usando el comando del
    sistema."""
    print("\n" * 500)
    os.system("cls" if os.name == "nt" else "clear")


def generar_codigo(tablero, turno_jugador):
    """Función que sirve para determinar si se termina."""
    codigo_tablero = ""
    for fila in tablero:
        for celda in fila:
            codigo_tablero += celda
    return codigo_tablero + turno_jugador