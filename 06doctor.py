import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from datetime import datetime
import sys

# Código de consola simplificado (5 líneas)
if len(sys.argv) > 1 and sys.argv[1] == "--cli":
    print("Sistema de Autodiagnóstico Médico")
    nombre = input("Nombre: ")
    print(f"Paciente: {nombre}")
    print("Diagnóstico: Consulte a un médico profesional")
    sys.exit(0)

class DoctorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MED-TECH SYSTEM v2.0")
        self.root.geometry("1050x800")
        self.root.configure(bg="#0a0a0f")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores neón tecnológicos
        bg_color = "#0a0a0f"
        fg_color = "#00ffff"
        accent_color = "#ff00ff"
        secondary_color = "#1a1a2e"
        tertiary_color = "#0d0d15"
        neon_green = "#00ff00"
        neon_blue = "#00ffff"
        neon_pink = "#ff00ff"
        neon_yellow = "#ffff00"
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=neon_blue, font=('Consolas', 10))
        style.configure('TButton', font=('Consolas', 11, 'bold'), background=neon_pink, foreground=bg_color)
        style.configure('Header.TLabel', font=('Consolas', 18, 'bold'), background=tertiary_color, foreground=neon_yellow)
        style.configure('Subheader.TLabel', font=('Consolas', 12, 'bold'), background=secondary_color, foreground=neon_green)
        
        style.map('TButton', background=[('active', neon_green)], foreground=[('active', bg_color)])
        
        self.numero_reporte = random.randint(1000, 9999)
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=secondary_color, foreground=neon_blue, 
                       padding=[25, 12], font=('Consolas', 11, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', neon_pink)], 
                 foreground=[('selected', bg_color)])
        
        self.crear_pestana_info()
        self.crear_pestana_sintomas()
        self.crear_pestana_resultados()
    
    def crear_pestana_info(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ DATOS")
        
        main_frame = tk.Frame(tab, bg="#0a0a0f")
        main_frame.pack(fill='both', expand=True)
        
        # Header con efecto neón
        header_frame = tk.Frame(main_frame, bg="#0d0d15", height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="╔══════════════════════════════════════════════════════╗", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        tk.Label(header_frame, text="║  MED-TECH SYSTEM v2.0 - MÓDULO DE INGRESO  ║", 
                bg="#0d0d15", fg="#ff00ff", font=('Consolas', 14, 'bold')).pack()
        tk.Label(header_frame, text="╚══════════════════════════════════════════════════════╝", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        
        content_frame = tk.Frame(main_frame, bg="#0a0a0f")
        content_frame.pack(fill='both', expand=True, padx=50, pady=40)
        
        self.crear_campo_neon(content_frame, "► NOMBRE DEL PACIENTE:", 0)
        self.crear_campo_neon(content_frame, "► EDAD:", 1, width=15)
        self.crear_campo_neon(content_frame, "► DIRECCIÓN:", 2)
        
        btn_frame = tk.Frame(content_frame, bg="#0a0a0f")
        btn_frame.pack(fill='x', pady=40)
        
        btn = tk.Button(btn_frame, text="▶ INICIAR ANÁLISIS ◀", 
                      bg="#ff00ff", fg="#0a0a0f", font=('Consolas', 14, 'bold'),
                      relief='flat', padx=40, pady=15, cursor='hand2',
                      command=lambda: self.notebook.select(1))
        btn.pack()
        
        btn.bind('<Enter>', lambda e: btn.configure(bg='#00ff00'))
        btn.bind('<Leave>', lambda e: btn.configure(bg='#ff00ff'))
    
    def crear_campo_neon(self, parent, label_text, row, width=40):
        frame = tk.Frame(parent, bg="#1a1a2e", pady=15, padx=20)
        frame.pack(fill='x', pady=12)
        
        tk.Label(frame, text=label_text, bg="#1a1a2e", fg="#00ffff", 
                font=('Consolas', 11, 'bold')).pack(anchor='w', padx=10, pady=(8, 5))
        
        entry = tk.Entry(frame, bg="#0d0d15", fg="#00ff00", 
                       font=('Consolas', 12), relief='flat', insertbackground="#ff00ff",
                       bd=2, highlightbackground="#ff00ff", highlightcolor="#ff00ff")
        entry.pack(fill='x', padx=10, pady=(5, 10))
        
        if label_text == "► NOMBRE DEL PACIENTE:":
            self.nombre = entry
        elif label_text == "► EDAD:":
            self.edad = entry
        elif label_text == "► DIRECCIÓN:":
            self.direccion = entry
    
    def crear_pestana_sintomas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ SÍNTOMAS")
        
        main_frame = tk.Frame(tab, bg="#0a0a0f")
        main_frame.pack(fill='both', expand=True)
        
        header_frame = tk.Frame(main_frame, bg="#0d0d15", height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="╔══════════════════════════════════════════════════════╗", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        tk.Label(header_frame, text="║  MÓDULO DE ANÁLISIS DE SÍNTOMAS  ║", 
                bg="#0d0d15", fg="#ff00ff", font=('Consolas', 14, 'bold')).pack()
        tk.Label(header_frame, text="╚══════════════════════════════════════════════════════╝", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        
        content_frame = tk.Frame(main_frame, bg="#0a0a0f")
        content_frame.pack(fill='both', expand=True, padx=50, pady=40)
        
        self.fiebre_var = tk.BooleanVar(value=False)
        self.tos_var = tk.BooleanVar(value=False)
        self.dolor_garganta_var = tk.BooleanVar(value=False)
        self.dificultad_respirar_var = tk.BooleanVar(value=False)
        self.dolor_cabeza_var = tk.BooleanVar(value=False)
        self.fatiga_var = tk.BooleanVar(value=False)
        self.problema_digestivo_var = tk.BooleanVar(value=False)
        self.alergia_var = tk.BooleanVar(value=False)
        
        sintomas = [
            ("[⚡] FIEBRE", self.fiebre_var),
            ("[⚡] TOS", self.tos_var),
            ("[⚡] DOLOR DE GARGANTA", self.dolor_garganta_var),
            ("[⚡] DIFICULTAD RESPIRATORIA", self.dificultad_respirar_var),
            ("[⚡] DOLOR DE CABEZA", self.dolor_cabeza_var),
            ("[⚡] FATIGA EXTREMA", self.fatiga_var),
            ("[⚡] PROBLEMAS DIGESTIVOS", self.problema_digestivo_var),
            ("[⚡] ALERGIA", self.alergia_var)
        ]
        
        col1_frame = tk.Frame(content_frame, bg="#0a0a0f")
        col1_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        col2_frame = tk.Frame(content_frame, bg="#0a0a0f")
        col2_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        for i, (texto, var) in enumerate(sintomas):
            if i < 4:
                self.crear_checkbox_neon(col1_frame, texto, var)
            else:
                self.crear_checkbox_neon(col2_frame, texto, var)
        
        btn_frame = tk.Frame(content_frame, bg="#0a0a0f")
        btn_frame.pack(fill='x', pady=40)
        
        btn = tk.Button(btn_frame, text="▶ EJECUTAR DIAGNÓSTICO ◀", 
                      bg="#ff00ff", fg="#0a0a0f", font=('Consolas', 14, 'bold'),
                      relief='flat', padx=40, pady=15, cursor='hand2',
                      command=self.generar_diagnostico)
        btn.pack()
        
        btn.bind('<Enter>', lambda e: btn.configure(bg='#00ff00'))
        btn.bind('<Leave>', lambda e: btn.configure(bg='#ff00ff'))
    
    def crear_checkbox_neon(self, parent, texto, var):
        frame = tk.Frame(parent, bg="#1a1a2e", pady=15, padx=20)
        frame.pack(fill='x', pady=12)
        
        cb = tk.Checkbutton(frame, text=texto, variable=var, 
                           bg="#1a1a2e", fg="#00ffff", 
                           font=('Consolas', 12, 'bold'),
                           selectcolor="#ff00ff", activebackground="#1a1a2e",
                           activeforeground="#00ff00", cursor='hand2',
                           relief='flat', bd=0)
        cb.pack(anchor='w')
    
    def crear_pestana_resultados(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ RESULTADOS")
        
        main_frame = tk.Frame(tab, bg="#0a0a0f")
        main_frame.pack(fill='both', expand=True)
        
        header_frame = tk.Frame(main_frame, bg="#0d0d15", height=100)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="╔══════════════════════════════════════════════════════╗", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        tk.Label(header_frame, text="║  MÓDULO DE RESULTADOS DE DIAGNÓSTICO  ║", 
                bg="#0d0d15", fg="#ff00ff", font=('Consolas', 14, 'bold')).pack()
        tk.Label(header_frame, text="╚══════════════════════════════════════════════════════╝", 
                bg="#0d0d15", fg="#00ffff", font=('Consolas', 12, 'bold')).pack()
        
        content_frame = tk.Frame(main_frame, bg="#0a0a0f")
        content_frame.pack(fill='both', expand=True, padx=50, pady=40)
        
        text_frame = tk.Frame(content_frame, bg="#1a1a2e", pady=20, padx=20)
        text_frame.pack(fill='both', expand=True)
        
        self.result_text = scrolledtext.ScrolledText(text_frame, height=22, width=100, 
                                                     font=('Consolas', 11), bg="#0d0d15", 
                                                     fg="#00ff00", relief='flat', bd=0)
        self.result_text.pack(fill='both', expand=True)
        
        btn_frame = tk.Frame(content_frame, bg="#0a0a0f")
        btn_frame.pack(fill='x', pady=30)
        
        btn_nuevo = tk.Button(btn_frame, text="⚡ NUEVO ANÁLISIS ⚡", 
                            bg="#ff00ff", fg="#0a0a0f", font=('Consolas', 12, 'bold'),
                            relief='flat', padx=30, pady=12, cursor='hand2',
                            command=self.nuevo_diagnostico)
        btn_nuevo.pack(side='left', padx=10)
        
        btn_nuevo.bind('<Enter>', lambda e: btn_nuevo.configure(bg='#00ff00'))
        btn_nuevo.bind('<Leave>', lambda e: btn_nuevo.configure(bg='#ff00ff'))
    
    def generar_diagnostico(self):
        try:
            nombre = self.nombre.get()
            edad = int(self.edad.get()) if self.edad.get() else 0
            direccion = self.direccion.get()
            
            if edad < 13:
                rango_edad = "NIÑO (0-12 AÑOS)"
            elif edad < 18:
                rango_edad = "ADOLESCENTE (13-17 AÑOS)"
            elif edad < 30:
                rango_edad = "ADULTO JOVEN (18-29 AÑOS)"
            elif edad < 50:
                rango_edad = "ADULTO (30-49 AÑOS)"
            elif edad < 65:
                rango_edad = "ADULTO MAYOR (50-64 AÑOS)"
            else:
                rango_edad = "ADULTO MAYOR AVANZADO (65+ AÑOS)"
            
            tiene_fiebre = self.fiebre_var.get()
            tiene_tos = self.tos_var.get()
            tiene_dolor_garganta = self.dolor_garganta_var.get()
            tiene_dificultad_respirar = self.dificultad_respirar_var.get()
            tiene_dolor_cabeza = self.dolor_cabeza_var.get()
            tiene_fatiga = self.fatiga_var.get()
            tiene_problema_digestivo = self.problema_digestivo_var.get()
            tiene_alergia = self.alergia_var.get()
            
            diagnosticos = []
            
            if tiene_dificultad_respirar:
                diagnosticos.append("⚠️ PROBLEMA RESPIRATORIO")
            
            if tiene_fiebre and tiene_tos and tiene_dolor_cabeza and tiene_fatiga:
                diagnosticos.append("🦠 POSIBLE COVID-19")
            elif tiene_fiebre and tiene_tos:
                diagnosticos.append("🦠 INFECCIÓN RESPIRATORIA")
            
            if tiene_tos and tiene_dolor_garganta:
                diagnosticos.append("🦠 IRRITACIÓN RESPIRATORIA")
            
            if tiene_fiebre and tiene_dolor_cabeza:
                diagnosticos.append("🦠 POSIBLE GRIPE")
            
            if tiene_alergia:
                diagnosticos.append("🌸 ALERGIA")
            
            if tiene_problema_digestivo:
                diagnosticos.append("🤢 PROBLEMA DIGESTIVO")
            
            if tiene_dolor_cabeza and not (tiene_fiebre or tiene_fatiga):
                diagnosticos.append("🤕 DOLOR DE CABEZA")
            
            if tiene_fiebre and not (tiene_tos or tiene_dolor_cabeza):
                diagnosticos.append("🌡️ FIEBRE SIN CAUSA APARENTE")
            
            if tiene_fatiga and not (tiene_fiebre and tiene_tos and tiene_dolor_cabeza):
                diagnosticos.append("😴 FATIGA GENERAL")
            
            # Diseño tecnológico del reporte
            reporte = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    MED-TECH SYSTEM v2.0 - REPORTE DE DIAGNÓSTICO                ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│  DATOS DEL PACIENTE                                                          │
└──────────────────────────────────────────────────────────────────────────────┘

  ► NOMBRE: {nombre.upper()}
  ► EDAD: {edad} AÑOS ({rango_edad})
  ► DIRECCIÓN: {direccion.upper()}
  ► REPORTE #: {self.numero_reporte}
  ► FECHA/HORA: {self.fecha_hora}

┌──────────────────────────────────────────────────────────────────────────────┐
│  ANÁLISIS DE SÍNTOMAS DETECTADOS                                             │
└──────────────────────────────────────────────────────────────────────────────┘

"""

            if diagnosticos:
                for diag in diagnosticos:
                    reporte += f"  ✗ {diag}\n"
            else:
                reporte += "  ✓ NO SE DETECTARON PATRONES DE ENFERMEDAD SIGNIFICATIVOS\n"
            
            reporte += f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  RECOMENDACIONES DEL SISTEMA                                                │
└──────────────────────────────────────────────────────────────────────────────┘

  ⚡ CONSULTA A UN MÉDICO PROFESIONAL PARA DIAGNÓSTICO DEFINITIVO
  ⚡ SI TIENES SÍNTOMAS DE EMERGENCIA, BUSCA ATENCIÓN MÉDICA INMEDIATA
  ⚡ MANTÉN UN REGISTRO DETALLADO DE TUS SÍNTOMAS
  ⚡ SIGUE UN ESTILO DE VIDA SALUDABLE Y EQUILIBRADO
  ⚡ REALIZA CHEQUEOS MÉDICOS REGULARES

┌──────────────────────────────────────────────────────────────────────────────┐
│  AVISO LEGAL DEL SISTEMA                                                     │
└──────────────────────────────────────────────────────────────────────────────┘

  ⚠️ ESTE SISTEMA ES SOLO ORIENTATIVO Y NO SUSTITUYE
  ⚠️ LA OPINIÓN DE UN PROFESIONAL MÉDICO CUALIFICADO.
  ⚠️ SI LOS SÍNTOMAS PERSISTEN O EMPEORAN, CONSULTA A UN MÉDICO.

╔════════════════════════════════════════════════════════════════════════════╗
║  REPORTE #{self.numero_reporte} - PROCESADO POR MED-TECH SYSTEM v2.0         ║
║  GRACIAS POR UTILIZAR NUESTRO SISTEMA DE DIAGNÓSTICO MÉDICO                  ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, reporte)
            self.notebook.select(2)
            
        except ValueError:
            messagebox.showerror("ERROR", "POR FAVOR INGRESE VALORES VÁLIDOS")
    
    def nuevo_diagnostico(self):
        self.nombre.delete(0, 'end')
        self.edad.delete(0, 'end')
        self.direccion.delete(0, 'end')
        self.fiebre_var.set(False)
        self.tos_var.set(False)
        self.dolor_garganta_var.set(False)
        self.dificultad_respirar_var.set(False)
        self.dolor_cabeza_var.set(False)
        self.fatiga_var.set(False)
        self.problema_digestivo_var.set(False)
        self.alergia_var.set(False)
        self.result_text.delete(1.0, tk.END)
        self.numero_reporte = random.randint(1000, 9999)
        self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.notebook.select(0)

# Ejecutar GUI por defecto
root = tk.Tk()
app = DoctorGUI(root)
root.mainloop()
