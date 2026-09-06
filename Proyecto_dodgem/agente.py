# Martín Araneda 21.858.236-2
# Isabella Quintero 25.868.144-4
# Stefano Negroni 21.945.448-1

import random
from math import inf
from juego import equipo_bloqueado, faltan_fichas_coronar

class Agente:
    def __init__(self, equipo, nombre="Agente", profundidad=3):
        self.equipo = equipo
        self.nombre = nombre
        self.profundidad = profundidad
        self.fichas = []
        self.fichas_rival = []
        self.nodos = 0
    
    def asignar_fichas(self, fichas_propias, fichas_rival):
        self.fichas = fichas_propias
        self.fichas_rival = fichas_rival

    def obtener_movimientos_posibles(self, tablero, fichas):
        movimientos = []
        
        for ficha in fichas:
            if ficha.corona:
                continue

            # Movimiento hacia arriba
            if ficha.posicion[0] > 0 and tablero[ficha.posicion[0] - 1][ficha.posicion[1]] == '.':
                movimientos.append((ficha, 1))
            
            # Movimiento hacia la derecha
            if ficha.posicion[1] < len(tablero) - 1 and tablero[ficha.posicion[0]][ficha.posicion[1] + 1] == '.': 
                movimientos.append((ficha, 2))
            
             
            if ficha.equipo == "azul":  # Movimiento hacia abajo 
                if ficha.posicion[0] < len(tablero) - 1 and tablero[ficha.posicion[0] + 1][ficha.posicion[1]] == '.':
                    movimientos.append((ficha, 3))
            else:   # Movimiento hacia la izquierda
                if ficha.posicion[1] > 0 and tablero[ficha.posicion[0]][ficha.posicion[1] - 1] == '.':
                    movimientos.append((ficha, 3))

            # Agregar posibilidad de coronar                                                                        
            if ficha.equipo == "azul" and ficha.posicion[1] == len(tablero) - 1:
                movimientos.append((ficha, 2))  # Coronación hacia la derecha
            elif ficha.equipo == "rojo" and ficha.posicion[0] == 0:
                movimientos.append((ficha, 1))  # Coronación hacia arriba

        return movimientos
    
    def simular_movimiento(self, tablero, ficha, movimiento):
        
        nuevo_tablero = [fila[:] for fila in tablero]
        corona = False
        nueva_fila = ficha.posicion[0]
        nueva_columna = ficha.posicion[1]
        
        if movimiento == 1:  # Arriba
            nueva_fila = ficha.posicion[0] - 1
            if ficha.equipo == "rojo" and nueva_fila == 0:
                corona = True
        elif movimiento == 2:  # Derecha
            nueva_columna = ficha.posicion[1] + 1
            if ficha.equipo == "azul" and nueva_columna == len(tablero) - 1:
                corona = True
        elif movimiento == 3:
            if ficha.equipo == "azul":  # Abajo
                nueva_fila = ficha.posicion[0] + 1
            else:  # rojo - Izquierda
                nueva_columna = ficha.posicion[1] - 1
        
        nuevo_tablero[ficha.posicion[0]][ficha.posicion[1]] = "."
        if ficha.equipo == "azul":
            nuevo_tablero[nueva_fila][nueva_columna] = "X"
        else:
            nuevo_tablero[nueva_fila][nueva_columna] = "O"
        
        return nuevo_tablero, [nueva_fila, nueva_columna], corona
    
    def es_terminal(self, tablero, es_turno_agente):
        if faltan_fichas_coronar(self.fichas):
            return True, 1
        if equipo_bloqueado(self.fichas, tablero):
            return True, -1

        if es_turno_agente:
            fichas_que_mueven = self.fichas
        else:
            fichas_que_mueven = self.fichas_rival

        if equipo_bloqueado(fichas_que_mueven, tablero):
            return True, -1 if es_turno_agente else 1
        
        return False, 0
    
    def evaluar_estado(self, tablero):
        n = len(tablero)   
        progreso_propio = 0
        for ficha in self.fichas:
            if ficha.corona:
                progreso_propio += 100
                continue
            distancia = (n - 1 - ficha.posicion[1]) if ficha.equipo == "azul" else ficha.posicion[0]
            progreso_propio += 10 / (distancia + 1)
            
        progreso_rival = 0
        for ficha in self.fichas_rival:
            if ficha.corona:
                progreso_rival += 100
                continue
            distancia = (n - 1 - ficha.posicion[1]) if ficha.equipo == "azul" else ficha.posicion[0]
            progreso_rival += 10 / (distancia + 1)

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