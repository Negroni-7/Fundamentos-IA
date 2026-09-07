# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

import random
from math import inf
from juego import equipo_bloqueado, faltan_fichas_coronar

class Agente:
    def __init__(self, equipo, nombre="Agente", profundidad=8):
        self.equipo = equipo
        self.nombre = nombre
        self.profundidad = profundidad
        self.fichas = []
        self.fichas_rival = []
        self.nodos = 0

    def asignar_fichas(self, fichas_propias, fichas_rival):
        self.fichas = fichas_propias
        self.fichas_rival = fichas_rival

    def aplicar_movimiento(self, tablero, ficha, movimiento):
        """Aplica de forma permanente el movimiento elegido sobre el tablero real."""
        nuevo_tablero, nueva_pos, corona = self.simular_movimiento(tablero, ficha, movimiento)

        for i in range(len(tablero)):
            for j in range(len(tablero)):
                tablero[i][j] = nuevo_tablero[i][j]

        ficha.posicion = nueva_pos
        ficha.corona = corona
        
    def mejor_movimiento(self, tablero):
        """Evalúa cada jugada propia posible en la raíz y devuelve la
        (ficha, movimiento) que produce el mejor valor."""
        movimientos = self.obtener_movimientos_posibles(tablero, self.fichas)
        
        movimientos_coronacion = []
        movimientos_normales = []
        
        for ficha, movimiento in movimientos:
            if ficha.equipo == "azul" and ficha.posicion[1] == len(tablero) - 1:
                movimientos_coronacion.append((ficha, movimiento))
            elif ficha.equipo == "rojo" and ficha.posicion[0] == 0:
                movimientos_coronacion.append((ficha, movimiento))
            else:
                movimientos_normales.append((ficha, movimiento))
        
        if movimientos_coronacion:
            ficha, movimiento = movimientos_coronacion[0]
            return ficha, movimiento

        mejor_valor = -inf
        mejor_ficha = None
        mejor_jugada = None
        alfa = -inf
        beta = inf

        for ficha, movimiento in movimientos_normales:
            nuevo_tablero, nueva_pos, corona = self.simular_movimiento(tablero, ficha, movimiento)

            pos_original = ficha.posicion[:]
            corona_original = ficha.corona
            ficha.posicion = nueva_pos
            ficha.corona = corona

            valor = self.alfa_beta_limitada(nuevo_tablero, False, self.profundidad - 1, alfa, beta)

            ficha.posicion = pos_original
            ficha.corona = corona_original

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_ficha = ficha
                mejor_jugada = movimiento

            alfa = max(alfa, mejor_valor)

        return mejor_ficha, mejor_jugada
    
    def asignar_fichas(self, fichas_propias, fichas_rival):
        self.fichas = fichas_propias
        self.fichas_rival = fichas_rival

    def obtener_movimientos_posibles(self, tablero, fichas):
        movimientos = []
        
        for ficha in fichas:
            if ficha.corona:
                continue

            fila, columna = ficha.posicion

            # Agregar posibilidad de coronar                                                                        
            if ficha.equipo == "azul" and ficha.posicion[1] == len(tablero) - 1:
                movimientos.append((ficha, 2))  # Coronación hacia la derecha
            elif ficha.equipo == "rojo" and ficha.posicion[0] == 0:
                movimientos.append((ficha, 1))  # Coronación hacia arriba

            # Movimiento hacia arriba
            if fila > 0 and tablero[fila - 1][columna] == '.':
                movimientos.append((ficha, 1))
            
            # Movimiento hacia la derecha
            if columna < len(tablero) - 1 and tablero[fila][columna + 1] == '.': 
                movimientos.append((ficha, 2))
             
            if ficha.equipo == "azul":  # Movimiento hacia abajo 
                if ficha.posicion[0] < len(tablero) - 1 and tablero[ficha.posicion[0] + 1][ficha.posicion[1]] == '.':
                    movimientos.append((ficha, 3))
            else:   # Movimiento hacia la izquierda
                if ficha.posicion[1] > 0 and tablero[ficha.posicion[0]][ficha.posicion[1] - 1] == '.':
                    movimientos.append((ficha, 3))

            

        return movimientos
    
    def simular_movimiento(self, tablero, ficha, movimiento):
        nuevo_tablero = [fila[:] for fila in tablero]
        corona = False
        nueva_fila = ficha.posicion[0]
        nueva_columna = ficha.posicion[1]

        fila, columna = ficha.posicion

        if movimiento == 1:  # Arriba
            if ficha.equipo == "rojo" and fila == 0:
                corona = True
                nuevo_tablero[fila][columna] = "."
                return nuevo_tablero, [fila, columna], corona
            else:
                nueva_fila = fila - 1
        elif movimiento == 2:  # Derecha
            if ficha.equipo == "azul" and columna == len(tablero) - 1:
                corona = True
                nuevo_tablero[fila][columna] = "."
                return nuevo_tablero, [fila, columna], corona
            else:
                nueva_columna = columna + 1
        elif movimiento == 3:
            if ficha.equipo == "azul":  # Abajo
                nueva_fila = fila + 1
            else:  # rojo - Izquierda
                nueva_columna = columna - 1

        nuevo_tablero[fila][columna] = "."
        if not corona:
            simbolo = "X" if ficha.equipo == "azul" else "O"
            nuevo_tablero[nueva_fila][nueva_columna] = simbolo

        return nuevo_tablero, [nueva_fila, nueva_columna], corona
    
    def es_terminal(self, tablero, es_turno_agente):
        inf = float('inf')
        if faltan_fichas_coronar(self.fichas):
            return True, inf
        if equipo_bloqueado(self.fichas, tablero):
            return True, -inf

        if es_turno_agente:
            fichas_que_mueven = self.fichas
        else:
            fichas_que_mueven = self.fichas_rival

        if equipo_bloqueado(fichas_que_mueven, tablero):
            return True, -inf if es_turno_agente else inf
        
        return False, 0
    
    def evaluar_estado(self, tablero):
        n = len(tablero)
        valor_avance = 5
        penalizacion_obstaculo = 3
        penalizacion_lateral = 1.5

        progreso_propio = 0
        for ficha in self.fichas:
            fila, columna = ficha.posicion
            if ficha.corona:
                progreso_propio += 100
                continue
            distancia = (n - 1 - columna) if ficha.equipo == "azul" else fila
            progreso_propio += valor_avance * (n - distancia)

            if ficha.equipo == "azul":
                if columna < n - 1 and tablero[fila][columna + 1] != ".": # Si hay un obstáculo a la derecha, penalizar
                    progreso_propio -= penalizacion_obstaculo
                if fila > 0 and tablero[fila - 1][columna] != ".": # Si hay un obstáculo arriba, penalizar
                    progreso_propio -= penalizacion_lateral
                if fila < n - 1 and tablero[fila + 1][columna] != ".": # Si hay un obstáculo abajo, penalizar
                    progreso_propio -= penalizacion_lateral
            else:
                if fila > 0 and tablero[fila - 1][columna] != ".": # Si hay un obstáculo arriba, penalizar
                    progreso_propio -= penalizacion_obstaculo
                if columna < n - 1 and tablero[fila][columna + 1] != ".": # Si hay un obstáculo a la derecha, penalizar                
                    progreso_propio -= penalizacion_lateral
                if columna > 0 and tablero[fila][columna - 1] != ".": # Si hay un obstáculo a la izquierda, penalizar
                    progreso_propio -= penalizacion_lateral
                    
        progreso_rival = 0
        for ficha in self.fichas_rival:
            if ficha.corona:
                progreso_rival += 100
                continue
            fila, columna = ficha.posicion
            distancia = (n - 1 - columna) if ficha.equipo == "azul" else fila
            progreso_rival += valor_avance * (n - distancia)

            if ficha.equipo == "azul":
                if columna < n - 1 and tablero[fila][columna + 1] != ".":
                    progreso_rival -= penalizacion_obstaculo
                if fila > 0 and tablero[fila - 1][columna] != ".":
                    progreso_rival -= penalizacion_lateral
                if fila < n - 1 and tablero[fila + 1][columna] != ".":
                    progreso_rival -= penalizacion_lateral
            else:
                if fila > 0 and tablero[fila - 1][columna] != ".":
                    progreso_rival -= penalizacion_obstaculo
                if columna < n - 1 and tablero[fila][columna + 1] != ".":
                    progreso_rival -= penalizacion_lateral
                if columna > 0 and tablero[fila][columna - 1] != ".":
                    progreso_rival -= penalizacion_lateral * 0.5

        return progreso_propio - progreso_rival
    
    def alfa_beta_limitada(self, tablero, es_turno_agente, profundidad, alfa, beta):
        self.nodos += 1
        
        # CASOS BASE
        es_terminal, valor = self.es_terminal(tablero, es_turno_agente)
        if es_terminal:
            return valor
        
        if profundidad == 0:
            return self.evaluar_estado(tablero)
        
        fichas_que_mueven = self.fichas if es_turno_agente else self.fichas_rival
        movimientos = self.obtener_movimientos_posibles(tablero, fichas_que_mueven)
        if not movimientos:
            return self.evaluar_estado(tablero)
        
        # CASOS RECURSIVOS 
        if es_turno_agente:  # MAX
            mejor_valor = -inf
            for ficha, movimiento in movimientos:
                nuevo_tablero, nueva_pos, corona = self.simular_movimiento(tablero, ficha, movimiento)
                
                pos_original = ficha.posicion[:]
                corona_original = ficha.corona
                
                ficha.posicion = nueva_pos
                ficha.corona = corona
                
                valor = self.alfa_beta_limitada(nuevo_tablero, False, profundidad - 1, alfa, beta)
                
                ficha.posicion = pos_original
                ficha.corona = corona_original
                
                mejor_valor = max(mejor_valor, valor)
                alfa = max(alfa, mejor_valor)
                
                if alfa >= beta:
                    break
            
            return mejor_valor
        
        else:  # MIN
            mejor_valor = inf
            for ficha, movimiento in movimientos:
                nuevo_tablero, nueva_pos, corona = self.simular_movimiento(tablero, ficha, movimiento)
                
                pos_original = ficha.posicion[:]
                corona_original = ficha.corona
                
                ficha.posicion = nueva_pos
                ficha.corona = corona
                
                valor = self.alfa_beta_limitada(nuevo_tablero, True, profundidad - 1, alfa, beta)
                
                ficha.posicion = pos_original
                ficha.corona = corona_original
                
                mejor_valor = min(mejor_valor, valor)
                beta = min(beta, mejor_valor)
                
                if alfa >= beta:
                    break
            
            return mejor_valor