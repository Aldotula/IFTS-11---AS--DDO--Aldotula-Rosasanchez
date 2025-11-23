# utilidades.py

import csv
import json
from datetime import datetime
# Importa las clases de datos del módulo modelo
from modelo import Cliente, Turno

# --- CONFIGURACIÓN DE ARCHIVOS ---
ARCHIVO_CLIENTES = "clientes.csv"
ARCHIVO_TURNOS = "turnos.csv"
ARCHIVO_DICT = "datos.json"

# ======================================================================
# 1. CLASES DE UTILIDAD (LÓGICA y PERSISTENCIA)
# ======================================================================

class Slot:
    #Clase Utilidad: Contiene la lógica para calcular y validar horarios disponibles#
    def _hora_a_minutos(self, hora_texto):
        #Auxiliar: Convierte una hora en formato 'HH:MM' a minutos totales#
        try:
            horas, minutos = map(int, hora_texto.split(":"))
            return (horas * 60) + minutos
        except: return 0

    def obtener_horarios(self, fecha_texto, duracion, profesional, lista_turnos):
        #Calcula los horarios disponibles para un profesional en un día dado#
        try: 
            # Valida la fecha y excluye domingos (weekday() == 6)
            if datetime.strptime(fecha_texto, "%Y-%m-%d").weekday() == 6: 
                print("La peluquería no abre los domingos.")
                return []
        except: 
            print("Fecha inválida o formato incorrecto (use YYYY-MM-DD).")
            return []
        
        # Bloques de trabajo en minutos totales (9:00 a 13:00 y 15:00 a 18:00)
        bloques_trabajo = [(540, 780), (900, 1080)]
        horarios_disponibles = []
        
        for inicio_bloque, fin_bloque in bloques_trabajo:
            tiempo_actual = inicio_bloque
            while tiempo_actual + duracion <= fin_bloque:
                esta_ocupado = False
                
                for turno in lista_turnos:
                    # Filtra por el mismo profesional y fecha
                    if turno.nombre_profesional == profesional and turno.fecha == fecha_texto:
                        inicio_existente, fin_existente = self._hora_a_minutos(turno.hora), self._hora_a_minutos(turno.hora) + turno.duracion
                        inicio_nuevo, fin_nuevo = tiempo_actual, tiempo_actual + duracion
                        
                        # Condición de solapamiento
                        if inicio_nuevo < fin_existente and inicio_existente < fin_nuevo: 
                            esta_ocupado = True; break
                
                if not esta_ocupado:
                    horas = tiempo_actual // 60
                    minutos = tiempo_actual % 60
                    horarios_disponibles.append(f"{horas:02}:{minutos:02}")
                tiempo_actual += 30 # Intervalo de avance de 30 minutos
        return horarios_disponibles

class Transformador:
    def guardar(self, lista_clientes, lista_turnos):
        #Guarda todos los datos en archivos CSV y JSON (usando utf-8)#
        try:
            #Guardar Clientes en CSV
            with open(ARCHIVO_CLIENTES, 'w', newline='', encoding='utf-8') as archivo_csv: 
                campos_cliente = list(Cliente("","","","").to_dict().keys())
                escritor_cliente = csv.DictWriter(archivo_csv, fieldnames=campos_cliente, delimiter=';')
                escritor_cliente.writeheader() # <-- CORRECCIÓN: Escribe la fila de nombres de columna
                escritor_cliente.writerows([cliente.to_dict() for cliente in lista_clientes])
            
            #Guardar Turnos en CSV
            with open(ARCHIVO_TURNOS, 'w', newline='', encoding='utf-8') as archivo_csv:
                campos_turno = list(Turno("","","","","","","","",0).to_dict().keys())
                escritor_turno = csv.DictWriter(archivo_csv, fieldnames=campos_turno, delimiter=';')
                escritor_turno.writeheader() # <-- CORRECCIÓN: Escribe la fila de nombres de columna
                escritor_turno.writerows([turno.to_dict() for turno in lista_turnos])
            
            #Guardar en JSON
            with open(ARCHIVO_DICT, 'w', encoding='utf-8') as archivo_json:
                json.dump({"clientes": [cliente.to_dict() for cliente in lista_clientes], "turnos": [turno.to_dict() for turno in lista_turnos]}, archivo_json, indent=4)
        except Exception as error: print(f"ERROR: Falló la persistencia: {error}")
    
    def cargar(self):
        #Carga datos desde CSV. Si CSV no existe, intenta cargar desde JSON#
        lista_clientes, lista_turnos = [], []
        try: #Intentar cargar CSV
            with open(ARCHIVO_CLIENTES, 'r', encoding='utf-8') as f_c: lista_clientes = [Cliente(fila["id_cliente"], fila["nombre"], fila["apellido"], fila["telefono"]) for fila in csv.DictReader(f_c, delimiter=';')]
            with open(ARCHIVO_TURNOS, 'r', encoding='utf-8') as f_t:
                for fila in csv.DictReader(f_t, delimiter=';'): lista_turnos.append(Turno(fila["id_turno"], fila["id_cliente"], fila["nombre_cliente"], fila["apellido_cliente"], fila["nombre_profesional"], fila["servicio"], fila["fecha"], fila["hora"], int(fila["duracion"])))
        except FileNotFoundError:
            try: #Intentar cargar JSON
                with open(ARCHIVO_DICT, 'r', encoding='utf-8') as f_d:
                    datos = json.load(f_d)
                    lista_clientes = [Cliente(f["id_cliente"], f["nombre"], f["apellido"], f["telefono"]) for f in datos.get("clientes", [])]
                    for f in datos.get("turnos", []): lista_turnos.append(Turno(f["id_turno"], f["id_cliente"], f["nombre_cliente"], f["apellido_cliente"], f["nombre_profesional"], f["servicio"], f["fecha"], f["hora"], int(f["duracion"])))
            except: pass
        except Exception as error: print(f"ERROR al cargar datos: {error}")
        return lista_clientes, lista_turnos
