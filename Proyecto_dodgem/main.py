# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

import time
from tablero import (imprimir_tablero, generar_tablero, limpiar_consola,
                     generar_codigo)
from juego import (llenar_tablero, seleccion_ficha, faltan_fichas_coronar,
                   equipo_bloqueado)


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
                    coordenada_jugar = None
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
                    else:
                        while coordenada_jugar is None:
                            coordenada_jugar = seleccion_ficha("azul", tablero)
                
                        for ficha in equipo_a:
                            if ficha.posicion == coordenada_jugar:
                                ficha.mover_ficha(tablero)
                        if faltan_fichas_coronar(equipo_a):
                            print("Felicidades. Gana el equipo de las X")
                            time.sleep(5)
                            exit()
                            
                        codigo_actual = generar_codigo(tablero, "X")
                        if historial.count(codigo_actual) >= 3:
                            print(
                                "Debido a repetición de movimientos,"
                                "el juego queda en empate."
                            )
                            time.sleep(5)
                            exit()
                        historial.append(codigo_actual)
                        limpiar_consola()
                            
                        # Juega O
                        print("Turno del equipo de los O")
                        imprimir_tablero(tablero)
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
                            
                        codigo_actual = generar_codigo(tablero, "O")
                        if historial.count(codigo_actual) >= 3:
                            print(
                                "Debido a repetición de movimientos,"
                                "el juego queda en empate."
                            )
                            time.sleep(5)
                            exit()
                        historial.append(codigo_actual)
                        limpiar_consola()
                        break
                
            elif opcion_sub_menu == "2":
                print("Iniciando juego contra la IA...")
                time.sleep(2)
                break
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