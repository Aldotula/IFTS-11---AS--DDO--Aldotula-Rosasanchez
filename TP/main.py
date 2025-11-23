# main.py

import sys
# Importar las clases Modelo (entidades)
from modelo import Profesional, Cliente, Turno
# Importar las clases de Utilidad (lógica y persistencia)
from utilidades import Slot, Transformador

# ======================================================================
# 3. CLASE GESTORA (CONTROLADOR PRINCIPAL)
# ======================================================================

class GestorTurnos:
    #Clase Principal: Administra las operaciones, las listas y el menú#
    def __init__(self):
        # Inicializa las clases de utilidad
        self.transformador = Transformador()
        self.slot = Slot() 
        
        # Carga de datos al iniciar
        self.clientes, self.turnos = self.transformador.cargar()
        
        # Datos iniciales (Profesionales y Servicios)
        self.profesionales = [Profesional("JORGE", ["Corte", "Barba"]), Profesional("MARIA", ["Coloracion", "Alisado"])]
        self.servicios = {"1": {"nombre": "Corte", "duracion": 30}, "2": {"nombre": "Barba", "duracion": 30},
                          "3": {"nombre": "Coloracion", "duracion": 120}, "4": {"nombre": "Alisado", "duracion": 120}}
                          
        # Contadores para generar IDs secuenciales y únicos
        self.contador_cliente = self._obtener_maximo_id_numerico(self.clientes, "C")
        self.contador_turno = self._obtener_maximo_id_numerico(self.turnos, "T")

    # --- MÉTODOS AUXILIARES ---
    def _obtener_maximo_id_numerico(self, lista_objetos, prefijo):
        #Busca el número más alto en los IDs existentes para continuar la secuencia#
        maximo_numero = 0
        for objeto in lista_objetos:
            try:
                id_completo = getattr(objeto, f"id_{'cliente' if prefijo == 'C' else 'turno'}")
                maximo_numero = max(maximo_numero, int(id_completo[1:]))
            except: pass
        return maximo_numero

    def _existe_cliente(self, nombre, apellido):
        #Verifica si un cliente ya existe por nombre y apellido (Validación de duplicados)#
        for cliente in self.clientes:
            if cliente.nombre == nombre and cliente.apellido == apellido: return cliente
        return None

    def _generar_id_cliente(self):
        self.contador_cliente += 1; return f"C{self.contador_cliente:02d}"
        
    def _generar_id_turno(self):
        self.contador_turno += 1; return f"T{self.contador_turno:02d}"

    def _buscar_cliente(self):
        #Permite al usuario buscar un cliente por texto y seleccionarlo de la lista de encontrados#
        busqueda = input("Buscar cliente (Nombre/Apellido): ").strip().upper()
        encontrados = [cliente for cliente in self.clientes if busqueda in cliente.nombre or busqueda in cliente.apellido]
        if not encontrados: print("No se encontró ningún cliente."); return None
        
        print("\nClientes encontrados:")
        for indice, cliente in enumerate(encontrados): print(f"{indice+1}. [{cliente.id_cliente}] {cliente.apellido} {cliente.nombre}")
            
        try: return encontrados[int(input("Elija Nro: ")) - 1]
        except: return None

    # --- MÉTODOS DE MENÚ (OPERACIONES PRINCIPALES) ---
    def iniciar(self):
        #Muestra el menú principal y maneja la navegación#
        while True:
            print("\n=== GESTIÓN DE TURNOS ===\n1. Registrar cliente\n2. Solicitar turno\n3. Listar turnos\n4. Modificar/Cancelar\n5. Guardar/Cargar manual\n6. Salir")
            opcion = input("Opción: ")
            if opcion == "1": self._registrar_cliente()
            elif opcion == "2": self._crear_turno()
            elif opcion == "3": self._listar_turnos()
            elif opcion == "4": self._modificar_turnos()
            elif opcion == "5": self.transformador.guardar(self.clientes, self.turnos) 
            elif opcion == "6": self._salir()
            else: print("Opción no válida.")

    def _registrar_cliente(self):
        #Opción 1: Registra un cliente nuevo y guarda automáticamente#
        nombre = input("Nombre (MAYÚS): ").strip().upper(); apellido = input("Apellido (MAYÚS): ").strip().upper()
        if self._existe_cliente(nombre, apellido): print("¡ERROR! Cliente ya existe."); return
        
        self.clientes.append(Cliente(self._generar_id_cliente(), nombre, apellido, input("Teléfono: ").strip()))
        print(f"Cliente registrado. ID: {self.clientes[-1].id_cliente}")
        self.transformador.guardar(self.clientes, self.turnos)

    def _crear_turno(self):
        #Opción 2: Crea un turno, utilizando la lógica de Slot para disponibilidad#
        cliente = self._buscar_cliente()
        if not cliente: return 
        
        print("\nServicios: 1-Corte(30m) 2-Barba(30m) 3-Coloracion(2h) 4-Alisado(2h)")
        opcion_servicio = input("Servicio (1-4): ")
        if opcion_servicio not in self.servicios: return
        
        datos = self.servicios[opcion_servicio]; servicio, duracion = datos["nombre"], datos["duracion"]
        nombre_profesional = next((p.nombre for p in self.profesionales if p.realiza_servicio(servicio)), None)
        fecha = input("Fecha (YYYY-MM-DD): ")
        
        # Llama a la lógica de Slot para obtener los horarios
        horarios_disponibles = self.slot.obtener_horarios(fecha, duracion, nombre_profesional, self.turnos)
        if not horarios_disponibles: print("No hay horarios disponibles."); return
            
        print("\nHorarios disponibles:")
        for indice, hora in enumerate(horarios_disponibles): print(f"{indice+1}. {hora}")
            
        try:
            hora_elegida = horarios_disponibles[int(input("Nro de hora: ")) - 1]
            # Crea el objeto Turno y lo añade a la lista
            self.turnos.append(Turno(self._generar_id_turno(), cliente.id_cliente, cliente.nombre, cliente.apellido, nombre_profesional, servicio, fecha, hora_elegida, duracion))
            print(f"Turno registrado. ID: {self.turnos[-1].id_turno}")
            self.transformador.guardar(self.clientes, self.turnos)
        except: print("Error en la selección.")

    def _listar_turnos(self):
        #Opción 3: Muestra los turnos existentes, con opción de filtrar por fecha#
        opcion = input("1-Todos | 2-Por Fecha: "); lista_turnos = self.turnos
        if opcion == "2": lista_turnos = [turno for turno in self.turnos if turno.fecha == input("Fecha (YYYY-MM-DD): ")]
        if not lista_turnos: print("No hay turnos para mostrar."); return
        
        print(f"\n{'ID':<5} | {'FECHA':<10} | {'HORA':<6} | {'CLIENTE':<20} | {'SERVICIO'}")
        for turno in lista_turnos: 
            print(f"{turno.id_turno:<5} | {turno.fecha[5:]:<10} | {turno.hora:<6} | {turno.apellido_cliente}, {turno.nombre_cliente:<10} | {turno.servicio} ({turno.nombre_profesional})")

    def _modificar_turnos(self):
        #Opción 4: Permite al usuario reprogramar o eliminar un turno y guarda automáticamente#
        accion = input("1-Modificar (Reprogramar) | 2-Eliminar: ")
        cliente = self._buscar_cliente()
        if not cliente: return 
        
        turnos_del_cliente = [turno for turno in self.turnos if turno.id_cliente == cliente.id_cliente]
        if not turnos_del_cliente: 
            print("El cliente no tiene turnos."); return
        
        print("\nTurnos encontrados:")
        for indice, turno in enumerate(turnos_del_cliente): 
            print(f"{indice+1}. [{turno.id_turno}] {turno.servicio} el {turno.fecha} a las {turno.hora}")
            
        try:
            turno_a_procesar = turnos_del_cliente[int(input("Elija turno por número: ")) - 1]
            self.turnos.remove(turno_a_procesar) 
            
            if accion == "1": 
                print("\nTurno anterior eliminado. Cree el nuevo para reprogramar:")
                self._crear_turno() 
            else: 
                print("Turno eliminado exitosamente.")
                self.transformador.guardar(self.clientes, self.turnos) 
        except: print("Selección inválida.")

    def _salir(self):
        #Opción 6: Cierra el programa, preguntando si debe guardar la información#
        if input("¿Guardar antes de salir? (S/N): ").upper() == "S": self.transformador.guardar(self.clientes, self.turnos)
        print("Saliendo..."); sys.exit() 

# --- EJECUCIÓN PRINCIPAL DEL PROGRAMA ---
# Este bloque garantiza que el programa solo se ejecute si se inicia directamente este archivo.
if __name__ == "__main__":
    GestorTurnos().iniciar()
    