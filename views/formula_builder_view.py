import customtkinter as ctk

class FormulaBuilderView(ctk.CTkToplevel):
    def __init__(self, master, available_metrics, on_model_add):
        super().__init__(master)
        self.title("Добавить пользовательскую модель")
        self.geometry("800x500")

        self.available_metrics = available_metrics
        self.on_model_add = on_model_add

        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.create_metric_buttons()
        self.create_formula_editor()

    def create_metric_buttons(self):
        metric_section = ctk.CTkFrame(self.left_panel)
        metric_section.pack(side="left", fill="y", padx=(0, 10))

        label = ctk.CTkLabel(metric_section, text="Показатели")
        label.pack(pady=5)

        for metric in self.available_metrics:
            btn = ctk.CTkButton(metric_section, text=metric, width=140, command=lambda m=metric: self.insert_into_formula(m))
            btn.pack(pady=2)

        op_section = ctk.CTkFrame(self.left_panel)
        op_section.pack(side="left", fill="y")

        op_label = ctk.CTkLabel(op_section, text="Операции")
        op_label.pack(pady=(5, 5))

        for op in ["+", "-", "*", "/", "(", ")"]:
            btn = ctk.CTkButton(op_section, text=op, width=50, command=lambda o=op: self.insert_into_formula(o))
            btn.pack(pady=1)

    def create_formula_editor(self):
        self.formula_label = ctk.CTkLabel(self.editor_frame, text="Формула:")
        self.formula_label.pack(pady=(5, 0))

        self.formula_entry = ctk.CTkEntry(self.editor_frame, width=400)
        self.formula_entry.pack(pady=5)

        self.clear_button = ctk.CTkButton(self.editor_frame, text="Очистить", command=self.clear_formula)
        self.clear_button.pack(pady=(0, 10))

        self.name_label = ctk.CTkLabel(self.editor_frame, text="Название модели:")
        self.name_label.pack(pady=(10, 0))

        self.name_entry = ctk.CTkEntry(self.editor_frame, width=400)
        self.name_entry.pack(pady=5)

        self.error_label = ctk.CTkLabel(self.editor_frame, text="", text_color="red")
        self.error_label.pack(pady=5)

        self.save_button = ctk.CTkButton(self.editor_frame, text="Добавить модель", command=self.save_model)
        self.save_button.pack(pady=20)

    def insert_into_formula(self, text):
        current = self.formula_entry.get()
        self.formula_entry.delete(0, "end")
        self.formula_entry.insert(0, current + text)

    def clear_formula(self):
        self.formula_entry.delete(0, "end")

    def save_model(self):
        formula = self.formula_entry.get()
        name = self.name_entry.get()
        if name and formula:
            self.on_model_add(name.strip(), formula.strip())
            self.destroy()
        else:
            self.error_label.configure(text="Введите название и формулу")
