import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def evaluar_consola():
    print("=" * 55)
    print("       SISTEMA DE AUTORIZACIÓN PARA EXAMEN")
    print("=" * 55)

    asistencia = float(input("Ingresa el porcentaje de asistencia: "))
    promedio = float(input("Ingresa el promedio: "))
    proyecto = input("¿Entregó el proyecto? (si/no): ").lower()
    autorizacion = input("¿Tiene autorización especial? (si/no): ").lower()
    adeudos = input("¿Tiene adeudos? (si/no): ").lower()
    lista_oficial = input("¿Aparece en la lista oficial? (si/no): ").lower()

    P = asistencia >= 80
    Q = promedio >= 7
    R = proyecto == "si"
    S = autorizacion == "si"
    T = adeudos == "no"
    U = lista_oficial == "si"

    print("\n" + "=" * 55)
    print("             VALORES DE LAS PROPOSICIONES")
    print("=" * 55)

    print("P - Asistencia suficiente:", P)
    print("Q - Promedio aprobatorio:", Q)
    print("R - Proyecto entregado:", R)
    print("S - Autorización especial:", S)
    print("T - Sin adeudos:", T)
    print("U - En lista oficial:", U)

    negacion_P = not P

    print("\nNEGACIÓN")
    print("¬P =", negacion_P)

    conjuncion = P and Q

    print("\nCONJUNCIÓN")
    print("P ∧ Q =", conjuncion)

    disyuncion = Q or S

    print("\nDISYUNCIÓN")
    print("Q ∨ S =", disyuncion)

    condicional = (not P) or Q

    print("\nCONDICIONAL")
    print("P → Q =", condicional)

    bicondicional = P == Q

    print("\nBICONDICIONAL")
    print("P ↔ Q =", bicondicional)

    expresion = U and ((P and Q and T) or S)

    print("\nEXPRESIÓN CON PARÉNTESIS")
    print("U ∧ ((P ∧ Q ∧ T) ∨ S) =", expresion)

    print("\n" + "=" * 55)
    print("                RESULTADO FINAL")
    print("=" * 55)

    if expresion:
        print("El alumno PUEDE presentar el examen.")
    else:
        print("El alumno NO puede presentar el examen.")

class AutorizacionExamenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Autorización para Examen")
        self.root.geometry("600x650")
        self.root.configure(bg="#f0f0f0")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TFrame', background="#f0f0f0")
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background="#2c3e50", foreground="white")
        
        header_frame = ttk.Frame(root)
        header_frame.pack(fill='x', pady=10)
        header_label = ttk.Label(header_frame, text="SISTEMA DE AUTORIZACIÓN PARA EXAMEN", style='Header.TLabel')
        header_label.pack(fill='x', padx=10, pady=10)
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Porcentaje de Asistencia:").grid(row=0, column=0, sticky='w', pady=5)
        self.asistencia = ttk.Entry(main_frame, width=20)
        self.asistencia.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Promedio:").grid(row=1, column=0, sticky='w', pady=5)
        self.promedio = ttk.Entry(main_frame, width=20)
        self.promedio.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="¿Entregó el Proyecto?:").grid(row=2, column=0, sticky='w', pady=5)
        self.proyecto_var = tk.StringVar(value="no")
        proyecto_frame = ttk.Frame(main_frame)
        proyecto_frame.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        ttk.Radiobutton(proyecto_frame, text="Sí", variable=self.proyecto_var, value="si").pack(side='left', padx=5)
        ttk.Radiobutton(proyecto_frame, text="No", variable=self.proyecto_var, value="no").pack(side='left', padx=5)
        
        ttk.Label(main_frame, text="¿Autorización Especial?:").grid(row=3, column=0, sticky='w', pady=5)
        self.autorizacion_var = tk.StringVar(value="no")
        autorizacion_frame = ttk.Frame(main_frame)
        autorizacion_frame.grid(row=3, column=1, sticky='w', pady=5, padx=5)
        ttk.Radiobutton(autorizacion_frame, text="Sí", variable=self.autorizacion_var, value="si").pack(side='left', padx=5)
        ttk.Radiobutton(autorizacion_frame, text="No", variable=self.autorizacion_var, value="no").pack(side='left', padx=5)
        
        ttk.Label(main_frame, text="¿Tiene Adeudos?:").grid(row=4, column=0, sticky='w', pady=5)
        self.adeudos_var = tk.StringVar(value="no")
        adeudos_frame = ttk.Frame(main_frame)
        adeudos_frame.grid(row=4, column=1, sticky='w', pady=5, padx=5)
        ttk.Radiobutton(adeudos_frame, text="Sí", variable=self.adeudos_var, value="si").pack(side='left', padx=5)
        ttk.Radiobutton(adeudos_frame, text="No", variable=self.adeudos_var, value="no").pack(side='left', padx=5)
        
        ttk.Label(main_frame, text="¿En Lista Oficial?:").grid(row=5, column=0, sticky='w', pady=5)
        self.lista_var = tk.StringVar(value="no")
        lista_frame = ttk.Frame(main_frame)
        lista_frame.grid(row=5, column=1, sticky='w', pady=5, padx=5)
        ttk.Radiobutton(lista_frame, text="Sí", variable=self.lista_var, value="si").pack(side='left', padx=5)
        ttk.Radiobutton(lista_frame, text="No", variable=self.lista_var, value="no").pack(side='left', padx=5)
        
        evaluar_btn = ttk.Button(main_frame, text="Evaluar", command=self.evaluar)
        evaluar_btn.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.result_frame = ttk.LabelFrame(root, text="Resultados", padding="10")
        self.result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=15, width=70, font=('Courier New', 10))
        self.result_text.pack(fill='both', expand=True)
        
        limpiar_btn = ttk.Button(root, text="Limpiar", command=self.limpiar)
        limpiar_btn.pack(pady=10)
    
    def evaluar(self):
        try:
            asistencia = float(self.asistencia.get())
            promedio = float(self.promedio.get())
            proyecto = self.proyecto_var.get()
            autorizacion = self.autorizacion_var.get()
            adeudos = self.adeudos_var.get()
            lista_oficial = self.lista_var.get()
            
            P = asistencia >= 80
            Q = promedio >= 7
            R = proyecto == "si"
            S = autorizacion == "si"
            T = adeudos == "no"
            U = lista_oficial == "si"
            
            negacion_P = not P
            conjuncion = P and Q
            disyuncion = Q or S
            condicional = (not P) or Q
            bicondicional = P == Q
            expresion = U and ((P and Q and T) or S)
            
            resultado_text = f"""VALORES DE LAS PROPOSICIONES
{'='*50}
P - Asistencia suficiente: {P}
Q - Promedio aprobatorio: {Q}
R - Proyecto entregado: {R}
S - Autorización especial: {S}
T - Sin adeudos: {T}
U - En lista oficial: {U}

NEGACIÓN
¬P = {negacion_P}

CONJUNCIÓN
P ∧ Q = {conjuncion}

DISYUNCIÓN
Q ∨ S = {disyuncion}

CONDICIONAL
P → Q = {condicional}

BICONDICIONAL
P ↔ Q = {bicondicional}

EXPRESIÓN CON PARÉNTESIS
U ∧ ((P ∧ Q ∧ T) ∨ S) = {expresion}

RESULTADO FINAL
{'='*50}
{'El alumno PUEDE presentar el examen.' if expresion else 'El alumno NO puede presentar el examen.'}
"""
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, resultado_text)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para asistencia y promedio.")
    
    def limpiar(self):
        self.asistencia.delete(0, 'end')
        self.promedio.delete(0, 'end')
        self.proyecto_var.set("no")
        self.autorizacion_var.set("no")
        self.adeudos_var.set("no")
        self.lista_var.set("no")
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        evaluar_consola()
    else:
        root = tk.Tk()
        app = AutorizacionExamenGUI(root)
        root.mainloop()