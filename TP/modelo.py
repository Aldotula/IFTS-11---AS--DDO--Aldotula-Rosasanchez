# modelo.py

# ======================================================================
# 1. CLASES DE DATOS (MODELO)
# Clases que representan las entidades principales (Cliente, Turno, Profesional).
# ======================================================================

class Profesional:
    def __init__(self, nombre, especialidades):
        self.nombre = nombre
        self.especialidades = especialidades
    
    def realiza_servicio(self, servicio):
        #Verifica si el profesional está calificado para realizar un servicio#
        return servicio in self.especialidades

class Cliente:
    def __init__(self, id_cliente, nombre, apellido, telefono):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        
    def to_dict(self):
        #Convierte el objeto Cliente a diccionario#
        return {"id_cliente": self.id_cliente, "nombre": self.nombre, 
                "apellido": self.apellido, "telefono": self.telefono}

class Turno:
    def __init__(self, id_turno, id_cliente, nombre_cliente, apellido_cliente, nombre_profesional, servicio, fecha, hora, duracion):
        self.id_turno = id_turno
        self.id_cliente = id_cliente
        self.nombre_cliente = nombre_cliente
        self.apellido_cliente = apellido_cliente
        self.nombre_profesional = nombre_profesional
        self.servicio = servicio
        self.fecha = fecha
        self.hora = hora
        self.duracion = int(duracion) 
        
    def to_dict(self):
        #Convierte el objeto Turno a diccionario#
        return {"id_turno": self.id_turno, "id_cliente": self.id_cliente, "nombre_cliente": self.nombre_cliente, 
                "apellido_cliente": self.apellido_cliente, "nombre_profesional": self.nombre_profesional, 
                "servicio": self.servicio, "fecha": self.fecha, "hora": self.hora, "duracion": self.duracion}
                