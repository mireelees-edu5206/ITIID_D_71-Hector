import tkinter as tk
from tkinter import ttk, messagebox

def evaluar_consola():
    print("=" * 55)
    print("       EVALUACIÓN DE ALUMNO PARA EXAMEN")
    print("=" * 55)

    asistencia = float(input("Ingresa el porcentaje de asistencia: "))
    promedio = float(input("Ingresa el promedio del alumno: "))
    proyecto = input("¿Entregó el proyecto? (si/no): ").lower()

    P = asistencia >= 80
    Q = promedio >= 8
    R = proyecto == "si"

    print("\n" + "=" * 55)
    print("          EVALUACIÓN DE PROPOSICIONES")
    print("=" * 55)

    print("P - Asistencia suficiente:", P)
    print("Q - Promedio aprobatorio:", Q)
    print("R - Proyecto entregado:", R)

    resultado = P and Q and R

    print("\nCONJUNCIÓN")
    print("P ∧ Q ∧ R =", resultado)

    print("\n" + "=" * 55)
    print("              RESULTADO FINAL")
    print("=" * 55)

    if resultado:
        print("El alumno PUEDE presentar el examen final.")
    else:
        print("El alumno NO puede presentar el examen final.")

class EvaluacionAlumnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Evaluación de Alumno para Examen")
        self.root.geometry("500x450")
        self.root.configure(bg="#f0f0f0")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TFrame', background="#f0f0f0")
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background="#2c3e50", foreground="white")
        
        header_frame = ttk.Frame(root)
        header_frame.pack(fill='x', pady=10)
        header_label = ttk.Label(header_frame, text="EVALUACIÓN DE ALUMNO PARA EXAMEN", style='Header.TLabel')
        header_label.pack(fill='x', padx=10, pady=10)
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Porcentaje de Asistencia:").grid(row=0, column=0, sticky='w', pady=5)
        self.asistencia = ttk.Entry(main_frame, width=20)
        self.asistencia.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Promedio del Alumno:").grid(row=1, column=0, sticky='w', pady=5)
        self.promedio = ttk.Entry(main_frame, width=20)
        self.promedio.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="¿Entregó el Proyecto?:").grid(row=2, column=0, sticky='w', pady=5)
        self.proyecto_var = tk.StringVar(value="no")
        proyecto_frame = ttk.Frame(main_frame)
        proyecto_frame.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        ttk.Radiobutton(proyecto_frame, text="Sí", variable=self.proyecto_var, value="si").pack(side='left', padx=5)
        ttk.Radiobutton(proyecto_frame, text="No", variable=self.proyecto_var, value="no").pack(side='left', padx=5)
        
        evaluar_btn = ttk.Button(main_frame, text="Evaluar", command=self.evaluar)
        evaluar_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.result_frame = ttk.LabelFrame(root, text="Resultados", padding="10")
        self.result_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.result_label = ttk.Label(self.result_frame, text="", justify='left')
        self.result_label.pack(fill='both', expand=True)
        
        limpiar_btn = ttk.Button(root, text="Limpiar", command=self.limpiar)
        limpiar_btn.pack(pady=10)
    
    def evaluar(self):
        try:
            asistencia = float(self.asistencia.get())
            promedio = float(self.promedio.get())
            proyecto = self.proyecto_var.get()
            
            P = asistencia >= 80
            Q = promedio >= 8
            R = proyecto == "si"
            
            resultado = P and Q and R
            
            resultado_text = f"""
P - Asistencia suficiente: {P}
Q - Promedio aprobatorio: {Q}
R - Proyecto entregado: {R}

CONJUNCIÓN
P ∧ Q ∧ R = {resultado}

RESULTADO FINAL
{'El alumno PUEDE presentar el examen final.' if resultado else 'El alumno NO puede presentar el examen final.'}
"""
            self.result_label.config(text=resultado_text.strip())
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para asistencia y promedio.")
    
    def limpiar(self):
        self.asistencia.delete(0, 'end')
        self.promedio.delete(0, 'end')
        self.proyecto_var.set("no")
        self.result_label.config(text="")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        evaluar_consola()
    else:
        root = tk.Tk()
        app = EvaluacionAlumnoGUI(root)
        root.mainloop()