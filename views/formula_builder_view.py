import customtkinter as ctk
from utils.formula_evaluator import FormulaEvaluator

# окно для создания пользовательской модели на основе формулы
class FormulaBuilderView(ctk.CTkToplevel):
    def __init__(self, master, available_metrics, on_model_add, controller):
        super().__init__(master)
        self.title("Добавить пользовательскую модель")
        self.geometry("800x500")

        self.attributes("-topmost", True)
        self.after(50, self.safe_focus)  # безопасный фокус
        self.grab_set()

        self.available_metrics = available_metrics
        self.evaluator = FormulaEvaluator(available_metrics)
        self.on_model_add = on_model_add
        self.controller = controller
        self.valid_formula = False

        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.create_metric_buttons()
        self.create_formula_editor()

    def safe_focus(self):
        if self.winfo_exists():
            self.focus_force()

    def create_metric_buttons(self):
        metric_section = ctk.CTkFrame(self.left_panel)
        metric_section.pack(side="left", fill="y", padx=(0, 10))

        label = ctk.CTkLabel(metric_section, text="Показатели")
        label.pack(pady=5)

        for metric in self.available_metrics:
            btn = ctk.CTkButton(metric_section, text=metric, width=140,
                                command=lambda m=metric: self.insert_into_formula(m))
            btn.pack(pady=2)

        op_section = ctk.CTkFrame(self.left_panel)
        op_section.pack(side="left", fill="y")

        op_label = ctk.CTkLabel(op_section, text="Операции")
        op_label.pack(pady=(5, 5))

        for op in ["+", "-", "*", "/", "(", ")"]:
            btn = ctk.CTkButton(op_section, text=op, width=50,
                                command=lambda o=op: self.insert_into_formula(o))
            btn.pack(pady=1)

    def create_formula_editor(self):
        self.formula_label = ctk.CTkLabel(self.editor_frame, text="Формула:")
        self.formula_label.pack(pady=(5, 0))

        self.formula_entry = ctk.CTkEntry(self.editor_frame, width=400)
        self.formula_entry.pack(pady=5)
        self.formula_entry.bind("<KeyRelease>", lambda event: self.on_formula_change())

        self.clear_button = ctk.CTkButton(self.editor_frame, text="Очистить", command=self.clear_formula)
        self.clear_button.pack(pady=(0, 10))

        self.name_label = ctk.CTkLabel(self.editor_frame, text="Название модели:")
        self.name_label.pack(pady=(10, 0))

        self.name_entry = ctk.CTkEntry(self.editor_frame, width=400)
        self.name_entry.pack(pady=5)

        self.check_button = ctk.CTkButton(self.editor_frame, text="Проверить формулу", command=self.check_formula)
        self.check_button.pack(pady=(5, 10))

        self.error_label = ctk.CTkLabel(self.editor_frame, text="", text_color="red")
        self.error_label.pack(pady=5)

        self.save_button = ctk.CTkButton(self.editor_frame, text="Добавить модель", command=self.save_model)
        self.save_button.pack(pady=(10, 5))
        self.save_button.configure(state="disabled")

        self.save_to_db_button = ctk.CTkButton(self.editor_frame, text="Сохранить в БД", command=self.save_model_to_db)
        self.save_to_db_button.pack(pady=(0, 10))
        self.save_to_db_button.configure(state="disabled")

    def insert_into_formula(self, text):
        safe_text = text.replace(" ", "_").replace("-", "_")
        current = self.formula_entry.get()
        self.formula_entry.delete(0, "end")
        self.formula_entry.insert(0, current + safe_text)

    def clear_formula(self):
        self.formula_entry.delete(0, "end")
        self.error_label.configure(text="", text_color="red")
        self.valid_formula = False
        self.save_button.configure(state="disabled")
        self.save_to_db_button.configure(state="disabled")

    def on_formula_change(self):
        self.error_label.configure(text="", text_color="red")
        self.valid_formula = False
        self.save_button.configure(state="disabled")
        self.save_to_db_button.configure(state="disabled")

    def check_formula(self):
        formula = self.formula_entry.get()
        if not formula:
            self.error_label.configure(text="Введите формулу для проверки", text_color="red")
            return

        is_valid, error_msg = self.evaluator.validate(formula)
        if is_valid:
            self.error_label.configure(text="Формула корректна ✅", text_color="green")
            self.valid_formula = True
            self.save_button.configure(state="normal")
            self.save_to_db_button.configure(state="normal")
        else:
            self.error_label.configure(text=error_msg, text_color="red")
            self.valid_formula = False
            self.save_button.configure(state="disabled")
            self.save_to_db_button.configure(state="disabled")

    def save_model(self):
        formula = self.formula_entry.get()
        name = self.name_entry.get()

        if not name or not formula:
            self.error_label.configure(text="Введите название и формулу", text_color="red")
            return

        if not self.valid_formula:
            self.error_label.configure(text="Сначала проверьте формулу", text_color="red")
            return

        self.on_model_add(name.strip(), formula.strip())
        if self.winfo_exists():
            self.destroy()

    def save_model_to_db(self):
        formula = self.formula_entry.get()
        name = self.name_entry.get()

        if not name or not formula:
            self.error_label.configure(text="Введите название и формулу", text_color="red")
            return

        if not self.valid_formula:
            self.error_label.configure(text="Сначала проверьте формулу", text_color="red")
            return

        self.on_model_add(name.strip(), formula.strip())

        try:
            self.controller.save_user_model_to_db(name.strip(), formula.strip())
            self.error_label.configure(text=f"Модель '{name}' сохранена ✅", text_color="green")
        except Exception as e:
            self.error_label.configure(text=f"Ошибка при сохранении: {e}", text_color="red")
