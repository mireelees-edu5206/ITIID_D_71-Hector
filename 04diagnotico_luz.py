import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from datetime import datetime

def mostrar_soluciones_equipo_consola(equipo, problema):
    print(f"\n{'=' * 55}")
    print(f"POSSIBLES SOLUCIONES PARA {problema.upper()} EN {equipo.upper()}")
    print('=' * 55)
    
    if problema == "Electricidad":
        if equipo == "PC":
            print("1. Verifica que la fuente de poder de la PC esté conectada")
            print("2. Revisa el interruptor trasero de la fuente de poder")
            print("3. Prueba el cable de corriente en otro dispositivo")
        elif equipo == "Laptop":
            print("1. Verifica que el cargador esté bien conectado")
            print("2. Prueba con otro cargador compatible")
            print("3. Revisa si la batería tiene carga")
        elif equipo == "Servidor":
            print("1. Verifica que el UPS esté funcionando")
            print("2. Revisa las conexiones de redundancia de energía")
            print("3. Verifica los indicadores de energía del servidor")
        elif equipo == "Tablet":
            print("1. Verifica que el cable USB esté bien conectado")
            print("2. Prueba con otro cargador o puerto USB")
            print("3. Revisa si la batería está completamente agotada")
    
    elif problema == "Encendido":
        if equipo == "PC":
            print("1. Presiona el botón de encendido del case frontal")
            print("2. Verifica si el ventilador de la fuente gira")
            print("3. Revisa las conexiones del botón de encendido a la motherboard")
        elif equipo == "Laptop":
            print("1. Mantén presionado el botón de encendido por 10 segundos")
            print("2. Conecta el cargador y espera 5 minutos antes de encender")
            print("3. Revisa si hay luces LED indicadoras de carga")
        elif equipo == "Servidor":
            print("1. Verifica los indicadores LED del panel frontal")
            print("2. Revisa si hay códigos de error en el display")
            print("3. Verifica que todos los módulos de memoria estén bien instalados")
        elif equipo == "Tablet":
            print("1. Mantén presionados botón de encendido + volumen abajo por 10 segundos")
            print("2. Conecta a carga y deja cargar por 15 minutos")
            print("3. Intenta un reinicio forzado mediante combinación de botones")
    
    elif problema == "Imagen":
        if equipo == "PC":
            print("1. Verifica que el monitor esté encendido y con señal")
            print("2. Revisa que el cable VGA/HDMI esté bien conectado en ambos extremos")
            print("3. Verifica que la tarjeta gráfica esté bien instalada")
        elif equipo == "Laptop":
            print("1. Prueba la combinación de teclas para cambiar pantalla externa")
            print("2. Conecta un monitor externo para descartar pantalla dañada")
            print("3. Revisa si el brillo no está al mínimo")
        elif equipo == "Servidor":
            print("1. Verifica que el monitor KVM esté seleccionado en el servidor correcto")
            print("2. Revisa los cables del sistema KVM")
            print("3. Verifica la configuración de IPMI para acceso remoto")
        elif equipo == "Tablet":
            print("1. Aumenta el brillo desde el centro de control")
            print("2. Prueba reiniciar el dispositivo")
            print("3. Verifica si hay daño físico en la pantalla")
    
    elif problema == "Sonido":
        if equipo == "PC":
            print("1. Verifica que los altavoces estén conectados al puerto verde (audio out)")
            print("2. Si no tienes altavoces, usa audífonos o conecta altavoces de laptop")
            print("3. Revisa que el volumen de Windows no esté en mute")
            print("4. Verifica en Configuración > Sonido que el dispositivo de salida sea correcto")
        elif equipo == "Laptop":
            print("1. Verifica que el volumen no esté en mute")
            print("2. Presiona Fn + tecla de sonido para aumentar volumen")
            print("3. Si no hay sonido interno, conecta audífonos o altavoces externos")
            print("4. Revisa los controladores de audio en Administrador de dispositivos")
        elif equipo == "Servidor":
            print("1. Los servidores generalmente no tienen audio - verifica si es necesario")
            print("2. Si requieres audio, instala tarjeta de sonido dedicada")
            print("3. Verifica que el sistema operativo tenga soporte de audio")
        elif equipo == "Tablet":
            print("1. Verifica que el volumen no esté en mute")
            print("2. Limpia los altavoces con aire comprimido si están obstruidos")
            print("3. Prueba con audífonos Bluetooth o cableados")
            print("4. Reinicia el tablet para restablecer el audio")
    
    elif problema == "Internet":
        if equipo == "PC":
            print("1. Verifica que el cable Ethernet esté bien conectado")
            print("2. Reinicia el router y módem")
            print("3. Verifica la configuración de red en Windows")
        elif equipo == "Laptop":
            print("1. Verifica que el WiFi esté activado (Fn + tecla de WiFi)")
            print("2. Conecta a otra red WiFi para descartar problema de red")
            print("3. Si es posible, usa cable Ethernet para diagnóstico")
        elif equipo == "Servidor":
            print("1. Verifica que los cables de red estén conectados a puertos correctos")
            print("2. Verifica la configuración IP estática o DHCP")
            print("3. Revisa los logs de red para identificar problemas de conectividad")
        elif equipo == "Tablet":
            print("1. Activa y desactiva el modo avión")
            print("2. Olvida la red WiFi y vuelve a conectarla")
            print("3. Verifica que no esté en modo datos móviles si necesitas WiFi")

def diagnostico_consola():
    print("=" * 55)
    print("       SISTEMA DE AUTODIAGNÓSTICO DE EQUIPO")
    print("=" * 55)
    print("\n¡Bienvenido al Sistema de Autodiagnóstico!")
    print("Por favor, proporcione la siguiente información:\n")

    nombre = input("Nombre completo: ")
    direccion = input("Dirección: ")

    print("\n¿Qué tipo de equipos tiene?")
    print("1. PC")
    print("2. Laptop")
    print("3. Servidor")
    print("4. Tablet")

    equipos_disponibles = []
    respuesta = input("¿Tiene PC? (si/no): ").lower()
    if respuesta == "si":
        equipos_disponibles.append("PC")

    respuesta = input("¿Tiene Laptop? (si/no): ").lower()
    if respuesta == "si":
        equipos_disponibles.append("Laptop")

    respuesta = input("¿Tiene Servidor? (si/no): ").lower()
    if respuesta == "si":
        equipos_disponibles.append("Servidor")

    respuesta = input("¿Tiene Tablet? (si/no): ").lower()
    if respuesta == "si":
        equipos_disponibles.append("Tablet")

    if not equipos_disponibles:
        print("\nNo se detectaron equipos disponibles. No se puede realizar el diagnóstico.")
        return

    print("\nEquipos disponibles:", ", ".join(equipos_disponibles))
    equipo_seleccionado = input("¿A cuál equipo le desea hacer el diagnóstico? ").capitalize()

    equipos_normalizados = [equipo.upper() for equipo in equipos_disponibles]
    if equipo_seleccionado.upper() not in equipos_normalizados:
        print(f"\nEl equipo '{equipo_seleccionado}' no está en su lista de equipos disponibles.")
        return

    i = 0
    while i < len(equipos_disponibles):
        if equipos_disponibles[i].upper() == equipo_seleccionado.upper():
            equipo_seleccionado = equipos_disponibles[i]
            break
        i += 1

    numero_reporte = random.randint(1000, 9999)
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n" + "=" * 55)
    print("              REPORTE DE DIAGNÓSTICO")
    print("=" * 55)
    print(f"Cliente: {nombre}")
    print(f"Dirección: {direccion}")
    print(f"Equipo a diagnosticar: {equipo_seleccionado}")
    print(f"Número de reporte: #{numero_reporte}")
    print(f"Fecha y hora: {fecha_hora}")
    print("=" * 55)

    print("\nSi tienes duda, escribe 'ayuda' para obtener instrucciones")

    problemas_detectados = []

    respuesta = input("¿Tiene electricidad? (si/no): ").lower()
    if respuesta == "ayuda":
        print("Verifica si hay luz en casa y si el equipo está conectado")
        respuesta = input("¿Tiene electricidad? (si/no): ").lower()
    P = respuesta == "si"
    if not P:
        problemas_detectados.append("Electricidad")
        mostrar_soluciones_equipo_consola(equipo_seleccionado, "Electricidad")

    respuesta = input("¿Enciende? (si/no): ").lower()
    if respuesta == "ayuda":
        print("Presiona el botón de encendido y verifica si hay luces o sonido")
        respuesta = input("¿Enciende? (si/no): ").lower()
    Q = respuesta == "si"
    if not Q:
        problemas_detectados.append("Encendido")
        mostrar_soluciones_equipo_consola(equipo_seleccionado, "Encendido")

    respuesta = input("¿El monitor muestra imagen? (si/no): ").lower()
    if respuesta == "ayuda":
        print("Verifica si el monitor está encendido y conectado correctamente")
        respuesta = input("¿El monitor muestra imagen? (si/no): ").lower()
    R = respuesta == "si"
    if not R:
        problemas_detectados.append("Imagen")
        mostrar_soluciones_equipo_consola(equipo_seleccionado, "Imagen")

    respuesta = input("¿Hay sonido? (si/no): ").lower()
    if respuesta == "ayuda":
        print("Verifica si los altavoces estén conectados y el volumen no esté en mute")
        respuesta = input("¿Hay sonido? (si/no): ").lower()
    S = respuesta == "si"
    if not S:
        problemas_detectados.append("Sonido")
        mostrar_soluciones_equipo_consola(equipo_seleccionado, "Sonido")

    respuesta = input("¿Conecta a internet? (si/no): ").lower()
    if respuesta == "ayuda":
        print("Verifica si el cable de red está conectado o si el WiFi está activo")
        respuesta = input("¿Conecta a internet? (si/no): ").lower()
    T = respuesta == "si"
    if not T:
        problemas_detectados.append("Internet")
        mostrar_soluciones_equipo_consola(equipo_seleccionado, "Internet")

    resultado = P and Q and R and S and T

    print("\n" + "=" * 55)
    print("              RESULTADO DEL DIAGNÓSTICO")
    print("=" * 55)

    if problemas_detectados:
        print(f"Problemas detectados: {', '.join(problemas_detectados)}")
        print(f"\nHas recibido soluciones específicas para cada problema detectado.")
        print(f"Si después de aplicar las soluciones el problema persiste,")
        print(f"considera contactar soporte técnico especializado.")
    else:
        print("Diagnostico: El equipo funciona correctamente y sin problemas detectados")

    print(f"\nReporte #{numero_reporte} finalizado.")
    print("Gracias por usar nuestro sistema de diagnóstico.")

class DiagnosticoEquipoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Autodiagnóstico de Equipo")
        self.root.geometry("700x750")
        self.root.configure(bg="#f0f0f0")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TFrame', background="#f0f0f0")
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background="#2c3e50", foreground="white")
        
        self.equipos_disponibles = []
        self.equipo_seleccionado = None
        self.numero_reporte = random.randint(1000, 9999)
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_info = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_info, text="Información")
        self.crear_tab_info()
        
        self.tab_equipo = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_equipo, text="Equipo")
        self.crear_tab_equipo()
        
        self.tab_diagnostico = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diagnostico, text="Diagnóstico")
        self.crear_tab_diagnostico()
        
        self.tab_resultados = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_resultados, text="Resultados")
        self.crear_tab_resultados()
    
    def crear_tab_info(self):
        frame = ttk.Frame(self.tab_info, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Nombre Completo:").grid(row=0, column=0, sticky='w', pady=5)
        self.nombre = ttk.Entry(frame, width=40)
        self.nombre.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Dirección:").grid(row=1, column=0, sticky='w', pady=5)
        self.direccion = ttk.Entry(frame, width=40)
        self.direccion.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Button(frame, text="Siguiente →", command=self.ir_a_equipo).grid(row=2, column=0, columnspan=2, pady=20)
    
    def crear_tab_equipo(self):
        frame = ttk.Frame(self.tab_equipo, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text="Seleccione los equipos disponibles:", font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.pc_var = tk.BooleanVar()
        self.laptop_var = tk.BooleanVar()
        self.servidor_var = tk.BooleanVar()
        self.tablet_var = tk.BooleanVar()
        
        ttk.Checkbutton(frame, text="PC", variable=self.pc_var).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Laptop", variable=self.laptop_var).grid(row=1, column=1, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Servidor", variable=self.servidor_var).grid(row=2, column=0, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Tablet", variable=self.tablet_var).grid(row=2, column=1, sticky='w', pady=5)
        
        ttk.Button(frame, text="Siguiente →", command=self.ir_a_diagnostico).grid(row=3, column=0, columnspan=2, pady=20)
    
    def crear_tab_diagnostico(self):
        frame = ttk.Frame(self.tab_diagnostico, padding="20")
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text=f"Equipo seleccionado: {self.equipo_seleccionado if self.equipo_seleccionado else 'Ninguno'}", font=('Arial', 11, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.electricidad_var = tk.BooleanVar(value=True)
        self.encendido_var = tk.BooleanVar(value=True)
        self.imagen_var = tk.BooleanVar(value=True)
        self.sonido_var = tk.BooleanVar(value=True)
        self.internet_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(frame, text="Tiene electricidad", variable=self.electricidad_var).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Enciende", variable=self.encendido_var).grid(row=1, column=1, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="El monitor muestra imagen", variable=self.imagen_var).grid(row=2, column=0, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Hay sonido", variable=self.sonido_var).grid(row=2, column=1, sticky='w', pady=5)
        ttk.Checkbutton(frame, text="Conecta a internet", variable=self.internet_var).grid(row=3, column=0, sticky='w', pady=5)
        
        ttk.Button(frame, text="Diagnosticar", command=self.realizar_diagnostico).grid(row=4, column=0, columnspan=2, pady=20)
    
    def crear_tab_resultados(self):
        frame = ttk.Frame(self.tab_resultados, padding="20")
        frame.pack(fill='both', expand=True)
        
        self.result_text = scrolledtext.ScrolledText(frame, height=20, width=70, font=('Courier New', 9))
        self.result_text.pack(fill='both', expand=True)
        
        ttk.Button(frame, text="Nuevo Diagnóstico", command=self.nuevo_diagnostico).pack(pady=10)
    
    def ir_a_equipo(self):
        if not self.nombre.get() or not self.direccion.get():
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos.")
            return
        self.notebook.select(self.tab_equipo)
    
    def ir_a_diagnostico(self):
        self.equipos_disponibles = []
        if self.pc_var.get():
            self.equipos_disponibles.append("PC")
        if self.laptop_var.get():
            self.equipos_disponibles.append("Laptop")
        if self.servidor_var.get():
            self.equipos_disponibles.append("Servidor")
        if self.tablet_var.get():
            self.equipos_disponibles.append("Tablet")
        
        if not self.equipos_disponibles:
            messagebox.showwarning("Advertencia", "Seleccione al menos un equipo.")
            return
        
        self.equipo_seleccionado = self.equipos_disponibles[0]
        
        for widget in self.tab_diagnostico.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and "Equipo seleccionado" in child.cget('text'):
                        child.config(text=f"Equipo seleccionado: {self.equipo_seleccionado}")
        
        self.notebook.select(self.tab_diagnostico)
    
    def realizar_diagnostico(self):
        P = self.electricidad_var.get()
        Q = self.encendido_var.get()
        R = self.imagen_var.get()
        S = self.sonido_var.get()
        T = self.internet_var.get()
        
        problemas_detectados = []
        soluciones = []
        
        if not P:
            problemas_detectados.append("Electricidad")
            soluciones.append(self.obtener_soluciones("Electricidad"))
        if not Q:
            problemas_detectados.append("Encendido")
            soluciones.append(self.obtener_soluciones("Encendido"))
        if not R:
            problemas_detectados.append("Imagen")
            soluciones.append(self.obtener_soluciones("Imagen"))
        if not S:
            problemas_detectados.append("Sonido")
            soluciones.append(self.obtener_soluciones("Sonido"))
        if not T:
            problemas_detectados.append("Internet")
            soluciones.append(self.obtener_soluciones("Internet"))
        
        resultado_text = f"""{'='*55}
REPORTE DE DIAGNÓSTICO
{'='*55}
Cliente: {self.nombre.get()}
Dirección: {self.direccion.get()}
Equipo a diagnosticar: {self.equipo_seleccionado}
Número de reporte: #{self.numero_reporte}
Fecha y hora: {self.fecha_hora}
{'='*55}

RESULTADO DEL DIAGNÓSTICO
{'='*55}
"""
        
        if problemas_detectados:
            resultado_text += f"Problemas detectados: {', '.join(problemas_detectados)}\n\n"
            for i, problema in enumerate(problemas_detectados):
                resultado_text += f"\n{'='*55}\nSOLUCIONES PARA {problema.upper()}\n{'='*55}\n"
                resultado_text += soluciones[i]
        else:
            resultado_text += "Diagnóstico: El equipo funciona correctamente y sin problemas detectados.\n"
        
        resultado_text += f"\n{'='*55}\nReporte #{self.numero_reporte} finalizado.\nGracias por usar nuestro sistema de diagnóstico.\n"
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, resultado_text)
        self.notebook.select(self.tab_resultados)
    
    def obtener_soluciones(self, problema):
        equipo = self.equipo_seleccionado
        soluciones_dict = {
            "Electricidad": {
                "PC": "1. Verifica que la fuente de poder de la PC esté conectada\n2. Revisa el interruptor trasero de la fuente de poder\n3. Prueba el cable de corriente en otro dispositivo",
                "Laptop": "1. Verifica que el cargador esté bien conectado\n2. Prueba con otro cargador compatible\n3. Revisa si la batería tiene carga",
                "Servidor": "1. Verifica que el UPS esté funcionando\n2. Revisa las conexiones de redundancia de energía\n3. Verifica los indicadores de energía del servidor",
                "Tablet": "1. Verifica que el cable USB esté bien conectado\n2. Prueba con otro cargador o puerto USB\n3. Revisa si la batería está completamente agotada"
            },
            "Encendido": {
                "PC": "1. Presiona el botón de encendido del case frontal\n2. Verifica si el ventilador de la fuente gira\n3. Revisa las conexiones del botón de encendido a la motherboard",
                "Laptop": "1. Mantén presionado el botón de encendido por 10 segundos\n2. Conecta el cargador y espera 5 minutos antes de encender\n3. Revisa si hay luces LED indicadoras de carga",
                "Servidor": "1. Verifica los indicadores LED del panel frontal\n2. Revisa si hay códigos de error en el display\n3. Verifica que todos los módulos de memoria estén bien instalados",
                "Tablet": "1. Mantén presionados botón de encendido + volumen abajo por 10 segundos\n2. Conecta a carga y deja cargar por 15 minutos\n3. Intenta un reinicio forzado mediante combinación de botones"
            },
            "Imagen": {
                "PC": "1. Verifica que el monitor esté encendido y con señal\n2. Revisa que el cable VGA/HDMI esté bien conectado en ambos extremos\n3. Verifica que la tarjeta gráfica esté bien instalada",
                "Laptop": "1. Prueba la combinación de teclas para cambiar pantalla externa\n2. Conecta un monitor externo para descartar pantalla dañada\n3. Revisa si el brillo no está al mínimo",
                "Servidor": "1. Verifica que el monitor KVM esté seleccionado en el servidor correcto\n2. Revisa los cables del sistema KVM\n3. Verifica la configuración de IPMI para acceso remoto",
                "Tablet": "1. Aumenta el brillo desde el centro de control\n2. Prueba reiniciar el dispositivo\n3. Verifica si hay daño físico en la pantalla"
            },
            "Sonido": {
                "PC": "1. Verifica que los altavoces estén conectados al puerto verde (audio out)\n2. Si no tienes altavoces, usa audífonos o conecta altavoces de laptop\n3. Revisa que el volumen de Windows no esté en mute\n4. Verifica en Configuración > Sonido que el dispositivo de salida sea correcto",
                "Laptop": "1. Verifica que el volumen no esté en mute\n2. Presiona Fn + tecla de sonido para aumentar volumen\n3. Si no hay sonido interno, conecta audífonos o altavoces externos\n4. Revisa los controladores de audio en Administrador de dispositivos",
                "Servidor": "1. Los servidores generalmente no tienen audio - verifica si es necesario\n2. Si requieres audio, instala tarjeta de sonido dedicada\n3. Verifica que el sistema operativo tenga soporte de audio",
                "Tablet": "1. Verifica que el volumen no esté en mute\n2. Limpia los altavoces con aire comprimido si están obstruidos\n3. Prueba con audífonos Bluetooth o cableados\n4. Reinicia el tablet para restablecer el audio"
            },
            "Internet": {
                "PC": "1. Verifica que el cable Ethernet esté bien conectado\n2. Reinicia el router y módem\n3. Verifica la configuración de red en Windows",
                "Laptop": "1. Verifica que el WiFi esté activado (Fn + tecla de WiFi)\n2. Conecta a otra red WiFi para descartar problema de red\n3. Si es posible, usa cable Ethernet para diagnóstico",
                "Servidor": "1. Verifica que los cables de red estén conectados a puertos correctos\n2. Verifica la configuración IP estática o DHCP\n3. Revisa los logs de red para identificar problemas de conectividad",
                "Tablet": "1. Activa y desactiva el modo avión\n2. Olvida la red WiFi y vuelve a conectarla\n3. Verifica que no esté en modo datos móviles si necesitas WiFi"
            }
        }
        
        return soluciones_dict.get(problema, {}).get(equipo, "Soluciones no disponibles para este equipo.")
    
    def nuevo_diagnostico(self):
        self.nombre.delete(0, 'end')
        self.direccion.delete(0, 'end')
        self.pc_var.set(False)
        self.laptop_var.set(False)
        self.servidor_var.set(False)
        self.tablet_var.set(False)
        self.electricidad_var.set(True)
        self.encendido_var.set(True)
        self.imagen_var.set(True)
        self.sonido_var.set(True)
        self.internet_var.set(True)
        self.equipos_disponibles = []
        self.equipo_seleccionado = None
        self.numero_reporte = random.randint(1000, 9999)
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.result_text.delete(1.0, tk.END)
        self.notebook.select(self.tab_info)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        diagnostico_consola()
    else:
        root = tk.Tk()
        app = DiagnosticoEquipoGUI(root)
        root.mainloop()