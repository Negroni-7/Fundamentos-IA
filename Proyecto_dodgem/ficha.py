# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

class Ficha:
    def __init__(self, nombre, equipo, fila, columna):
        """Inicializa una ficha con su nombre, equipo y posición."""
        self.nombre = nombre
        self.posicion = [fila, columna]
        self.equipo = equipo
        self.corona = False

    def getequipo(self):
        """Devuelve el equipo al que pertenece la ficha."""
        return self.equipo

    def solicitar_movimiento(self):
        """Solicita al usuario una dirección de movimiento válida."""
        peticion = None
        while (peticion is None or not peticion.isdigit() 
                or int(peticion) < 1 or int(peticion) > 3):
            if peticion is not None:
                print("ATENCIÓN: Debe de ingresar un número que se"
                      "muestre en las opciones.\n\n")
            print("¿Hacia donde desea mover la ficha?")
            print("1- Arriba")
            print("2- Derecha")
            if self.equipo == "azul":
                print("3- Abajo")
            else:
                print("3- Izquierda")
            peticion = input("Ingrese número: ")
        return int(peticion)

    def mover_ficha(self, tablero):
        """Solicita y aplica un movimiento válido de la ficha en el
        tablero."""
        movimiento_valido = False
        while not movimiento_valido:
            peticion = self.solicitar_movimiento()

            if peticion == 1:
                if self.posicion[0] == 0 and self.equipo == "azul":
                    print("ERROR: Movimiento no válido")
                elif self.posicion[0] == 0 and self.equipo == "rojo":
                    movimiento_valido = True
                    tablero[self.posicion[0]][self.posicion[1]] = "."
                    self.posicion[0] = None
                    self.corona = True
                elif tablero[self.posicion[0] - 1][self.posicion[1]] != ".":
                    print("ERROR: Movimiento no válido")
                else:
                    movimiento_valido = True
                    aux = [self.posicion[0], self.posicion[1]]
                    self.posicion[0] = self.posicion[0] - 1
                    if self.equipo == "azul":
                        tablero[self.posicion[0]][self.posicion[1]] = "X"
                    else:
                        tablero[self.posicion[0]][self.posicion[1]] = "O"
                    tablero[aux[0]][aux[1]] = "."
            elif peticion == 2:
                if (self.posicion[1] == len(tablero) - 1 
                        and self.equipo == "rojo"):
                    print("ERROR: Movimiento no válido")
                elif (self.posicion[1] == len(tablero) - 1 
                        and self.equipo == "azul"):
                    movimiento_valido = True
                    tablero[self.posicion[0]][self.posicion[1]] = "."
                    self.posicion[1] = None
                    self.corona = True
                    print("Felicidades!")
                elif tablero[self.posicion[0]][self.posicion[1] + 1] != ".":
                    print("ERROR: Movimiento no válido")
                else:
                    movimiento_valido = True
                    aux = [self.posicion[0], self.posicion[1]]
                    self.posicion[1] = self.posicion[1] + 1
                    if self.equipo == "azul":
                        tablero[self.posicion[0]][self.posicion[1]] = "X"
                    else:
                        tablero[self.posicion[0]][self.posicion[1]] = "O"
                    tablero[aux[0]][aux[1]] = "."
            elif peticion == 3 and self.equipo == "azul":
                if self.posicion[0] == len(tablero) - 1:
                    print("ERROR: Movimiento no válido")
                elif tablero[self.posicion[0] + 1][self.posicion[1]] != ".":
                    print("ERROR: Movimiento no válido")
                else:
                    movimiento_valido = True
                    aux = [self.posicion[0], self.posicion[1]]
                    self.posicion[0] = self.posicion[0] + 1
                    tablero[self.posicion[0]][self.posicion[1]] = "X"
                    tablero[aux[0]][aux[1]] = "."
            elif peticion == 3 and self.equipo == "rojo":
                if self.posicion[1] == 0:
                    print("ERROR: Movimiento no válido")
                elif tablero[self.posicion[0]][self.posicion[1] - 1] != ".":
                    print("ERROR: Movimiento no válido")
                else:
                    movimiento_valido = True
                    aux = [self.posicion[0], self.posicion[1]]
                    self.posicion[1] = self.posicion[1] - 1
                    tablero[self.posicion[0]][self.posicion[1]] = "O"
                    tablero[aux[0]][aux[1]] = "."