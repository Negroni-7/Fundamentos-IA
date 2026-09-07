# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

import time
from tablero import (imprimir_tablero, generar_tablero, limpiar_consola)
from juego import (llenar_tablero, seleccion_ficha, faltan_fichas_coronar,
                   equipo_bloqueado, hay_repeticion)
from agente import Agente

def jugar():
    """Función principal que ejecuta el juego."""
    print("====================================")
    print("        Bienvenido a Dodgem         ")
    print("====================================\n")
    
    while True:
        print("================MENU================")
        print("=            1. Jugar              =")
        print("=            2. Salir              =")
        print("================MENU================\n")

        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            print("\n\n¿Con quién desea jugar?\n")
            opcion_sub_menu = input("1. Contra otro jugador\n2. Contra la IA\n3. Volver al menú principal\n\nSeleccione una opción: ")
            if opcion_sub_menu == "1":
        
                n = input(
                        "Ingrese el tamaño del tablero (mínimo 4 y con numero PAR): "
                    )
                while not n.isdigit() or int(n) < 4 or int(n) % 2 != 0:
                    print("ERROR: Ingrese un valor numérico válido")
                    n = input(
                        "Ingrese el tamaño del tablero (mínimo 4 y con numero PAR): "
                            )
                n = int(n)
                limpiar_consola()
                
                print("Comienza el equipo de las X \n")
                tablero = generar_tablero(n)
                equipo_a = []
                equipo_r = []
                historial = []
                llenar_tablero(tablero, equipo_a, equipo_r)
                parar_juego = False
                
                while not parar_juego:
                    # Juega X
                    print("Turno del equipo de las X")
                    imprimir_tablero(tablero)
                    
                    if equipo_bloqueado(equipo_a, tablero):
                        print(
                            "El equipo de las X no puede moverse."
                            "Gana el equipo de las O"
                        )
                        time.sleep(5)
                        exit()
                    elif equipo_bloqueado(equipo_r, tablero):
                        print(
                            "El equipo de las O no puede moverse."
                            "Gana el equipo de las X"
                        )
                        time.sleep(5)
                        exit()

                    coordenada_jugar = None
            
                    while coordenada_jugar is None:
                        coordenada_jugar = seleccion_ficha("azul", tablero)
            
                    for ficha in equipo_a:
                        if ficha.posicion == coordenada_jugar:
                            ficha.mover_ficha(tablero)
                    if faltan_fichas_coronar(equipo_a):
                        print("Felicidades. Gana el equipo de las X")
                        time.sleep(5)
                        exit()
                        
                    hay_repeticion(tablero, "X", historial)
                    limpiar_consola()
                        
                    # Juega O
                    print("Turno del equipo de los O")
                    imprimir_tablero(tablero)
                    
                    if equipo_bloqueado(equipo_a, tablero):
                        print(
                            "El equipo de las X no puede moverse."
                            "Gana el equipo de las O"
                        )
                        time.sleep(5)
                        exit()
                    elif equipo_bloqueado(equipo_r, tablero):
                        print(
                            "El equipo de las O no puede moverse."
                            "Gana el equipo de las X"
                        )
                        time.sleep(5)
                        exit()

                    coordenada_jugar = None

                    while coordenada_jugar is None:
                        coordenada_jugar = seleccion_ficha("rojo", tablero)
                    for ficha in equipo_r:
                        if ficha.posicion == coordenada_jugar:
                            ficha.mover_ficha(tablero)
                    if faltan_fichas_coronar(equipo_r):
                        print("Felicidades. Gana el equipo de las O")
                        time.sleep(5)
                        exit()
                        
                    hay_repeticion(tablero, "O", historial)
                    limpiar_consola()
                    
                
            elif opcion_sub_menu == "2":
                print("Iniciando juego contra la IA...")
                time.sleep(2)
                n = input("Ingrese el tamaño del tablero (mínimo 4 y con numero PAR): ")
                while not n.isdigit() or int(n) < 4 or int(n) % 2 != 0:
                    print("ERROR: Ingrese un valor numérico válido")
                    n = input("Ingrese el tamaño del tablero (mínimo 4 y con numero PAR): ")
                n = int(n)
                limpiar_consola()
                tablero = generar_tablero(n)
                equipo_a = []
                equipo_r = []
                historial = []
                llenar_tablero(tablero, equipo_a, equipo_r)
                parar_juego = False

                escoger_equipo = input("Seleccione su equipo (X para azul, O para rojo): ").upper()
                while escoger_equipo not in ["X", "O"]:
                    print("ERROR: Ingrese un equipo válido (X o O)")
                    escoger_equipo = input("Seleccione su equipo (X para azul, O para rojo): ").upper()

                if escoger_equipo == "X":
                    agente = Agente("rojo")
                    agente.asignar_fichas(equipo_r, equipo_a)

                else:
                    agente = Agente("azul")
                    agente.asignar_fichas(equipo_a, equipo_r)

                while not parar_juego:
                    print("Turno del equipo de las X")
                    imprimir_tablero(tablero)

                    if equipo_bloqueado(equipo_a, tablero):
                        print("El equipo de las X no puede moverse. Gana el equipo de las O")
                        time.sleep(5)
                        exit()
                    elif equipo_bloqueado(equipo_r, tablero):
                        print("El equipo de las O no puede moverse. Gana el equipo de las X")
                        time.sleep(5)
                        exit()

                    if escoger_equipo == "X":
                        coordenada_jugar = None
                        while coordenada_jugar is None:
                            coordenada_jugar = seleccion_ficha("azul", tablero)
                        for ficha in equipo_a:
                            if ficha.posicion == coordenada_jugar:
                                ficha.mover_ficha(tablero)
                    else:
                        
                        ficha_elegida, movimiento_elegido = agente.mejor_movimiento(tablero)
                        agente.aplicar_movimiento(tablero, ficha_elegida, movimiento_elegido)
                    

                    if faltan_fichas_coronar(equipo_a):
                        print("Felicidades. Gana el equipo de las X")
                        time.sleep(5)
                        exit()

                    hay_repeticion(tablero, "X", historial)
                    limpiar_consola()   

                    print("Turno del equipo de los O")
                    imprimir_tablero(tablero)

                    if faltan_fichas_coronar(equipo_a) or faltan_fichas_coronar(equipo_r):
                        pass  # ya se validó arriba, pero si acabó de coronar X, no debe jugar O
                    elif equipo_bloqueado(equipo_a, tablero):
                        print("El equipo de las X no puede moverse. Gana el equipo de las O")
                        time.sleep(5)
                        exit()
                    elif equipo_bloqueado(equipo_r, tablero):
                        print("El equipo de las O no puede moverse. Gana el equipo de las X")
                        time.sleep(5)
                        exit()

                    if escoger_equipo == "O":
                        coordenada_jugar = None
                        while coordenada_jugar is None:
                            coordenada_jugar = seleccion_ficha("rojo", tablero)
                        for ficha in equipo_r:
                            if ficha.posicion == coordenada_jugar:
                                ficha.mover_ficha(tablero)
                    else:
        
                        ficha_elegida, movimiento_elegido = agente.mejor_movimiento(tablero)
                        agente.aplicar_movimiento(tablero, ficha_elegida, movimiento_elegido)

                    if faltan_fichas_coronar(equipo_r):
                        print("Felicidades. Gana el equipo de las O")
                        time.sleep(5)
                        exit()

                    hay_repeticion(tablero, "O", historial)
                    limpiar_consola()
                         
            elif opcion_sub_menu == "3":
                continue

        elif opcion == "2":
            print("Saliendo del juego...")
            time.sleep(2)
            exit()
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")
            time.sleep(2)
            limpiar_consola()

if __name__ == "__main__":
    jugar()