import customtkinter as ctk
from utils.formula_evaluator import FormulaEvaluator

# окно для создания пользовательской модели на основе формулы
class FormulaBuilderView(ctk.CTkToplevel):
    def __init__(self, master, available_metrics, on_model_add):
        super().__init__(master)
        self.title("Добавить пользовательскую модель")
        self.geometry("800x500")

        self.attributes("-topmost", True)  # окно всегда поверх
        self.focus_force()
        self.grab_set()  # блокирует основное окно, пока открыто это

        self.available_metrics = available_metrics
        self.evaluator = FormulaEvaluator(available_metrics)
        self.on_model_add = on_model_add
        self.valid_formula = False

        # левая панель с кнопками показателей и операций
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # правая часть - редактор формулы и ввод названия модели
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.create_metric_buttons()
        self.create_formula_editor()

    # создаёт кнопки показателей и операций, которые можно вставить в формулу
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

    # создаёт редактор формулы и поля для ввода названия модели
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
        self.save_button.pack(pady=20)
        self.save_button.configure(state="disabled")  # активируется только при успешной проверке

    # вставляет выбранный показатель или оператор в строку формулы
    def insert_into_formula(self, text):
        current = self.formula_entry.get()
        self.formula_entry.delete(0, "end")
        self.formula_entry.insert(0, current + text)

    # очищает поле формулы и сбрасывает состояние
    def clear_formula(self):
        self.formula_entry.delete(0, "end")
        self.error_label.configure(text="", text_color="red")
        self.valid_formula = False
        self.save_button.configure(state="disabled")

    # сбрасывает валидацию при любом изменении формулы вручную
    def on_formula_change(self):
        self.error_label.configure(text="", text_color="red")
        self.valid_formula = False
        self.save_button.configure(state="disabled")

    # проверка формулы
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
        else:
            self.error_label.configure(text=error_msg, text_color="red")
            self.valid_formula = False
            self.save_button.configure(state="disabled")

    # сохраняет модель если всё корректно
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
        self.destroy()
