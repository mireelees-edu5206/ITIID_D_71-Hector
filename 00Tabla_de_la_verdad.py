import tkinter as tk
from tkinter import ttk

def tabla_verdad_consola():
    print("=" * 75)
    print("              TABLA DE VERDAD - OPERADORES LÓGICOS")
    print("=" * 75)

    print(f"{'p':<6} {'q':<6} {'¬p':<6} {'p ∧ q':<8} {'p ∨ q':<8} {'p → q':<8} {'p ↔ q':<8}")
    print("-" * 75)

    for p in [True, False]:
        for q in [True, False]:
            negacion = not p
            conjuncion = p and q
            disyuncion = p or q
            condicional = (not p) or q
            bicondicional = p == q

            print(f"{str(p):<6} {str(q):<6} {str(negacion):<6} {str(conjuncion):<8} {str(disyuncion):<8} {str(condicional):<8} {str(bicondicional):<8}")

    print("=" * 75)

class TablaVerdadGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabla de Verdad - Operadores Lógicos")
        self.root.geometry("700x300")
        self.root.configure(bg="#f0f0f0")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('TFrame', background="#f0f0f0")
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background="#2c3e50", foreground="white")
        style.configure('Treeview', font=('Courier New', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
        header_frame = ttk.Frame(root)
        header_frame.pack(fill='x', pady=10)
        header_label = ttk.Label(header_frame, text="TABLA DE VERDAD - OPERADORES LÓGICOS", style='Header.TLabel')
        header_label.pack(fill='x', padx=10, pady=10)
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        columns = ('p', 'q', 'not_p', 'p_and_q', 'p_or_q', 'p_implies_q', 'p_iff_q')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        self.tree.heading('p', text='p')
        self.tree.heading('q', text='q')
        self.tree.heading('not_p', text='¬p')
        self.tree.heading('p_and_q', text='p ∧ q')
        self.tree.heading('p_or_q', text='p ∨ q')
        self.tree.heading('p_implies_q', text='p → q')
        self.tree.heading('p_iff_q', text='p ↔ q')
        
        self.tree.column('p', width=60, anchor='center')
        self.tree.column('q', width=60, anchor='center')
        self.tree.column('not_p', width=60, anchor='center')
        self.tree.column('p_and_q', width=80, anchor='center')
        self.tree.column('p_or_q', width=80, anchor='center')
        self.tree.column('p_implies_q', width=80, anchor='center')
        self.tree.column('p_iff_q', width=80, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.generar_tabla()
        
        regenerar_btn = ttk.Button(root, text="Regenerar Tabla", command=self.generar_tabla)
        regenerar_btn.pack(pady=10)
    
    def generar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for p in [True, False]:
            for q in [True, False]:
                negacion = not p
                conjuncion = p and q
                disyuncion = p or q
                condicional = (not p) or q
                bicondicional = p == q
                
                self.tree.insert('', 'end', values=(
                    str(p),
                    str(q),
                    str(negacion),
                    str(conjuncion),
                    str(disyuncion),
                    str(condicional),
                    str(bicondicional)
                ))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        tabla_verdad_consola()
    else:
        root = tk.Tk()
        app = TablaVerdadGUI(root)
        root.mainloop()

