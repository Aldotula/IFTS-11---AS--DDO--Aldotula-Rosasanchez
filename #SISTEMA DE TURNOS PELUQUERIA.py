#SISTEMA DE TURNOS PELUQUERIA
# EQUIPO: ROSA SANCHEZ, ALDO TULA, CRISTIAN RINCON
import csv
from datetime import datetime

# CLASE CLIENTE
class Cliente:
    def __init__(self, id_cliente, nombre, telefono):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono

    def convertir(self):
        return {
            "id_cliente": self.id_cliente,
            "cliente_nombre": self.nombre,
            "cliente_telefono": self.telefono
        }

# CLASE PROFESIONAL
class Profesional:
    def __init__(self, nombre):
        self.nombre = nombre


# CLASE SLOT (fecha y hora)
class Slot:
    def __init__(self, fecha, hora):
        self.fecha = fecha
        self.hora = hora

# CLASE TURNO
class Turno:
    def __init__(self, id_turno, cliente, profesional, slot, servicio):
        self.id_turno = id_turno
        self.cliente = cliente
        self.profesional = profesional
        self.slot = slot
        self.servicio = servicio
        self.estado = "reservado"

    def convertir(self):
        return {
            "id_turno": self.id_turno,
            "id_cliente": self.cliente.id_cliente,
            "cliente_nombre": self.cliente.nombre,
            "cliente_telefono": self.cliente.telefono,
            "profesional": self.profesional.nombre,
            "fecha": self.slot.fecha,
            "hora": self.slot.hora,
            "servicio": self.servicio,
            "estado": self.estado
        }

# CLASE TRANSFORMADOR
class Transformador:
    def convertir_a_dict(self, turno):
        return turno.convertir()

# CLASE PELUQUERIA
class Peluqueria:
    def __init__(self):
        self.clientes = {}
        self.turnos = {}
        self.contador_clientes = 0
        self.contador_turnos = 0
        self.transformador = Transformador()
        self.archivo_csv = "turnos.csv"

        self.profesionales = {
            "JORGE": Profesional("JORGE"),
            "MARIA": Profesional("MARIA")
        }

        self.cargar_csv()

    # ---------- CREAR CLIENTE ----------
    def crear_cliente(self, nombre, telefono):
        self.contador_clientes += 1
        id_cliente = "CLIENTE" + str(self.contador_clientes)
        cliente = Cliente(id_cliente, nombre, telefono)
        self.clientes[id_cliente] = cliente
        self.guardar_csv()
        return cliente

    # ---------- VALIDAR HORARIO NO REPETIDO ----------
    def horario_ocupado(self, fecha, hora):
        for turno_existente in self.turnos.values():
            if turno_existente.slot.fecha == fecha and turno_existente.slot.hora == hora:
                return True
        return False

    # ---------- CREAR TURNO ----------
    def crear_turno(self, cliente, profesional, fecha, hora, servicio):

        if self.horario_ocupado(fecha, hora):
            print("Ese horario ya está reservado.")
            return None

        self.contador_turnos += 1
        id_turno = "TURNO" + str(self.contador_turnos)
        slot = Slot(fecha, hora)
        turno = Turno(id_turno, cliente, profesional, slot, servicio)
        self.turnos[id_turno] = turno
        self.guardar_csv()
        return turno

    # ---------- MODIFICAR ----------
    def modificar_turno(self, id_turno, nueva_fecha=None, nueva_hora=None,
                        nuevo_servicio=None, nuevo_profesional=None):

        turno = self.turnos[id_turno]

        if nueva_fecha and nueva_hora:
            if self.horario_ocupado(nueva_fecha, nueva_hora):
                print("Ese nuevo horario está ocupado.")
                return

        if nueva_fecha:
            turno.slot.fecha = nueva_fecha
        if nueva_hora:
            turno.slot.hora = nueva_hora
        if nuevo_servicio:
            turno.servicio = nuevo_servicio
        if nuevo_profesional:
            turno.profesional = nuevo_profesional

        self.guardar_csv()

    # ---------- CANCELAR ----------
    def cancelar_turno(self, id_turno):
        self.turnos[id_turno].estado = "cancelado"
        self.guardar_csv()

    # ---------- LISTAR ----------
    def listar_turnos(self):
        return list(self.turnos.values())

    # ---------- GUARDAR CSV ----------
    def guardar_csv(self):

        lista_turnos = [self.transformador.convertir_a_dict(turno) for turno in self.turnos.values()]

        with open(self.archivo_csv, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=[
                "id_turno", "id_cliente", "cliente_nombre", "cliente_telefono",
                "profesional", "fecha", "hora", "servicio", "estado"
            ])
            escritor.writeheader()
            for datos_turno in lista_turnos:
                escritor.writerow(datos_turno)

    # ---------- CARGAR CSV ----------
    def cargar_csv(self):

        try:
            archivo = open(self.archivo_csv, encoding="utf-8")
        except FileNotFoundError:
            return

        with archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:

                id_cliente = fila["id_cliente"]

                if id_cliente not in self.clientes:
                    cliente = Cliente(id_cliente, fila["cliente_nombre"], fila["cliente_telefono"])
                    self.clientes[id_cliente] = cliente
                else:
                    cliente = self.clientes[id_cliente]

                profesional = Profesional(fila["profesional"])
                slot = Slot(fila["fecha"], fila["hora"])
                turno = Turno(fila["id_turno"], cliente, profesional, slot, fila["servicio"])
                turno.estado = fila["estado"]

                self.turnos[turno.id_turno] = turno

# CLASE MENU
class Menu:
    def __init__(self):
        self.peluqueria = Peluqueria()

    def iniciar(self):
        while True:
            print("\n===== MENÚ PRINCIPAL =====")
            print("1 - Registrar nuevo cliente")
            print("2 - Solicitar turno")
            print("3 - Listar turnos existentes")
            print("4 - Modificar o cancelar turno")
            print("5 - Guardar datos en CSV / Cargar desde dict")
            print("6 - Salir\n")

            opcion_menu = input("Seleccione una opción: ")

            if opcion_menu == "1":
                self.registrar_cliente()
            elif opcion_menu == "2":
                self.solicitar_turno()
            elif opcion_menu == "3":
                self.listar_turnos()
            elif opcion_menu == "4":
                self.modificar_o_cancelar()
            elif opcion_menu == "5":
                self.guardar_o_cargar()
            elif opcion_menu == "6":
                print("Saliendo...")
                break
            else:
                print("Opción incorrecta.")

    # ---------- REGISTRAR CLIENTE ----------
    def registrar_cliente(self):
        print("\nREGISTRAR CLIENTE")
        nombre = input("Nombre: ")
        telefono = input("Teléfono (solo números): ")
        cliente = self.peluqueria.crear_cliente(nombre, telefono)
        print("Cliente creado. ID:", cliente.id_cliente)

    # ---------- SOLICITAR TURNO ----------
    def solicitar_turno(self):
        print("\nSOLICITAR TURNO")

        id_cliente = input("ID Cliente: ")

        if id_cliente not in self.peluqueria.clientes:
            print("Ese cliente no existe.")
            return

        cliente = self.peluqueria.clientes[id_cliente]

        fecha = input("Fecha (AAAA-MM-DD): ")
        hora = input("Hora (HH:MM): ")
        servicio = input("Servicio: ")
        profesional_nombre = input("Profesional (JORGE/MARIA): ")

        if profesional_nombre not in self.peluqueria.profesionales:
            print("Profesional no válido.")
            return

        profesional = self.peluqueria.profesionales[profesional_nombre]

        turno = self.peluqueria.crear_turno(cliente, profesional, fecha, hora, servicio)

        if turno:
            print("Turno creado. ID:", turno.id_turno)

    # ---------- LISTAR ----------
    def listar_turnos(self):
        print("\nLISTADO DE TURNOS")
        lista_turnos = self.peluqueria.listar_turnos()

        if len(lista_turnos) == 0:
            print("No hay turnos.")
            return

        for turno in lista_turnos:
            print("\n----- TURNO -----")
            print("ID:", turno.id_turno)
            print("Fecha:", turno.slot.fecha)
            print("Hora:", turno.slot.hora)
            print("Cliente:", turno.cliente.nombre)
            print("Profesional:", turno.profesional.nombre)
            print("Servicio:", turno.servicio)
            print("Estado:", turno.estado)

    # ---------- MODIFICAR O CANCELAR ----------
    def modificar_o_cancelar(self):
        print("\nMODIFICAR O CANCELAR TURNO")
        id_turno = input("ID del turno: ")

        if id_turno not in self.peluqueria.turnos:
            print("No existe ese turno.")
            return

        print("\n1 - Modificar turno")
        print("2 - Cancelar turno")
        print("3 - Volver")

        opcion_modificar_cancelar = input("Seleccione: ")

        if opcion_modificar_cancelar == "1":
            nueva_fecha = input("Nueva fecha o Enter: ")
            nueva_hora = input("Nueva hora o Enter: ")
            nuevo_servicio = input("Nuevo servicio o Enter: ")
            nuevo_profesional_nombre = input("Nuevo profesional o Enter: ")

            profesional_seleccionado = None
            if nuevo_profesional_nombre:
                if nuevo_profesional_nombre in self.peluqueria.profesionales:
                    profesional_seleccionado = self.peluqueria.profesionales[nuevo_profesional_nombre]

            self.peluqueria.modificar_turno(
                id_turno,
                nueva_fecha if nueva_fecha else None,
                nueva_hora if nueva_hora else None,
                nuevo_servicio if nuevo_servicio else None,
                profesional_seleccionado
            )

            print("Turno modificado.")

        elif opcion_modificar_cancelar == "2":
            self.peluqueria.cancelar_turno(id_turno)
            print("Turno cancelado.")

    # ---------- GUARDAR / CARGAR ----------
    def guardar_o_cargar(self):
        print("\n1 - Guardar en CSV")
        print("2 - Cargar CSV (ya se hace al iniciar)")
        print("3 - Volver")

        opcion_guardar_cargar = input("Seleccione: ")

        if opcion_guardar_cargar == "1":
            self.peluqueria.guardar_csv()
            print("Datos guardados.")

# INICIO DEL PROGRAMA
if __name__ == "__main__":
    Menu().iniciar()
