# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

from ficha import Ficha


def llenar_tablero(tablero, azules, rojos):
    """Llena el tablero de las fichas que se utilizarán."""
    for i, fila in enumerate(tablero):
        if i == len(tablero) - 1:
            continue

        azules.append(Ficha(i + 1, "azul", i, 0))
        rojos.append(Ficha(i + 1, "rojo", len(tablero) - 1, i + 1))
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
    for ficha in equipo_x:
        if ficha.corona:
            continue
        if ficha.equipo == "azul":
            if (ficha.posicion[0] > 0
                    and tablero[ficha.posicion[0] - 1][ficha.posicion[1]]
                    == "."):
                return False
            elif (ficha.posicion[1] < len(tablero) - 1
                    and tablero[ficha.posicion[0]][ficha.posicion[1] + 1]
                  == "."):
                return False
            elif (ficha.posicion[0] < len(tablero) - 1
                    and tablero[ficha.posicion[0] + 1][ficha.posicion[1]]
                  == "."):
                return False
        elif ficha.equipo == "rojo":
            if (ficha.posicion[0] > 0
                    and tablero[ficha.posicion[0] - 1][ficha.posicion[1]]
                    == "."):
                return False
            elif (ficha.posicion[1] < len(tablero) - 1
                    and tablero[ficha.posicion[0]][ficha.posicion[1] + 1]
                  == "."):
                return False
            elif (ficha.posicion[1] > 0
                    and tablero[ficha.posicion[0]][ficha.posicion[1] - 1]
                  == "."):
                return False
    return True